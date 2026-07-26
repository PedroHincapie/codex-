from __future__ import annotations

import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any


DATA_DIR = Path.cwd() / "data"
DAILY_SIGNAL_DIR = DATA_DIR / "signals" / "daily"
REVIEW_RANKING_DIR = DATA_DIR / "reviews" / "rankings"
DAILY_FILE_PREFIX = "daily-radar-"
RANKING_FILE_PREFIX = "signal-review-ranking-"
DEFAULT_LIST_FIELDS = ["id", "publishedAt", "source", "impact", "status", "title"]
SOURCE_TYPES = ["news", "official", "paper", "repo", "product", "social"]


def load_daily_signals(data_dir: Path | str = DATA_DIR) -> list[dict[str, Any]]:
  root = _daily_signal_dir(Path(data_dir))
  signals: list[dict[str, Any]] = []

  for path in sorted(root.glob(f"{DAILY_FILE_PREFIX}[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json")):
    snapshot = read_json(path)
    for signal in snapshot.get("signals", []):
      signals.append({
        **signal,
        "radarDate": snapshot.get("radarDate", ""),
        "snapshotFile": path.name,
        "snapshotPath": str(path)
      })

  return signals


def load_ranking(date: str | None = None, data_dir: Path | str = DATA_DIR) -> dict[str, Any] | None:
  root = _review_ranking_dir(Path(data_dir))
  paths = sorted(root.glob(f"{RANKING_FILE_PREFIX}[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json"))
  if date:
    paths = [path for path in paths if date in path.name]

  if not paths:
    return None

  latest = paths[-1]
  return {
    "file": latest.name,
    "fullPath": str(latest),
    "ranking": read_json(latest)
  }


def load_daily_snapshot(date: str, data_dir: Path | str = DATA_DIR) -> dict[str, Any] | None:
  path = _daily_signal_dir(Path(data_dir)) / f"{DAILY_FILE_PREFIX}{date}.json"
  if not path.exists():
    return None
  return {
    "file": path.name,
    "fullPath": str(path),
    "snapshot": read_json(path)
  }


def list_daily_snapshot_dates(data_dir: Path | str = DATA_DIR) -> list[str]:
  root = _daily_signal_dir(Path(data_dir))
  dates = []

  for path in sorted(root.glob(f"{DAILY_FILE_PREFIX}[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json")):
    snapshot_date = path.stem.removeprefix(DAILY_FILE_PREFIX)
    _parse_date(snapshot_date)
    dates.append(snapshot_date)

  return dates


def report_snapshot_coverage(
  from_date: str | None = None,
  to_date: str | None = None,
  data_dir: Path | str = DATA_DIR
) -> dict[str, Any]:
  observed_dates = list_daily_snapshot_dates(data_dir)
  observed_from = observed_dates[0] if observed_dates else ""
  observed_to = observed_dates[-1] if observed_dates else ""

  coverage_from = from_date or observed_from
  coverage_to = to_date or observed_to

  if coverage_from:
    _parse_date(coverage_from)
  if coverage_to:
    _parse_date(coverage_to)
  if coverage_from and coverage_to and coverage_from > coverage_to:
    raise ValueError("from_date must be before or equal to to_date")

  expected_dates = list(_date_range(coverage_from, coverage_to)) if coverage_from and coverage_to else []
  snapshots_in_range = [item for item in observed_dates if _date_in_range(item, coverage_from, coverage_to)]
  missing_dates = [item for item in expected_dates if item not in set(snapshots_in_range)]

  return {
    "observedRange": {
      "from": observed_from,
      "to": observed_to
    },
    "coverageRange": {
      "from": coverage_from,
      "to": coverage_to
    },
    "snapshotDates": snapshots_in_range,
    "missingDates": missing_dates,
    "counts": {
      "observedSnapshots": len(observed_dates),
      "expectedDays": len(expected_dates),
      "daysWithSnapshot": len(snapshots_in_range),
      "missingDays": len(missing_dates)
    }
  }


def filter_signals(signals: list[dict[str, Any]], filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
  filters = filters or {}

  return [
    signal
    for signal in signals
    if _matches_filters(signal, filters)
  ]


def summarize_signals(signals: list[dict[str, Any]]) -> dict[str, Any]:
  return {
    "count": len(signals),
    "byRadarDate": _count_by(signals, lambda signal: signal["radarDate"]),
    "byImpact": _count_by(signals, lambda signal: signal["impact"]["level"]),
    "byStatus": _count_by(signals, lambda signal: signal["status"]),
    "bySource": _count_by(signals, lambda signal: signal["source"]["name"]),
    "topTags": [
      {"tag": tag, "count": count}
      for tag, count in sorted(
        Counter(tag for signal in signals for tag in signal.get("tags", [])).items(),
        key=lambda item: (-item[1], item[0])
      )[:10]
    ]
  }


def audit_signals(signals: list[dict[str, Any]]) -> dict[str, Any]:
  return {
    "totalSignals": len(signals),
    "statusCounts": _count_by(signals, lambda signal: signal.get("status", "")),
    "emptyEvidence": find_empty_evidence(signals),
    "duplicateGroups": find_duplicate_groups(signals),
    "primarySources": list_primary_sources(signals)
  }


def find_empty_evidence(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
  return [
    _signal_reference(signal)
    for signal in signals
    if not _has_evidence(signal)
  ]


def find_duplicate_groups(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
  candidates = {
    "id": {},
    "url": {},
    "title": {}
  }

  for signal in signals:
    values = {
      "id": signal.get("id", ""),
      "url": signal.get("source", {}).get("url", ""),
      "title": _normalize(signal.get("title", ""))
    }

    for field, value in values.items():
      if not value:
        continue
      candidates[field].setdefault(value, []).append(signal)

  duplicate_groups = []
  for field, groups in candidates.items():
    for value, items in sorted(groups.items()):
      if len(items) > 1:
        duplicate_groups.append({
          "field": field,
          "value": value,
          "signals": [_signal_reference(signal) for signal in items]
        })

  return duplicate_groups


def list_primary_sources(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
  sources: dict[str, dict[str, Any]] = {}

  for signal in signals:
    source = signal.get("source", {})
    name = source.get("name", "")
    if not name:
      continue

    item = sources.setdefault(name, {
      "source": name,
      "count": 0,
      "urls": set()
    })
    item["count"] += 1
    if source.get("url"):
      item["urls"].add(source["url"])

  return [
    {
      "source": item["source"],
      "count": item["count"],
      "urls": sorted(item["urls"])
    }
    for item in sorted(sources.values(), key=lambda item: (-item["count"], item["source"]))
  ]


def pick_fields(signal: dict[str, Any], fields: list[str]) -> dict[str, Any]:
  return {field: get_field(signal, field) for field in fields}


def join_ranking_with_signals(ranking: dict[str, Any], signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
  signal_by_id = {signal["id"]: signal for signal in signals}
  rows = []

  for ranked in ranking.get("rankedSignals", []):
    signal = signal_by_id.get(ranked.get("signalId"))
    rows.append({
      **ranked,
      "title": signal.get("title", "") if signal else "",
      "impact": signal.get("impact", {}).get("level", "") if signal else "",
      "status": signal.get("status", "") if signal else "",
      "source": signal.get("source", {}).get("name", "") if signal else "",
      "publishedAt": signal.get("source", {}).get("publishedAt", "") if signal else ""
    })

  return rows


def validate_daily_snapshot(snapshot: dict[str, Any]) -> list[str]:
  errors: list[str] = []
  required_root = ["contractVersion", "radarDate", "generatedAt", "topic", "locale", "signals"]

  for field in required_root:
    if field not in snapshot:
      errors.append(f"missing root field: {field}")

  if not isinstance(snapshot.get("signals"), list) or not snapshot.get("signals"):
    errors.append("signals must be a non-empty list")
    return errors

  radar_date = snapshot.get("radarDate")
  seen_ids = set()
  for index, signal in enumerate(snapshot["signals"]):
    prefix = f"signals[{index}]"
    for field in ["id", "title", "source", "evidence", "impact", "action", "status", "tags"]:
      if field not in signal:
        errors.append(f"{prefix} missing field: {field}")

    signal_id = signal.get("id", "")
    if signal_id in seen_ids:
      errors.append(f"{prefix} duplicate id: {signal_id}")
    seen_ids.add(signal_id)

    if radar_date and not signal_id.startswith(f"{radar_date}-"):
      errors.append(f"{prefix} id does not start with radarDate: {signal_id}")

    if not isinstance(signal.get("evidence"), list) or not signal.get("evidence"):
      errors.append(f"{prefix} evidence must be a non-empty list")

    if not isinstance(signal.get("tags"), list) or not signal.get("tags"):
      errors.append(f"{prefix} tags must be a non-empty list")

  return errors


def read_json(path: Path) -> Any:
  with path.open(encoding="utf-8") as file:
    return json.load(file)


def get_field(signal: dict[str, Any], field: str) -> Any:
  field_map = {
    "id": signal.get("id", ""),
    "title": signal.get("title", ""),
    "radarDate": signal.get("radarDate", ""),
    "publishedAt": signal.get("source", {}).get("publishedAt", ""),
    "retrievedAt": signal.get("source", {}).get("retrievedAt", ""),
    "source": signal.get("source", {}).get("name", ""),
    "sourceType": get_source_type(signal),
    "impact": signal.get("impact", {}).get("level", ""),
    "status": signal.get("status", ""),
    "tags": ",".join(signal.get("tags", [])),
    "action": signal.get("action", ""),
    "url": signal.get("source", {}).get("url", ""),
    "snapshot": signal.get("snapshotFile", "")
  }
  return field_map.get(field, "")


def _matches_filters(signal: dict[str, Any], filters: dict[str, Any]) -> bool:
  source = signal.get("source", {})
  impact = signal.get("impact", {})

  if filters.get("date") and signal.get("radarDate") != filters["date"]:
    return False

  if filters.get("from_date") and source.get("publishedAt", "") < filters["from_date"]:
    return False

  if filters.get("to_date") and source.get("publishedAt", "") > filters["to_date"]:
    return False

  if filters.get("tag") and filters["tag"] not in signal.get("tags", []):
    return False

  if filters.get("impact") and impact.get("level") != filters["impact"]:
    return False

  if filters.get("status") and signal.get("status") != filters["status"]:
    return False

  if filters.get("source") and _normalize(filters["source"]) not in _normalize(source.get("name", "")):
    return False

  if filters.get("source_type") and get_source_type(signal) != _normalize(filters["source_type"]):
    return False

  if filters.get("q") and not _matches_query(signal, filters["q"]):
    return False

  return True


def get_source_type(signal: dict[str, Any]) -> str:
  explicit_type = _normalize(signal.get("sourceType", ""))
  if explicit_type:
    return explicit_type
  return infer_source_type(signal.get("source", {}))


def infer_source_type(source: dict[str, Any]) -> str:
  name = _normalize(source.get("name", ""))
  url = _normalize(source.get("url", ""))

  if "github" in name or "github.com" in url or "gitlab" in name or "gitlab.com" in url:
    return "repo"
  if "arxiv" in name or "arxiv.org" in url or "doi.org" in url:
    return "paper"
  if "releases" in name or "/releases" in url or "changelog" in name:
    return "product"
  if any(marker in name for marker in ["reddit", "hacker news", "x.com", "twitter"]):
    return "social"
  if any(marker in name for marker in ["openai", "anthropic", "nist", "google", "microsoft", "meta"]):
    return "official"
  return "news"


def _matches_query(signal: dict[str, Any], query: str) -> bool:
  haystack = " ".join([
    signal.get("id", ""),
    signal.get("title", ""),
    signal.get("source", {}).get("name", ""),
    get_source_type(signal),
    signal.get("impact", {}).get("summary", ""),
    signal.get("action", ""),
    signal.get("status", ""),
    *signal.get("tags", []),
    *signal.get("evidence", [])
  ])
  return _normalize(query) in _normalize(haystack)


def _has_evidence(signal: dict[str, Any]) -> bool:
  evidence = signal.get("evidence")
  if not isinstance(evidence, list):
    return False
  return any(str(item).strip() for item in evidence)


def _signal_reference(signal: dict[str, Any]) -> dict[str, str]:
  return {
    "id": signal.get("id", ""),
    "radarDate": signal.get("radarDate", ""),
    "title": signal.get("title", ""),
    "source": signal.get("source", {}).get("name", ""),
    "url": signal.get("source", {}).get("url", ""),
    "snapshot": signal.get("snapshotFile", "")
  }


def _normalize(value: Any) -> str:
  return str(value).strip().lower()


def _count_by(items: list[dict[str, Any]], selector) -> dict[str, int]:
  return dict(Counter(selector(item) for item in items))


def _date_range(from_date: str, to_date: str):
  current = _parse_date(from_date)
  end = _parse_date(to_date)

  while current <= end:
    yield current.isoformat()
    current += timedelta(days=1)


def _date_in_range(value: str, from_date: str, to_date: str) -> bool:
  return (not from_date or value >= from_date) and (not to_date or value <= to_date)


def _parse_date(value: str) -> date:
  try:
    return date.fromisoformat(value)
  except ValueError as error:
    raise ValueError(f"invalid date: {value}") from error


def _daily_signal_dir(data_dir: Path) -> Path:
  if data_dir.name == "daily":
    return data_dir
  if data_dir.name == "fixtures":
    return data_dir
  return data_dir / "signals" / "daily"


def _review_ranking_dir(data_dir: Path) -> Path:
  if data_dir.name == "rankings":
    return data_dir
  if data_dir.name == "fixtures":
    return data_dir
  return data_dir / "reviews" / "rankings"
