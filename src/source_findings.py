from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


REPORT_VERSION = 1
FINDING_KINDS = {"fetch_failure", "content_unavailable", "candidate_rejection"}
REJECTION_REASONS = {"missing-verifiable-published-at"}


def build_fetch_failure(
  *,
  source_name: str,
  url: str,
  retrieved_at: str,
  group: str,
  http_status: int,
  strategy: str = "canonical-url",
  message: str = ""
) -> dict[str, Any]:
  _validate_common(source_name, url, retrieved_at)
  if not group.strip():
    raise ValueError("group is required")
  if http_status < 100 or http_status > 599:
    raise ValueError("http_status must be between 100 and 599")

  outcome = "blocked" if http_status in {401, 403, 429} else "degraded"
  reason_code = f"http-{http_status}"
  return {
    "id": _finding_id(retrieved_at, source_name, reason_code),
    "kind": "fetch_failure",
    "observedAt": retrieved_at,
    "source": {
      "name": source_name.strip(),
      "url": url,
      "group": group.strip()
    },
    "outcome": outcome,
    "reasonCode": reason_code,
    "httpStatus": http_status,
    "message": message.strip() or f"La fuente respondio HTTP {http_status}.",
    "strategy": strategy.strip() or "canonical-url",
    "collectionAction": "continue-other-sources",
    "sourceHealthAction": "record-only",
    "alternativePolicy": "configured-only"
  }


def build_candidate_rejection(
  *,
  source_name: str,
  url: str,
  retrieved_at: str,
  reason_code: str = "missing-verifiable-published-at",
  raw_input: str = ""
) -> dict[str, Any]:
  _validate_common(source_name, url, retrieved_at)
  if reason_code not in REJECTION_REASONS:
    raise ValueError(f"unsupported rejection reason: {reason_code}")

  return {
    "id": _finding_id(retrieved_at, source_name, reason_code),
    "kind": "candidate_rejection",
    "observedAt": retrieved_at,
    "source": {
      "name": source_name.strip(),
      "url": url
    },
    "outcome": "rejected",
    "reasonCode": reason_code,
    "missingFields": ["publishedAt"],
    "candidate": {
      "canonicalUrl": url,
      "sourceName": source_name.strip(),
      "retrievedAt": retrieved_at,
      "rawInput": raw_input.strip() or url
    },
    "collectionAction": "exclude-candidate",
    "datePolicy": "verified-evidence-only"
  }


def build_content_unavailable(
  *,
  source_name: str,
  url: str,
  retrieved_at: str,
  group: str,
  message: str = ""
) -> dict[str, Any]:
  _validate_common(source_name, url, retrieved_at)
  if not group.strip():
    raise ValueError("group is required")
  return {
    "id": _finding_id(retrieved_at, source_name, "no-recent-content"),
    "kind": "content_unavailable",
    "observedAt": retrieved_at,
    "source": {
      "name": source_name.strip(),
      "url": url,
      "group": group.strip()
    },
    "outcome": "no_content",
    "reasonCode": "no-recent-content",
    "message": message.strip() or "No se identifico contenido reciente verificable.",
    "collectionAction": "continue-other-sources",
    "sourceHealthAction": "record-only"
  }


def build_report(report_date: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
  _validate_date(report_date)
  errors = []
  for index, finding in enumerate(findings):
    errors.extend(f"findings[{index}]: {error}" for error in validate_finding(finding))
  if errors:
    raise ValueError("; ".join(errors))

  unique_findings = {finding["id"]: finding for finding in findings}
  ordered = [unique_findings[key] for key in sorted(unique_findings)]
  reason_counts: dict[str, int] = {}
  for finding in ordered:
    reason = finding["reasonCode"]
    reason_counts[reason] = reason_counts.get(reason, 0) + 1

  return {
    "version": REPORT_VERSION,
    "reportDate": report_date,
    "generatedAt": f"{report_date}T00:00:00Z",
    "summary": {
      "total": len(ordered),
      "fetchFailures": sum(item["kind"] == "fetch_failure" for item in ordered),
      "contentUnavailable": sum(item["kind"] == "content_unavailable" for item in ordered),
      "candidateRejections": sum(item["kind"] == "candidate_rejection" for item in ordered),
      "reasonCounts": reason_counts
    },
    "findings": ordered
  }


def merge_report(existing: dict[str, Any] | None, finding: dict[str, Any]) -> dict[str, Any]:
  errors = validate_finding(finding)
  if errors:
    raise ValueError("; ".join(errors))
  report_date = finding["observedAt"]
  findings = []
  if existing:
    if existing.get("reportDate") != report_date:
      raise ValueError("existing reportDate does not match finding observedAt")
    findings.extend(existing.get("findings", []))
  findings.append(finding)
  return build_report(report_date, findings)


def write_report(path: Path | str, finding: dict[str, Any]) -> dict[str, Any]:
  output_path = Path(path)
  existing = None
  if output_path.exists():
    existing = json.loads(output_path.read_text(encoding="utf-8"))
  report = merge_report(existing, finding)
  output_path.parent.mkdir(parents=True, exist_ok=True)
  output_path.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
  )
  return report


def validate_finding(finding: dict[str, Any]) -> list[str]:
  errors = []
  if finding.get("kind") not in FINDING_KINDS:
    errors.append("kind is invalid")
  if not finding.get("id"):
    errors.append("id is required")
  try:
    _validate_date(finding.get("observedAt", ""))
  except ValueError as error:
    errors.append(str(error))

  source = finding.get("source") or {}
  if not source.get("name"):
    errors.append("source.name is required")
  if not _valid_url(source.get("url", "")):
    errors.append("source.url must be http or https")

  if finding.get("kind") == "fetch_failure":
    if not isinstance(finding.get("httpStatus"), int):
      errors.append("httpStatus must be an integer")
    if finding.get("collectionAction") != "continue-other-sources":
      errors.append("fetch failures must continue other sources")
    if finding.get("sourceHealthAction") != "record-only":
      errors.append("isolated fetch failures must not mutate source health")
  if finding.get("kind") == "content_unavailable":
    if finding.get("outcome") != "no_content":
      errors.append("content_unavailable outcome must be no_content")
    if finding.get("collectionAction") != "continue-other-sources":
      errors.append("content_unavailable must continue other sources")
  if finding.get("kind") == "candidate_rejection":
    if finding.get("reasonCode") not in REJECTION_REASONS:
      errors.append("candidate rejection reasonCode is invalid")
    if "publishedAt" not in finding.get("missingFields", []):
      errors.append("candidate rejection must identify missing publishedAt")
    if "publishedAt" in (finding.get("candidate") or {}):
      errors.append("candidate rejection must not invent publishedAt")
  return errors


def _finding_id(observed_at: str, source_name: str, reason_code: str) -> str:
  slug = re.sub(r"[^a-z0-9]+", "-", source_name.lower()).strip("-")
  return f"{observed_at}-{slug}-{reason_code}"


def _validate_common(source_name: str, url: str, retrieved_at: str) -> None:
  if not source_name.strip():
    raise ValueError("source_name is required")
  if not _valid_url(url):
    raise ValueError("url must start with http or https")
  _validate_date(retrieved_at)


def _validate_date(value: str) -> None:
  try:
    date.fromisoformat(value)
  except (TypeError, ValueError) as error:
    raise ValueError("date must use YYYY-MM-DD") from error


def _valid_url(value: str) -> bool:
  parsed = urlparse(value)
  return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
