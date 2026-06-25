import unittest

from src.radar_store import (
  audit_signals,
  filter_signals,
  find_duplicate_groups,
  find_empty_evidence,
  get_source_type,
  join_ranking_with_signals,
  list_primary_sources,
  load_daily_signals,
  load_daily_snapshot,
  load_ranking,
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
    ranking_result = load_ranking(date="2026-06-24")
    ranked_signals = join_ranking_with_signals(ranking_result["ranking"], signals)

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


if __name__ == "__main__":
  unittest.main()
