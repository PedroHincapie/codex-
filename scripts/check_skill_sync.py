#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
CANONICAL_SKILLS_DIR = ROOT_DIR / "skills"
DEFAULT_ACTIVE_SKILLS_DIR = Path.home() / ".codex" / "skills"
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


def discover_skill_names(skills_dir: Path) -> list[str]:
  return sorted(
    path.name
    for path in skills_dir.iterdir()
    if path.is_dir() and (path / "SKILL.md").is_file()
  )


def compare_skill_directories(
  canonical_dir: Path,
  active_dir: Path
) -> dict[str, Any]:
  canonical_files = build_manifest(canonical_dir)
  active_files = build_manifest(active_dir) if active_dir.is_dir() else {}
  missing_files = sorted(set(canonical_files) - set(active_files))
  extra_files = sorted(set(active_files) - set(canonical_files))
  changed_files = sorted(
    path
    for path in set(canonical_files) & set(active_files)
    if canonical_files[path] != active_files[path]
  )

  if not active_dir.is_dir():
    status = "missing"
  elif missing_files or extra_files or changed_files:
    status = "different"
  else:
    status = "in_sync"

  return {
    "status": status,
    "missingFiles": missing_files,
    "extraFiles": extra_files,
    "changedFiles": changed_files
  }


def check_skill_sync(
  canonical_skills_dir: Path = CANONICAL_SKILLS_DIR,
  active_skills_dir: Path = DEFAULT_ACTIVE_SKILLS_DIR
) -> dict[str, Any]:
  skills = []
  for name in discover_skill_names(canonical_skills_dir):
    comparison = compare_skill_directories(
      canonical_skills_dir / name,
      active_skills_dir / name
    )
    skills.append({"skill": name, **comparison})

  return {
    "canonicalSkillsDir": str(canonical_skills_dir),
    "activeSkillsDir": str(active_skills_dir),
    "inSync": all(item["status"] == "in_sync" for item in skills),
    "skills": skills
  }


def build_manifest(directory: Path) -> dict[str, str]:
  manifest = {}
  for path in sorted(item for item in directory.rglob("*") if item.is_file()):
    relative_path = path.relative_to(directory)
    if any(part in IGNORED_PARTS for part in relative_path.parts):
      continue
    manifest[str(relative_path)] = hashlib.sha256(path.read_bytes()).hexdigest()
  return manifest


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
    description="Compara las skills canonicas del repositorio con las skills activas de Codex."
  )
  parser.add_argument(
    "--canonical-dir",
    type=Path,
    default=CANONICAL_SKILLS_DIR,
    help="Directorio que contiene las skills canonicas."
  )
  parser.add_argument(
    "--active-dir",
    type=Path,
    default=DEFAULT_ACTIVE_SKILLS_DIR,
    help="Directorio que contiene las skills activas."
  )
  parser.add_argument("--format", choices=["json", "text"], default="text")
  args = parser.parse_args(argv)

  result = check_skill_sync(args.canonical_dir, args.active_dir)
  if args.format == "json":
    print(json.dumps(result, ensure_ascii=False, indent=2))
  else:
    print_text_report(result)
  return 0 if result["inSync"] else 1


def print_text_report(result: dict[str, Any]) -> None:
  for item in result["skills"]:
    details = []
    if item["missingFiles"]:
      details.append(f"missing={','.join(item['missingFiles'])}")
    if item["extraFiles"]:
      details.append(f"extra={','.join(item['extraFiles'])}")
    if item["changedFiles"]:
      details.append(f"changed={','.join(item['changedFiles'])}")
    suffix = f" ({'; '.join(details)})" if details else ""
    print(f"{item['skill']}: {item['status']}{suffix}")


if __name__ == "__main__":
  raise SystemExit(main())
