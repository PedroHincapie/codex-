import json
import tempfile
import unittest
from pathlib import Path

from src.radar_store import load_daily_signals
from src.ranking_engine import (
  WEIGHTS,
  build_ranking,
  deduplicate_signals,
  score_signal,
  write_ranking
)


def make_signal(signal_id="2026-06-25-alpha", **overrides):
  signal = {
    "id": signal_id,
    "title": "Control de seguridad para agentes",
    "radarDate": "2026-06-25",
    "sourceType": "official",
    "source": {
      "name": "Primary Lab",
      "url": f"https://example.com/{signal_id}",
      "publishedAt": "2026-06-25",
      "retrievedAt": "2026-06-25"
    },
    "evidence": ["El laboratorio publico controles verificables para agentes autonomos."],
    "impact": {"level": "high", "summary": "Afecta seguridad y despliegue."},
    "action": "Evaluar controles antes de implementar agentes.",
    "status": "actionable",
    "tags": ["agents", "security"]
  }
  signal.update(overrides)
  return signal


class RankingEngineTest(unittest.TestCase):
  def test_applies_weighted_formula_and_keeps_risk_separate(self):
    ranked = score_signal(make_signal())
    expected = round(sum(ranked["dimensions"][name] * weight for name, weight in WEIGHTS.items()), 2)

    self.assertEqual(ranked["score"], expected)
    self.assertIn("risk", ranked["dimensions"])
    self.assertNotIn("risk", WEIGHTS)
    self.assertTrue(all(0 <= value <= 5 for value in ranked["dimensions"].values()))

  def test_deduplicates_by_url_and_keeps_stronger_signal(self):
    weak = make_signal(
      "2026-06-25-weak",
      sourceType="social",
      evidence=["Dato breve"],
      action="Seguir.",
      status="candidate"
    )
    strong = make_signal(
      "2026-06-25-strong",
      source={**weak["source"], "name": "Primary Lab"}
    )

    unique, groups = deduplicate_signals([weak, strong])

    self.assertEqual([item["id"] for item in unique], ["2026-06-25-strong"])
    self.assertEqual(groups[0]["matchedBy"], ["url", "title"])

  def test_uses_stable_id_as_final_tiebreaker(self):
    beta = make_signal("2026-06-25-beta", title="Beta", source={**make_signal()["source"], "url": "https://example.com/beta"})
    alpha = make_signal("2026-06-25-alpha", title="Alpha", source={**make_signal()["source"], "url": "https://example.com/alpha"})

    ranking = build_ranking([beta, alpha], "2026-06-25")

    self.assertEqual([item["signalId"] for item in ranking["rankedSignals"]], ["2026-06-25-alpha", "2026-06-25-beta"])

  def test_skips_incomplete_signals_with_reason(self):
    incomplete = make_signal(action="")

    ranking = build_ranking([incomplete], "2026-06-25")

    self.assertEqual(ranking["rankedSignals"], [])
    self.assertEqual(ranking["audit"]["skippedSignals"][0]["reason"], "missing fields: action")

  def test_current_data_removes_all_strong_duplicates(self):
    ranking = build_ranking(load_daily_signals(), "2026-06-25")
    ranked_ids = {item["signalId"] for item in ranking["rankedSignals"]}
    duplicate_pairs = [
      {"2026-06-18-deepmind-agent-controls", "2026-06-18-deepmind-agent-control-roadmap"},
      {"2026-06-20-ai-ceos-g7", "2026-06-20-ai-ceos-g7-standards"},
      {"2026-06-15-amazon-discloses-datacenter-water-use", "2026-06-15-amazon-datacenter-water-transparency"}
    ]

    self.assertEqual(len(ranking["audit"]["duplicateGroups"]), 3)
    self.assertEqual(len(ranked_ids), 30)
    self.assertTrue(all(len(pair & ranked_ids) == 1 for pair in duplicate_pairs))

  def test_writes_identical_output_for_identical_input(self):
    ranking = build_ranking([make_signal()], "2026-06-25")
    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / "ranking.json"
      write_ranking(ranking, path)
      first = path.read_bytes()
      write_ranking(build_ranking([make_signal()], "2026-06-25"), path)

      self.assertEqual(path.read_bytes(), first)
      self.assertEqual(json.loads(first)["scoringVersion"], "1.0.0")


if __name__ == "__main__":
  unittest.main()
