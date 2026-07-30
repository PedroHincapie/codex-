from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from src.radar_store import (
  DATA_DIR,
  DAILY_FILE_PREFIX,
  RANKING_FILE_PREFIX,
  get_source_type,
  read_json,
  validate_daily_snapshot
)


TABLE_ORDER = (
  "radar_snapshots",
  "signals",
  "rankings",
  "ranking_entries",
  "source_candidate_batches",
  "source_candidates"
)
CANDIDATE_FILE_PREFIX = "source-candidates-"
UPSERT_KEYS = {
  "radar_snapshots": "radar_date",
  "signals": "id",
  "rankings": "radar_date",
  "ranking_entries": "ranking_date,signal_id",
  "source_candidate_batches": "source_file",
  "source_candidates": "batch_file,source_id"
}


def build_persistence_bundle(data_dir: Path | str = DATA_DIR) -> dict[str, list[dict[str, Any]]]:
  root = Path(data_dir)
  bundle = {table: [] for table in TABLE_ORDER}

  for path in sorted((root / "signals" / "daily").glob(f"{DAILY_FILE_PREFIX}*.json")):
    snapshot = read_json(path)
    errors = validate_daily_snapshot(snapshot)
    if errors:
      raise ValueError(f"{path.name}: {'; '.join(errors)}")

    radar_date = snapshot["radarDate"]
    bundle["radar_snapshots"].append({
      "radar_date": radar_date,
      "contract_version": snapshot["contractVersion"],
      "generated_at": snapshot["generatedAt"],
      "topic": snapshot["topic"],
      "locale": snapshot["locale"],
      "source_file": path.name
    })

    for signal in snapshot["signals"]:
      source = signal["source"]
      impact = signal["impact"]
      bundle["signals"].append({
        "id": signal["id"],
        "radar_date": radar_date,
        "title": signal["title"],
        "source_name": source["name"],
        "source_url": source["url"],
        "published_at": source["publishedAt"],
        "retrieved_at": source["retrievedAt"],
        "source_type": get_source_type(signal),
        "evidence": signal["evidence"],
        "impact_level": impact["level"],
        "impact_summary": impact["summary"],
        "action": signal["action"],
        "status": signal["status"],
        "tags": signal["tags"]
      })

  signal_ids = {row["id"] for row in bundle["signals"]}
  for path in sorted((root / "reviews" / "rankings").glob(f"{RANKING_FILE_PREFIX}*.json")):
    ranking = read_json(path)
    radar_date = ranking["radarDate"]
    bundle["rankings"].append({
      "radar_date": radar_date,
      "generated_at": ranking["generatedAt"],
      "reviewed_snapshot": ranking["reviewedSnapshot"],
      "scoring_version": ranking["scoringVersion"],
      "weights": ranking["weights"],
      "audit": ranking["audit"],
      "source_file": path.name
    })

    for entry in ranking["rankedSignals"]:
      if entry["signalId"] not in signal_ids:
        raise ValueError(f"{path.name}: unknown signalId {entry['signalId']}")
      bundle["ranking_entries"].append({
        "ranking_date": radar_date,
        "signal_id": entry["signalId"],
        "rank": entry["rank"],
        "score": entry["score"],
        "dimensions": entry["dimensions"],
        "reason": entry["reason"]
      })

  candidate_dir = root / "sources" / "candidates"
  for path in sorted(candidate_dir.glob(f"{CANDIDATE_FILE_PREFIX}*.json")):
    batch = read_json(path)
    window = batch.get("window") or {}
    bundle["source_candidate_batches"].append({
      "source_file": path.name,
      "generated_at": batch["generatedAt"],
      "retrieved_from": batch["retrievedFrom"],
      "topic": batch["topic"],
      "locale": batch["locale"],
      "window_from": window.get("from"),
      "window_to": window.get("to")
    })

    for candidate in batch["candidates"]:
      bundle["source_candidates"].append({
        "batch_file": path.name,
        "source_id": candidate["sourceId"],
        "canonical_url": candidate["canonicalUrl"],
        "source_name": candidate["sourceName"],
        "source_type": candidate["sourceType"],
        "title": candidate["title"],
        "published_at": candidate["publishedAt"],
        "retrieved_at": candidate["retrievedAt"],
        "actors": candidate.get("actors", []),
        "topics": candidate.get("topics", []),
        "raw_input": candidate.get("rawInput", ""),
        "facts": candidate["facts"],
        "inferences": candidate.get("inferences", []),
        "confidence": candidate["confidence"]
      })

  errors = validate_persistence_bundle(bundle)
  if errors:
    raise ValueError("; ".join(errors))
  return bundle


def persistence_manifest(bundle: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
  return {
    "tables": [
      {"table": table, "rows": len(bundle[table])}
      for table in TABLE_ORDER
    ],
    "totalRows": sum(len(bundle[table]) for table in TABLE_ORDER)
  }


def upsert_persistence_bundle(
  bundle: dict[str, list[dict[str, Any]]],
  supabase_url: str,
  secret_key: str,
  batch_size: int = 100
) -> dict[str, Any]:
  if not supabase_url.startswith(("http://", "https://")):
    raise ValueError("SUPABASE_URL must start with http:// or https://")
  if not secret_key:
    raise ValueError("SUPABASE_SECRET_KEY or SUPABASE_SERVICE_ROLE_KEY is required")
  if batch_size < 1:
    raise ValueError("batch_size must be greater than zero")

  applied = []
  for table in TABLE_ORDER:
    rows = bundle[table]
    for offset in range(0, len(rows), batch_size):
      batch = rows[offset:offset + batch_size]
      _postgrest_upsert(
        supabase_url=supabase_url,
        secret_key=secret_key,
        table=table,
        conflict_columns=UPSERT_KEYS[table],
        rows=batch
      )
    applied.append({"table": table, "rows": len(rows)})

  return {
    "tables": applied,
    "totalRows": sum(item["rows"] for item in applied)
  }


def validate_persistence_bundle(bundle: dict[str, list[dict[str, Any]]]) -> list[str]:
  errors = []
  snapshot_dates = {row["radar_date"] for row in bundle["radar_snapshots"]}
  signal_ids = {row["id"] for row in bundle["signals"]}
  ranking_dates = {row["radar_date"] for row in bundle["rankings"]}
  batch_files = {row["source_file"] for row in bundle["source_candidate_batches"]}

  errors.extend(_duplicate_key_errors(bundle["radar_snapshots"], ("radar_date",)))
  errors.extend(_duplicate_key_errors(bundle["signals"], ("id",)))
  errors.extend(_duplicate_key_errors(bundle["rankings"], ("radar_date",)))
  errors.extend(_duplicate_key_errors(bundle["ranking_entries"], ("ranking_date", "signal_id")))
  errors.extend(_duplicate_key_errors(bundle["ranking_entries"], ("ranking_date", "rank")))
  errors.extend(_duplicate_key_errors(bundle["source_candidate_batches"], ("source_file",)))
  errors.extend(_duplicate_key_errors(bundle["source_candidates"], ("batch_file", "source_id")))

  for row in bundle["signals"]:
    if row["radar_date"] not in snapshot_dates:
      errors.append(f"signals:{row['id']} references missing snapshot {row['radar_date']}")
  for row in bundle["ranking_entries"]:
    if row["ranking_date"] not in ranking_dates:
      errors.append(f"ranking_entries references missing ranking {row['ranking_date']}")
    if row["signal_id"] not in signal_ids:
      errors.append(f"ranking_entries references missing signal {row['signal_id']}")
  for row in bundle["source_candidates"]:
    if row["batch_file"] not in batch_files:
      errors.append(f"source_candidates references missing batch {row['batch_file']}")

  return errors


def _duplicate_key_errors(
  rows: list[dict[str, Any]],
  fields: tuple[str, ...]
) -> list[str]:
  seen = set()
  errors = []
  for row in rows:
    key = tuple(row[field] for field in fields)
    if key in seen:
      errors.append(f"duplicate key {','.join(fields)}={key}")
    seen.add(key)
  return errors


def _postgrest_upsert(
  supabase_url: str,
  secret_key: str,
  table: str,
  conflict_columns: str,
  rows: list[dict[str, Any]]
) -> None:
  import json

  endpoint = (
    f"{supabase_url.rstrip('/')}/rest/v1/{quote(table)}"
    f"?on_conflict={quote(conflict_columns, safe=',')}"
  )
  headers = {
    "apikey": secret_key,
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=minimal",
    "User-Agent": "ai-radar-persistence/1.0"
  }
  if not secret_key.startswith("sb_"):
    headers["Authorization"] = f"Bearer {secret_key}"

  request = Request(
    endpoint,
    data=json.dumps(rows, ensure_ascii=False).encode("utf-8"),
    headers=headers,
    method="POST"
  )
  try:
    with urlopen(request, timeout=30) as response:
      if response.status not in (200, 201, 204):
        raise RuntimeError(f"{table}: unexpected HTTP status {response.status}")
  except HTTPError as error:
    detail = error.read().decode("utf-8", errors="replace")
    raise RuntimeError(f"{table}: HTTP {error.code}: {detail}") from error
