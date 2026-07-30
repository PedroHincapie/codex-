import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.check_skill_sync import check_skill_sync, main


class SkillSyncTest(unittest.TestCase):
  def setUp(self):
    self.temporary_directory = tempfile.TemporaryDirectory()
    self.root = Path(self.temporary_directory.name)
    self.canonical = self.root / "canonical"
    self.active = self.root / "active"
    self.canonical.mkdir()
    self.active.mkdir()

  def tearDown(self):
    self.temporary_directory.cleanup()

  def write_skill(self, parent: Path, name: str, content: str = "# Skill\n") -> None:
    skill_dir = parent / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

  def test_reports_matching_skill_directories(self):
    self.write_skill(self.canonical, "example")
    self.write_skill(self.active, "example")

    result = check_skill_sync(self.canonical, self.active)

    self.assertTrue(result["inSync"])
    self.assertEqual(result["skills"][0]["status"], "in_sync")

  def test_reports_missing_and_changed_skills(self):
    self.write_skill(self.canonical, "changed", "# Canonical\n")
    self.write_skill(self.canonical, "missing")
    self.write_skill(self.active, "changed", "# Active\n")

    result = check_skill_sync(self.canonical, self.active)
    statuses = {item["skill"]: item["status"] for item in result["skills"]}

    self.assertFalse(result["inSync"])
    self.assertEqual(statuses, {"changed": "different", "missing": "missing"})

  def test_json_cli_returns_failure_for_drift(self):
    self.write_skill(self.canonical, "missing")
    stdout = io.StringIO()

    with redirect_stdout(stdout):
      exit_code = main([
        "--canonical-dir", str(self.canonical),
        "--active-dir", str(self.active),
        "--format", "json"
      ])

    result = json.loads(stdout.getvalue())
    self.assertEqual(exit_code, 1)
    self.assertFalse(result["inSync"])


if __name__ == "__main__":
  unittest.main()
