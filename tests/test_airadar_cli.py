import io
import json
import unittest
from contextlib import redirect_stdout

from scripts.airadar import main


class AiradarCliTest(unittest.TestCase):
  def test_summary_accepts_explicit_json_format(self):
    stdout = io.StringIO()

    with redirect_stdout(stdout):
      exit_code = main(["summary", "--from", "2026-06-15", "--format", "json"])

    summary = json.loads(stdout.getvalue())

    self.assertEqual(exit_code, 0)
    self.assertGreaterEqual(summary["count"], 1)
    self.assertIn("byImpact", summary)

  def test_summary_keeps_default_json_output(self):
    stdout = io.StringIO()

    with redirect_stdout(stdout):
      exit_code = main(["summary", "--from", "2026-06-15"])

    summary = json.loads(stdout.getvalue())

    self.assertEqual(exit_code, 0)
    self.assertGreaterEqual(summary["count"], 1)
    self.assertIn("topTags", summary)


if __name__ == "__main__":
  unittest.main()
