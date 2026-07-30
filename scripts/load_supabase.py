#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.persistence import (  # noqa: E402
  build_persistence_bundle,
  persistence_manifest,
  upsert_persistence_bundle
)


SUPABASE_CLI_VERSION = "2.110.0"


def get_local_credentials() -> tuple[str, str]:
  command = [
    "npx",
    "--yes",
    f"supabase@{SUPABASE_CLI_VERSION}",
    "status",
    "-o",
    "json",
    "--agent",
    "no",
  ]
  try:
    completed = subprocess.run(
      command,
      check=True,
      capture_output=True,
      text=True,
      timeout=30,
    )
    status = json.loads(completed.stdout)
    supabase_url = status["API_URL"]
    secret_key = status.get("SECRET_KEY") or status["SERVICE_ROLE_KEY"]
  except (
    KeyError,
    json.JSONDecodeError,
    subprocess.SubprocessError,
  ) as error:
    raise RuntimeError(
      "No fue posible obtener las credenciales de Supabase local. "
      "Confirma que Docker este activo y ejecuta `npx --yes "
      f"supabase@{SUPABASE_CLI_VERSION} status`."
    ) from error
  return supabase_url, secret_key


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
  parser.add_argument(
    "--local",
    action="store_true",
    help=(
      "Obtiene URL y clave de la instancia local mediante Supabase CLI. "
      "No imprime ni persiste credenciales."
    ),
  )
  args = parser.parse_args(argv)

  bundle = build_persistence_bundle()
  result = {
    "mode": "apply" if args.apply else "dry-run",
    "manifest": persistence_manifest(bundle)
  }
  if args.apply:
    if args.local:
      supabase_url, secret_key = get_local_credentials()
      result["target"] = "local"
    else:
      supabase_url = os.environ.get("SUPABASE_URL", "")
      secret_key = (
        os.environ.get("SUPABASE_SECRET_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
      )
      result["target"] = "configured-environment"
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
