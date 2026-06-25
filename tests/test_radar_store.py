import unittest

from src.radar_store import (
  filter_signals,
  join_ranking_with_signals,
  load_daily_signals,
  load_daily_snapshot,
  load_ranking,
  summarize_signals,
  validate_daily_snapshot
)


class RadarStoreTest(unittest.TestCase):
  def test_loads_daily_radar_signals_from_fixtures(self):
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


if __name__ == "__main__":
  unittest.main()
