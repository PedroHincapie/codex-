#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.radar_store import (  # noqa: E402
  DEFAULT_LIST_FIELDS,
  audit_signals,
  filter_signals,
  join_ranking_with_signals,
  load_daily_signals,
  load_daily_snapshot,
  load_ranking,
  pick_fields,
  summarize_signals,
  validate_daily_snapshot
)


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)

  if args.command == "list":
    return list_signals(args)
  if args.command == "summary":
    return print_summary(args)
  if args.command == "show":
    return show_signal(args)
  if args.command == "ranking":
    return print_ranking(args)
  if args.command == "validate":
    return validate_snapshot(args)
  if args.command == "audit":
    return audit(args)

  parser.print_help()
  return 0


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    prog="airadar",
    description="Consulta datos locales de AI Radar."
  )
  subparsers = parser.add_subparsers(dest="command")

  list_parser = subparsers.add_parser("list", help="Lista senales diarias.")
  add_signal_filters(list_parser)
  add_output_options(list_parser, default_fields=",".join(DEFAULT_LIST_FIELDS))

  summary_parser = subparsers.add_parser("summary", help="Resume senales filtradas.")
  add_signal_filters(summary_parser)

  show_parser = subparsers.add_parser("show", help="Muestra una senal por id.")
  show_parser.add_argument("signal_id")
  show_parser.add_argument("--fields")

  ranking_parser = subparsers.add_parser("ranking", help="Muestra ranking editorial.")
  ranking_parser.add_argument("--date")
  add_output_options(ranking_parser, default_fields="rank,signalId,score,risk,impact,status,title")

  validate_parser = subparsers.add_parser("validate", help="Valida snapshots diarios locales.")
  validate_parser.add_argument("--date", help="Valida solo data/signals/daily/daily-radar-YYYY-MM-DD.json.")
  validate_parser.add_argument("--format", choices=["json", "tsv"], default="tsv")

  audit_parser = subparsers.add_parser("audit", help="Audita senales: duplicados, evidencias, estados y fuentes.")
  add_signal_filters(audit_parser)
  audit_parser.add_argument("--format", choices=["json"], default="json")

  return parser


def add_signal_filters(parser: argparse.ArgumentParser) -> None:
  parser.add_argument("--date")
  parser.add_argument("--from", dest="from_date")
  parser.add_argument("--to", dest="to_date")
  parser.add_argument("--tag")
  parser.add_argument("--impact")
  parser.add_argument("--status")
  parser.add_argument("--source")
  parser.add_argument("--source-type", dest="source_type")
  parser.add_argument("--q")


def add_output_options(parser: argparse.ArgumentParser, default_fields: str) -> None:
  parser.add_argument("--limit", type=int)
  parser.add_argument("--fields", default=default_fields)
  parser.add_argument("--format", choices=["json", "tsv"], default="tsv")


def list_signals(args: argparse.Namespace) -> int:
  signals = apply_limit(filter_signals(load_daily_signals(), vars(args)), args.limit)
  fields = split_csv(args.fields)
  write_records([pick_fields(signal, fields) for signal in signals], args.format)
  return 0


def print_summary(args: argparse.Namespace) -> int:
  signals = filter_signals(load_daily_signals(), vars(args))
  write_json(summarize_signals(signals))
  return 0


def show_signal(args: argparse.Namespace) -> int:
  signal = next((item for item in load_daily_signals() if item["id"] == args.signal_id), None)
  if not signal:
    raise SystemExit(f"Signal not found: {args.signal_id}")

  if args.fields:
    write_json(pick_fields(signal, split_csv(args.fields)))
  else:
    write_json(signal)
  return 0


def print_ranking(args: argparse.Namespace) -> int:
  ranking_result = load_ranking(date=args.date)
  if not ranking_result:
    raise SystemExit("No signal-review-ranking data file found")

  rows = apply_limit(join_ranking_with_signals(ranking_result["ranking"], load_daily_signals()), args.limit)
  fields = split_csv(args.fields)
  records = []

  for row in rows:
    record = {}
    for field in fields:
      record[field] = row.get("dimensions", {}).get("risk", "") if field == "risk" else row.get(field, "")
    records.append(record)

  write_records(records, args.format)
  return 0


def validate_snapshot(args: argparse.Namespace) -> int:
  if args.date:
    snapshots = [load_daily_snapshot(args.date)]
  else:
    dates = sorted({signal["radarDate"] for signal in load_daily_signals()})
    snapshots = [load_daily_snapshot(date) for date in dates]

  results = []
  for item in snapshots:
    if not item:
      results.append({"file": "", "valid": False, "errors": ["snapshot not found"]})
      continue

    errors = validate_daily_snapshot(item["snapshot"])
    results.append({
      "file": item["file"],
      "valid": not errors,
      "errors": errors
    })

  if args.format == "json":
    write_json(results)
  else:
    write_records(results, "tsv")

  return 0 if all(result["valid"] for result in results) else 1


def audit(args: argparse.Namespace) -> int:
  signals = filter_signals(load_daily_signals(), vars(args))
  write_json(audit_signals(signals))
  return 0


def split_csv(value: str) -> list[str]:
  return [item.strip() for item in value.split(",") if item.strip()]


def apply_limit(rows: list[Any], limit: int | None) -> list[Any]:
  return rows[:limit] if limit else rows


def write_records(records: list[dict[str, Any]], output_format: str) -> None:
  if output_format == "json":
    write_json(records)
    return

  if not records:
    return

  fields = list(records[0].keys())
  print("\t".join(fields))
  for record in records:
    print("\t".join(format_cell(record.get(field, "")) for field in fields))


def write_json(value: Any) -> None:
  print(json.dumps(value, ensure_ascii=False, indent=2))


def format_cell(value: Any) -> str:
  if isinstance(value, list):
    return ",".join(str(item) for item in value)
  return str(value)


if __name__ == "__main__":
  raise SystemExit(main())
