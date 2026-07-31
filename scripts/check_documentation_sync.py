#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]


def collect_project_facts(root_dir: Path = ROOT_DIR) -> dict[str, Any]:
  daily_dir = root_dir / "data" / "signals" / "daily"
  ranking_dir = root_dir / "data" / "reviews" / "rankings"
  candidate_dir = root_dir / "data" / "sources" / "candidates"
  skills_dir = root_dir / "skills"
  evidence_dir = root_dir / "frontend" / "evidence"
  migrations_dir = root_dir / "supabase" / "migrations"

  snapshots = sorted(daily_dir.glob("daily-radar-*.json"))
  rankings = sorted(ranking_dir.glob("signal-review-ranking-*.json"))
  candidate_batches = sorted(candidate_dir.glob("source-candidates-*.json"))
  signal_count = sum(
    len(read_json(path).get("signals", []))
    for path in snapshots
  )
  ranking_entry_count = sum(
    len(read_json(path).get("rankedSignals", []))
    for path in rankings
  )
  candidate_count = sum(
    len(read_json(path).get("candidates", []))
    for path in candidate_batches
  )
  skill_count = sum(
    1
    for path in skills_dir.iterdir()
    if path.is_dir() and (path / "SKILL.md").is_file()
  )
  test_count = 0
  for path in sorted((root_dir / "tests").glob("test_*.py")):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    test_count += sum(
      1
      for node in ast.walk(tree)
      if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
      and node.name.startswith("test_")
    )

  table_rows = {
    "radar_snapshots": len(snapshots),
    "signals": signal_count,
    "rankings": len(rankings),
    "ranking_entries": ranking_entry_count,
    "source_candidate_batches": len(candidate_batches),
    "source_candidates": candidate_count
  }
  return {
    "tests": test_count,
    "skills": skill_count,
    "snapshots": len(snapshots),
    "signals": signal_count,
    "rankings": len(rankings),
    "rankingEntries": ranking_entry_count,
    "candidateBatches": len(candidate_batches),
    "candidates": candidate_count,
    "persistenceRows": sum(table_rows.values()),
    "migrations": len(list(migrations_dir.glob("*.sql"))),
    "evidenceImages": len(list(evidence_dir.glob("*.png"))),
    "tableRows": table_rows
  }


def check_documentation_sync(root_dir: Path = ROOT_DIR) -> dict[str, Any]:
  facts = collect_project_facts(root_dir)
  checks = {
    "README.md": [
      f"{facts['tests']} pruebas",
      f"{facts['snapshots']} snapshots",
      f"{facts['signals']} senales",
      f"{facts['rankings']} rankings",
      f"{facts['persistenceRows']} filas",
      f"{facts['skills']} skills",
      f"{facts['migrations']} migraciones",
      f"{facts['evidenceImages']} capturas",
      "frontend/",
      "docs/supabase-cloud.md",
      "scripts/check_documentation_sync.py"
    ],
    "docs/ai-radar-current-state.md": [
      f"{facts['tests']} pruebas",
      f"{facts['snapshots']} snapshots",
      f"{facts['signals']} senales",
      f"{facts['rankings']} rankings",
      f"{facts['persistenceRows']} filas",
      f"{facts['skills']} skills",
      f"{facts['migrations']} migraciones",
      f"{facts['evidenceImages']} capturas",
      "Supabase Cloud",
      "frontend/evidence/",
      "scripts/check_documentation_sync.py"
    ],
    "docs/ai-radar-operating-model.md": [
      "frontend/",
      "supabase/",
      "Supabase Cloud",
      "scripts/check_skill_sync.py",
      "scripts/check_documentation_sync.py"
    ],
    "docs/supabase-cloud.md": [
      f"`radar_snapshots` | {facts['snapshots']}",
      f"`signals` | {facts['signals']}",
      f"`rankings` | {facts['rankings']}",
      f"`ranking_entries` | {facts['rankingEntries']}",
      f"`source_candidate_batches` | {facts['candidateBatches']}",
      f"`source_candidates` | {facts['candidates']}",
      f"Total: {facts['persistenceRows']} filas",
      "RLS",
      "publishable"
    ]
  }

  errors = []
  for relative_path, markers in checks.items():
    path = root_dir / relative_path
    if not path.is_file():
      errors.append(f"{relative_path}: missing document")
      continue
    content = " ".join(path.read_text(encoding="utf-8").split())
    for marker in markers:
      if marker not in content:
        errors.append(f"{relative_path}: missing marker: {marker}")

  return {
    "inSync": not errors,
    "facts": facts,
    "errors": errors,
    "notion": {
      "page": "AI Radar — Centro de operacion y fuentes",
      "requiredCheck": (
        "Verificar manualmente o mediante el conector que Notion refleje "
        "las mismas metricas despues de cada cambio material."
      )
    }
  }


def read_json(path: Path) -> dict[str, Any]:
  return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
    description=(
      "Valida que README y documentos canonicos reflejen las metricas "
      "verificables del repositorio."
    )
  )
  parser.add_argument("--format", choices=["json", "text"], default="text")
  args = parser.parse_args(argv)

  result = check_documentation_sync()
  if args.format == "json":
    print(json.dumps(result, ensure_ascii=False, indent=2))
  else:
    print_text_report(result)
  return 0 if result["inSync"] else 1


def print_text_report(result: dict[str, Any]) -> None:
  facts = result["facts"]
  print(
    "project: "
    f"{facts['tests']} tests, "
    f"{facts['skills']} skills, "
    f"{facts['snapshots']} snapshots, "
    f"{facts['signals']} signals, "
    f"{facts['persistenceRows']} persistence rows"
  )
  if result["inSync"]:
    print("documentation: in_sync")
    return
  print("documentation: different")
  for error in result["errors"]:
    print(f"- {error}")


if __name__ == "__main__":
  raise SystemExit(main())
