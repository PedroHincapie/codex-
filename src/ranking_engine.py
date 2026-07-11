from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCORING_VERSION = "1.0.0"
WEIGHTS = {
  "novelty": 0.15,
  "evidence": 0.20,
  "impact": 0.25,
  "reliability": 0.15,
  "actionability": 0.20,
  "strategicFit": 0.05
}
IMPACT_SCORES = {"low": 1, "medium": 3, "medium-high": 4, "high": 5}
SOURCE_SCORES = {"official": 5, "paper": 5, "repo": 4, "product": 4, "news": 4, "social": 2}
NOVELTY_SCORES = {
  "candidate": 3,
  "debated": 4,
  "evolving": 4,
  "confirmed": 3,
  "actionable": 4,
  "archived": 1
}
ACTION_MARKERS = (
  "adopt", "audit", "compar", "disen", "evalu", "implement", "medir",
  "monitor", "prepar", "prioriz", "probar", "revis", "track"
)
RISK_MARKERS = (
  "compliance", "dependencia", "privacidad", "regulacion", "regulation",
  "riesgo", "safety", "seguridad", "security"
)
STRATEGIC_TAGS = {
  "agents", "ai-for-science", "cloud", "compliance", "frontier-models",
  "infrastructure", "mcp", "policy", "regulation", "safety", "security"
}
REQUIRED_SIGNAL_FIELDS = ("id", "title", "source", "evidence", "impact", "action", "status", "tags")


def build_ranking(signals: list[dict[str, Any]], radar_date: str) -> dict[str, Any]:
  eligible = [signal for signal in signals if _published_at(signal) <= radar_date]
  complete = []
  skipped = []
  for signal in eligible:
    missing = missing_ranking_fields(signal)
    if missing:
      skipped.append({"signalId": signal.get("id", ""), "reason": f"missing fields: {','.join(missing)}"})
    else:
      complete.append(signal)

  unique, duplicates = deduplicate_signals(complete)
  scored = [score_signal(signal) for signal in unique]
  scored.sort(key=_ranking_sort_key)

  ranked = []
  for index, item in enumerate(scored, start=1):
    ranked.append({"rank": index, **item})

  return {
    "generatedAt": f"{radar_date}T00:00:00Z",
    "reviewedSnapshot": "data/signals/daily/",
    "radarDate": radar_date,
    "scoringVersion": SCORING_VERSION,
    "weights": WEIGHTS,
    "audit": {
      "inputSignals": len(eligible),
      "rankedSignals": len(ranked),
      "duplicateGroups": duplicates,
      "skippedSignals": sorted(skipped, key=lambda item: item["signalId"])
    },
    "rankedSignals": ranked
  }


def score_signal(signal: dict[str, Any]) -> dict[str, Any]:
  dimensions = score_dimensions(signal)
  score = round(sum(dimensions[name] * weight for name, weight in WEIGHTS.items()), 2)
  return {
    "signalId": signal["id"],
    "score": score,
    "dimensions": dimensions,
    "reason": _score_reason(dimensions)
  }


def score_dimensions(signal: dict[str, Any]) -> dict[str, int]:
  source_type = _source_type(signal)
  evidence = [str(item).strip() for item in signal.get("evidence", []) if str(item).strip()]
  action = _normalize(signal.get("action", ""))
  text = _normalize(" ".join([
    signal.get("title", ""),
    signal.get("impact", {}).get("summary", ""),
    signal.get("action", ""),
    *signal.get("tags", [])
  ]))

  evidence_score = min(5, 2 + len(evidence))
  if evidence and max(len(item) for item in evidence) >= 80:
    evidence_score = min(5, evidence_score + 1)

  actionability = 3
  if any(marker in action for marker in ACTION_MARKERS):
    actionability = 4
  if signal.get("status") == "actionable":
    actionability = 5

  tags = set(signal.get("tags", []))
  strategic_fit = 5 if tags & STRATEGIC_TAGS else 4
  impact = IMPACT_SCORES.get(signal.get("impact", {}).get("level", ""), 0)
  risk = max(1, impact - 1)
  if any(marker in text for marker in RISK_MARKERS):
    risk = min(5, risk + 1)

  return {
    "novelty": NOVELTY_SCORES.get(signal.get("status", ""), 2),
    "evidence": evidence_score,
    "impact": impact,
    "reliability": SOURCE_SCORES.get(source_type, 2),
    "actionability": actionability,
    "strategicFit": strategic_fit,
    "risk": risk
  }


def deduplicate_signals(signals: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
  groups: list[list[dict[str, Any]]] = []
  for signal in sorted(signals, key=lambda item: item.get("id", "")):
    matching = [group for group in groups if any(_same_signal(signal, item) for item in group)]
    if not matching:
      groups.append([signal])
      continue
    merged = [signal]
    for group in matching:
      merged.extend(group)
      groups.remove(group)
    groups.append(merged)

  unique = []
  duplicate_groups = []
  for group in groups:
    keeper = max(group, key=_dedup_quality_key)
    unique.append(keeper)
    if len(group) > 1:
      duplicate_groups.append({
        "keptSignalId": keeper.get("id", ""),
        "mergedSignalIds": sorted(item.get("id", "") for item in group if item is not keeper),
        "matchedBy": _matching_fields(group)
      })

  duplicate_groups.sort(key=lambda item: (item["keptSignalId"], item["mergedSignalIds"]))
  return unique, duplicate_groups


def missing_ranking_fields(signal: dict[str, Any]) -> list[str]:
  missing = [field for field in REQUIRED_SIGNAL_FIELDS if not signal.get(field)]
  source = signal.get("source", {})
  if source and not all(source.get(field) for field in ("name", "url", "publishedAt")):
    missing.append("source.name/url/publishedAt")
  impact = signal.get("impact", {})
  if impact and not all(impact.get(field) for field in ("level", "summary")):
    missing.append("impact.level/summary")
  return missing


def write_ranking(ranking: dict[str, Any], path: Path) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(ranking, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _ranking_sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
  dimensions = item["dimensions"]
  return (
    -item["score"],
    -dimensions["evidence"],
    -dimensions["actionability"],
    -dimensions["impact"],
    item["signalId"]
  )


def _dedup_quality_key(signal: dict[str, Any]) -> tuple[Any, ...]:
  dimensions = score_dimensions(signal)
  return (
    dimensions["evidence"],
    dimensions["reliability"],
    dimensions["actionability"],
    dimensions["impact"],
    signal.get("id", "")
  )


def _same_signal(left: dict[str, Any], right: dict[str, Any]) -> bool:
  return any(
    left_value and left_value == right_value
    for left_value, right_value in (
      (left.get("id", ""), right.get("id", "")),
      (left.get("source", {}).get("url", ""), right.get("source", {}).get("url", "")),
      (_normalize(left.get("title", "")), _normalize(right.get("title", "")))
    )
  )


def _matching_fields(group: list[dict[str, Any]]) -> list[str]:
  fields = []
  for field, getter in (
    ("id", lambda item: item.get("id", "")),
    ("url", lambda item: item.get("source", {}).get("url", "")),
    ("title", lambda item: _normalize(item.get("title", "")))
  ):
    values = [getter(item) for item in group]
    if any(value and values.count(value) > 1 for value in values):
      fields.append(field)
  return fields


def _score_reason(dimensions: dict[str, int]) -> str:
  strongest = sorted(
    WEIGHTS,
    key=lambda name: (-(dimensions[name] * WEIGHTS[name]), name)
  )[:2]
  return f"Prioridad determinada por {strongest[0]}={dimensions[strongest[0]]} y {strongest[1]}={dimensions[strongest[1]]}; risk={dimensions['risk']} requiere revision separada."


def _published_at(signal: dict[str, Any]) -> str:
  return signal.get("source", {}).get("publishedAt", signal.get("radarDate", ""))


def _source_type(signal: dict[str, Any]) -> str:
  explicit = _normalize(signal.get("sourceType", ""))
  if explicit:
    return explicit
  source = signal.get("source", {})
  name = _normalize(source.get("name", ""))
  url = _normalize(source.get("url", ""))
  if "github" in name or "github.com" in url or "gitlab" in name or "gitlab.com" in url:
    return "repo"
  if "arxiv" in name or "arxiv.org" in url or "doi.org" in url:
    return "paper"
  if any(marker in name for marker in ("openai", "anthropic", "nist", "google", "microsoft", "meta")):
    return "official"
  return "news"


def _normalize(value: Any) -> str:
  return str(value).strip().lower()
