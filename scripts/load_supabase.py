#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.persistence import (  # noqa: E402
  build_persistence_bundle,
  persistence_manifest,
  upsert_persistence_bundle
)


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
    description="Carga idempotente de los datos versionados de AI Radar en Supabase."
  )
  parser.add_argument(
    "--apply",
    action="store_true",
    help="Ejecuta los upserts. Sin este flag solo valida y muestra el manifiesto."
  )
  parser.add_argument("--batch-size", type=int, default=100)
  args = parser.parse_args(argv)

  bundle = build_persistence_bundle()
  result = {
    "mode": "apply" if args.apply else "dry-run",
    "manifest": persistence_manifest(bundle)
  }
  if args.apply:
    supabase_url = os.environ.get("SUPABASE_URL", "")
    secret_key = (
      os.environ.get("SUPABASE_SECRET_KEY")
      or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    )
    result["applied"] = upsert_persistence_bundle(
      bundle,
      supabase_url=supabase_url,
      secret_key=secret_key,
      batch_size=args.batch_size
    )

  print(json.dumps(result, ensure_ascii=False, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
