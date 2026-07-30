import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "frontend" / "supabase-config.js"
DATA_PATH = ROOT / "frontend" / "data.js"


class FrontendSupabaseConfigTest(unittest.TestCase):
  def test_frontend_uses_only_a_publishable_key(self):
    config = CONFIG_PATH.read_text(encoding="utf-8")

    self.assertIn("sb_publishable_", config)
    self.assertNotIn("service_role", config.lower())
    self.assertNotIn("secretKey", config)
    self.assertIsNone(re.search(r"eyJ[A-Za-z0-9_-]{20,}\.", config))

  def test_cloud_project_is_explicitly_configured(self):
    config = CONFIG_PATH.read_text(encoding="utf-8")

    self.assertIn('projectId: "xredenxxhnzkmfxxnrlg"', config)
    self.assertIn(
      'url: "https://xredenxxhnzkmfxxnrlg.supabase.co"',
      config,
    )

  def test_data_adapter_keeps_an_explicit_local_fallback(self):
    data_source = DATA_PATH.read_text(encoding="utf-8")

    self.assertIn('kind: "supabase"', data_source)
    self.assertIn('kind: "fixture"', data_source)
    self.assertIn('demoState === "fallback"', data_source)
    self.assertIn("data.fallbackReason", data_source)


if __name__ == "__main__":
  unittest.main()
