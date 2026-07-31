#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
  sys.path.insert(0, str(ROOT_DIR))

from src.source_findings import (  # noqa: E402
  REJECTION_REASONS,
  build_candidate_rejection,
  build_content_unavailable,
  build_fetch_failure,
  write_report
)


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    description="Registra fallos y descartes de fuentes sin detener la recoleccion."
  )
  subparsers = parser.add_subparsers(dest="kind", required=True)

  fetch = subparsers.add_parser("fetch-failure", help="Registra un fallo HTTP estructurado.")
  _add_common_arguments(fetch)
  fetch.add_argument("--group", required=True)
  fetch.add_argument("--http-status", required=True, type=int)
  fetch.add_argument("--strategy", default="canonical-url")
  fetch.add_argument("--message", default="")

  rejection = subparsers.add_parser(
    "candidate-rejection",
    help="Registra un candidato descartado sin inventar metadatos."
  )
  _add_common_arguments(rejection)
  rejection.add_argument(
    "--reason-code",
    choices=sorted(REJECTION_REASONS),
    default="missing-verifiable-published-at"
  )
  rejection.add_argument("--raw-input", default="")

  content = subparsers.add_parser(
    "content-unavailable",
    help="Registra una fuente valida sin contenido reciente verificable."
  )
  _add_common_arguments(content)
  content.add_argument("--group", required=True)
  content.add_argument("--message", default="")
  return parser


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
  parser.add_argument("--source-name", required=True)
  parser.add_argument("--url", required=True)
  parser.add_argument("--retrieved-at", required=True)
  parser.add_argument("--output")
  parser.add_argument("--format", choices=("json", "text"), default="text")


def main(argv: list[str] | None = None) -> int:
  args = build_parser().parse_args(argv)
  if args.kind == "fetch-failure":
    finding = build_fetch_failure(
      source_name=args.source_name,
      url=args.url,
      retrieved_at=args.retrieved_at,
      group=args.group,
      http_status=args.http_status,
      strategy=args.strategy,
      message=args.message
    )
  elif args.kind == "candidate-rejection":
    finding = build_candidate_rejection(
      source_name=args.source_name,
      url=args.url,
      retrieved_at=args.retrieved_at,
      reason_code=args.reason_code,
      raw_input=args.raw_input
    )
  else:
    finding = build_content_unavailable(
      source_name=args.source_name,
      url=args.url,
      retrieved_at=args.retrieved_at,
      group=args.group,
      message=args.message
    )

  output = Path(args.output) if args.output else (
    ROOT_DIR / "data" / "observability" / f"source-findings-{args.retrieved_at}.json"
  )
  report = write_report(output, finding)
  if args.format == "json":
    print(json.dumps({"output": str(output), "finding": finding, "summary": report["summary"]}, indent=2))
  else:
    print(
      f"{finding['kind']}: {finding['reasonCode']} | "
      f"{finding['source']['name']} | {output}"
    )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
