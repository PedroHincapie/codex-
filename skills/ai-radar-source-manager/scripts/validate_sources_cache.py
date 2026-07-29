#!/usr/bin/env python3
"""Validate the AI Radar source cache using only the standard library."""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


SOURCE_TYPES = {
  "comunidad",
  "fuente_oficial",
  "medio_secundario",
  "repo_tecnico",
}
PRIORITIES = {"alta", "media", "baja"}
USES = {"evidencia", "descubrimiento", "contexto"}
FREQUENCIES = {"diaria", "semanal", "mensual"}
HEALTH_STATES = {"saludable", "degradada", "en_revision"}
CONFIDENCE_LEVELS = {"alta", "media", "baja"}
GROUPS_BY_TYPE = {
  "fuente_oficial": "official-verification",
  "repo_tecnico": "technical-repos",
  "comunidad": "community-discovery",
  "medio_secundario": "secondary-context",
}


def is_absolute_http_url(value):
  if not isinstance(value, str):
    return False
  parsed = urlparse(value)
  return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_iso_datetime(value):
  if not isinstance(value, str):
    return False
  try:
    datetime.fromisoformat(value.replace("Z", "+00:00"))
  except ValueError:
    return False
  return True


def validate_source(source, index):
  errors = []
  prefix = f"sources[{index}]"
  required = {
    "name",
    "type",
    "url",
    "active",
    "description",
    "lastReviewed",
    "priority",
    "uses",
    "frequency",
    "health",
    "lastSuccess",
    "consecutiveFailures",
    "feedUrl",
    "lastContentDetected",
    "editorialConfidence",
  }
  missing = sorted(required - set(source))
  if missing:
    errors.append(f"{prefix}: missing {', '.join(missing)}")
    return errors

  if not isinstance(source["name"], str) or not source["name"].strip():
    errors.append(f"{prefix}.name must be non-empty")
  if source["type"] not in SOURCE_TYPES:
    errors.append(f"{prefix}.type is invalid")
  if not is_absolute_http_url(source["url"]):
    errors.append(f"{prefix}.url must be absolute HTTP(S)")
  if source["active"] is not True:
    errors.append(f"{prefix}.active must be true")
  if source["priority"] not in PRIORITIES:
    errors.append(f"{prefix}.priority is invalid")
  if not isinstance(source["uses"], list) or not source["uses"]:
    errors.append(f"{prefix}.uses must be a non-empty list")
  elif set(source["uses"]) - USES:
    errors.append(f"{prefix}.uses contains invalid values")
  if source["frequency"] not in FREQUENCIES:
    errors.append(f"{prefix}.frequency is invalid")
  if source["health"] not in HEALTH_STATES:
    errors.append(f"{prefix}.health is invalid")
  if not isinstance(source["consecutiveFailures"], int) or source["consecutiveFailures"] < 0:
    errors.append(f"{prefix}.consecutiveFailures must be a non-negative integer")
  if source["feedUrl"] is not None and not is_absolute_http_url(source["feedUrl"]):
    errors.append(f"{prefix}.feedUrl must be null or absolute HTTP(S)")
  if source["editorialConfidence"] not in CONFIDENCE_LEVELS:
    errors.append(f"{prefix}.editorialConfidence is invalid")
  return errors


def validate_cache(data):
  errors = []
  if data.get("version") != 2:
    errors.append("version must be 2")
  if not is_iso_datetime(data.get("generatedAt")):
    errors.append("generatedAt must be an ISO datetime")

  policy = data.get("cachePolicy", {})
  if policy.get("ttlHours") != 24:
    errors.append("cachePolicy.ttlHours must be 24")
  if not is_iso_datetime(policy.get("expiresAt")):
    errors.append("cachePolicy.expiresAt must be an ISO datetime")

  catalog = data.get("sourceCatalog", {})
  if catalog.get("provider") != "notion":
    errors.append("sourceCatalog.provider must be notion")
  if catalog.get("status") != "fresh":
    errors.append("persisted sourceCatalog.status must be fresh")

  sources = data.get("sources")
  if not isinstance(sources, list) or not sources:
    return errors + ["sources must be a non-empty list"]
  for index, source in enumerate(sources):
    if not isinstance(source, dict):
      errors.append(f"sources[{index}] must be an object")
      continue
    errors.extend(validate_source(source, index))

  expected_order = sorted(
    sources,
    key=lambda item: (
      str(item.get("type", "")).casefold(),
      str(item.get("name", "")).casefold(),
    ),
  )
  if sources != expected_order:
    errors.append("sources must be sorted by type and name")

  urls = [source.get("url") for source in sources]
  duplicates = [url for url, count in Counter(urls).items() if count > 1]
  if duplicates:
    errors.append(f"duplicate source URLs: {', '.join(sorted(duplicates))}")

  groups = data.get("subagentGroups")
  if not isinstance(groups, list):
    return errors + ["subagentGroups must be a list"]
  expected_groups = {
    group_id: sorted(
      [
        source["url"]
        for source in sources
        if source.get("type") == source_type
      ],
      key=str.casefold,
    )
    for source_type, group_id in GROUPS_BY_TYPE.items()
  }
  actual_groups = {}
  for group in groups:
    group_id = group.get("id")
    if group_id in actual_groups:
      errors.append(f"duplicate group id: {group_id}")
      continue
    actual_groups[group_id] = group.get("sourceUrls")
  if actual_groups != expected_groups:
    errors.append("subagentGroups do not match active sources")
  return errors


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("cache", type=Path)
  args = parser.parse_args()

  try:
    data = json.loads(args.cache.read_text())
  except (OSError, json.JSONDecodeError) as error:
    print(json.dumps({"valid": False, "errors": [str(error)]}, indent=2))
    return 1

  errors = validate_cache(data)
  counts = Counter(source.get("type") for source in data.get("sources", []))
  print(json.dumps({
    "valid": not errors,
    "totalSources": sum(counts.values()),
    "typeCounts": dict(sorted(counts.items())),
    "errors": errors,
  }, indent=2))
  return 0 if not errors else 1


if __name__ == "__main__":
  sys.exit(main())
