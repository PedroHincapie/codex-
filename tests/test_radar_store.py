import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.radar_store import (
  audit_signals,
  filter_signals,
  find_duplicate_groups,
  find_empty_evidence,
  get_source_type,
  join_ranking_with_signals,
  list_daily_snapshot_dates,
  list_primary_sources,
  load_daily_signals,
  load_daily_snapshot,
  report_snapshot_coverage,
  summarize_signals,
  validate_daily_snapshot
)


class RadarStoreTest(unittest.TestCase):
  def test_loads_daily_radar_signals_from_local_data(self):
    signals = load_daily_signals()

    self.assertGreaterEqual(len(signals), 8)
    self.assertTrue(all(signal["id"].startswith(signal["radarDate"]) for signal in signals))

  def test_filters_signals_by_supported_fields(self):
    signals = load_daily_signals()

    self.assertGreaterEqual(len(filter_signals(signals, {"tag": "agents"})), 1)
    self.assertTrue(all(signal["radarDate"] == "2026-06-24" for signal in filter_signals(signals, {"date": "2026-06-24"})))
    self.assertTrue(all(signal["impact"]["level"] == "high" for signal in filter_signals(signals, {"impact": "high"})))
    self.assertTrue(all(signal["status"] == "actionable" for signal in filter_signals(signals, {"status": "actionable"})))
    self.assertTrue(all(signal["source"]["name"] == "Axios" for signal in filter_signals(signals, {"source": "Axios"})))
    self.assertGreaterEqual(len(filter_signals(signals, {"date": "2026-06-25", "source": "GitHub"})), 1)
    self.assertTrue(all(get_source_type(signal) == "repo" for signal in filter_signals(signals, {"date": "2026-06-25", "source_type": "repo"})))
    self.assertTrue(any("DeepMind" in signal["title"] for signal in filter_signals(signals, {"q": "DeepMind"})))

  def test_summarizes_filtered_signals(self):
    summary = summarize_signals(filter_signals(load_daily_signals(), {"from_date": "2026-06-15"}))

    self.assertGreaterEqual(summary["count"], 1)
    self.assertGreaterEqual(summary["byImpact"]["high"], 1)
    self.assertTrue(any(item["tag"] in ["policy", "datacenters"] for item in summary["topTags"]))

  def test_joins_ranking_entries_with_signal_metadata(self):
    signals = load_daily_signals()
    ranking = {
      "rankedSignals": [
        {"rank": 1, "signalId": signals[0]["id"], "score": 4.5},
        {"rank": 2, "signalId": signals[1]["id"], "score": 4.0}
      ]
    }
    ranked_signals = join_ranking_with_signals(ranking, signals)

    self.assertEqual(ranked_signals[0]["rank"], 1)
    self.assertGreaterEqual(ranked_signals[0]["score"], ranked_signals[-1]["score"])
    self.assertTrue(all(row["title"] for row in ranked_signals))

  def test_validates_daily_snapshot_shape(self):
    snapshot = load_daily_snapshot("2026-06-20")["snapshot"]

    self.assertEqual(validate_daily_snapshot(snapshot), [])

  def test_audits_status_counts_empty_evidence_duplicates_and_sources(self):
    signals = [
      {
        "id": "2026-06-20-alpha",
        "title": "Alpha signal",
        "radarDate": "2026-06-20",
        "status": "confirmed",
        "source": {"name": "Primary Lab", "url": "https://example.com/alpha"},
        "evidence": ["Fact"],
        "impact": {"level": "high"}
      },
      {
        "id": "2026-06-20-beta",
        "title": "Beta signal",
        "radarDate": "2026-06-20",
        "status": "candidate",
        "source": {"name": "Primary Lab", "url": "https://example.com/beta"},
        "evidence": [""],
        "impact": {"level": "medium"}
      },
      {
        "id": "2026-06-20-beta",
        "title": "Beta signal",
        "radarDate": "2026-06-20",
        "status": "candidate",
        "source": {"name": "Other Source", "url": "https://example.com/beta"},
        "evidence": ["Another fact"],
        "impact": {"level": "medium"}
      }
    ]

    audit = audit_signals(signals)

    self.assertEqual(audit["statusCounts"], {"confirmed": 1, "candidate": 2})
    self.assertEqual(len(audit["emptyEvidence"]), 1)
    self.assertEqual(audit["primarySources"][0]["source"], "Primary Lab")
    self.assertEqual(audit["primarySources"][0]["count"], 2)
    self.assertEqual(
      [(group["field"], group["value"]) for group in audit["duplicateGroups"]],
      [
        ("id", "2026-06-20-beta"),
        ("url", "https://example.com/beta"),
        ("title", "beta signal")
      ]
    )

    self.assertEqual(find_empty_evidence(signals), audit["emptyEvidence"])
    self.assertEqual(find_duplicate_groups(signals), audit["duplicateGroups"])
    self.assertEqual(list_primary_sources(signals), audit["primarySources"])

  def test_reports_snapshot_coverage_gaps_without_loading_signals(self):
    with TemporaryDirectory() as directory:
      daily_dir = Path(directory) / "signals" / "daily"
      daily_dir.mkdir(parents=True)
      for snapshot_date in ["2026-06-13", "2026-06-15", "2026-06-17"]:
        (daily_dir / f"daily-radar-{snapshot_date}.json").write_text("{}", encoding="utf-8")

      self.assertEqual(
        list_daily_snapshot_dates(directory),
        ["2026-06-13", "2026-06-15", "2026-06-17"]
      )

      coverage = report_snapshot_coverage("2026-06-13", "2026-06-17", directory)

      self.assertEqual(coverage["observedRange"], {"from": "2026-06-13", "to": "2026-06-17"})
      self.assertEqual(coverage["coverageRange"], {"from": "2026-06-13", "to": "2026-06-17"})
      self.assertEqual(coverage["snapshotDates"], ["2026-06-13", "2026-06-15", "2026-06-17"])
      self.assertEqual(coverage["missingDates"], ["2026-06-14", "2026-06-16"])
      self.assertEqual(
        coverage["counts"],
        {
          "observedSnapshots": 3,
          "expectedDays": 5,
          "daysWithSnapshot": 3,
          "missingDays": 2
        }
      )

  def test_reports_snapshot_coverage_for_observed_range_by_default(self):
    with TemporaryDirectory() as directory:
      daily_dir = Path(directory) / "signals" / "daily"
      daily_dir.mkdir(parents=True)
      for snapshot_date in ["2026-07-01", "2026-07-03"]:
        (daily_dir / f"daily-radar-{snapshot_date}.json").write_text("{}", encoding="utf-8")

      coverage = report_snapshot_coverage(data_dir=directory)

      self.assertEqual(coverage["coverageRange"], {"from": "2026-07-01", "to": "2026-07-03"})
      self.assertEqual(coverage["missingDates"], ["2026-07-02"])

  def test_rejects_invalid_snapshot_coverage_range(self):
    with self.assertRaises(ValueError):
      report_snapshot_coverage("2026-07-09", "2026-06-13")


if __name__ == "__main__":
  unittest.main()
