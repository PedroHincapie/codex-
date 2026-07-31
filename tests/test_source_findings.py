import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.source_findings import (
  build_candidate_rejection,
  build_content_unavailable,
  build_fetch_failure,
  merge_report,
  validate_finding
)


ROOT_DIR = Path(__file__).resolve().parents[1]
FIXTURE = json.loads(
  (ROOT_DIR / "tests" / "fixtures" / "source-findings.json").read_text(encoding="utf-8")
)


class SourceFindingsTest(unittest.TestCase):
  def test_records_http_403_without_stopping_other_sources(self):
    item = FIXTURE["fetchFailure"]
    finding = build_fetch_failure(
      source_name=item["sourceName"],
      url=item["url"],
      retrieved_at=item["retrievedAt"],
      group=item["group"],
      http_status=item["httpStatus"]
    )

    self.assertEqual(finding["outcome"], item["expectedOutcome"])
    self.assertEqual(finding["reasonCode"], item["expectedReason"])
    self.assertEqual(finding["collectionAction"], "continue-other-sources")
    self.assertEqual(finding["sourceHealthAction"], "record-only")
    self.assertEqual(validate_finding(finding), [])

  def test_rejects_candidate_without_inventing_publication_date(self):
    item = FIXTURE["candidateRejection"]
    finding = build_candidate_rejection(
      source_name=item["sourceName"],
      url=item["url"],
      retrieved_at=item["retrievedAt"]
    )

    self.assertEqual(finding["outcome"], item["expectedOutcome"])
    self.assertEqual(finding["reasonCode"], item["expectedReason"])
    self.assertNotIn("publishedAt", finding["candidate"])
    self.assertEqual(validate_finding(finding), [])

  def test_report_merge_is_idempotent_by_finding_id(self):
    finding = build_fetch_failure(
      source_name="Ars Technica",
      url="https://arstechnica.com/ai/",
      retrieved_at="2026-07-30",
      group="secondary-context",
      http_status=403
    )
    report = merge_report(None, finding)
    report = merge_report(report, finding)

    self.assertEqual(report["summary"]["total"], 1)
    self.assertEqual(report["summary"]["reasonCounts"], {"http-403": 1})

  def test_distinguishes_missing_content_from_http_failures(self):
    finding = build_content_unavailable(
      source_name="Example AI",
      url="https://example.com/ai/",
      retrieved_at="2026-07-30",
      group="secondary-context"
    )

    self.assertEqual(finding["kind"], "content_unavailable")
    self.assertEqual(finding["outcome"], "no_content")
    self.assertEqual(validate_finding(finding), [])

  def test_cli_persists_both_findings_in_one_report(self):
    with tempfile.TemporaryDirectory() as directory:
      output = Path(directory) / "source-findings-2026-07-30.json"
      commands = [
        [
          "fetch-failure", "--source-name", "Ars Technica",
          "--url", "https://arstechnica.com/ai/", "--retrieved-at", "2026-07-30",
          "--group", "secondary-context", "--http-status", "403"
        ],
        [
          "candidate-rejection", "--source-name", "IEEE",
          "--url", "https://spectrum.ieee.org/artificial-intelligence",
          "--retrieved-at", "2026-07-30"
        ]
      ]
      for arguments in commands:
        result = subprocess.run(
          [sys.executable, "scripts/record_source_finding.py", *arguments, "--output", str(output)],
          cwd=ROOT_DIR,
          check=False,
          capture_output=True,
          text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

      report = json.loads(output.read_text(encoding="utf-8"))
      self.assertEqual(report["summary"]["fetchFailures"], 1)
      self.assertEqual(report["summary"]["candidateRejections"], 1)


if __name__ == "__main__":
  unittest.main()
