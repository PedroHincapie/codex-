import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path


VALIDATOR_PATH = (
  Path(__file__).parents[1]
  / "skills"
  / "ai-radar-source-manager"
  / "scripts"
  / "validate_sources_cache.py"
)
SPEC = importlib.util.spec_from_file_location("validate_sources_cache", VALIDATOR_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def make_source(name, source_type, url):
  return {
    "name": name,
    "type": source_type,
    "url": url,
    "active": True,
    "description": "Fuente de prueba.",
    "lastReviewed": "2026-07-29",
    "priority": "alta",
    "uses": ["evidencia"],
    "frequency": "diaria",
    "health": "saludable",
    "lastSuccess": "2026-07-29",
    "consecutiveFailures": 0,
    "feedUrl": None,
    "lastContentDetected": None,
    "editorialConfidence": "alta",
  }


def make_cache():
  sources = [
    make_source("Community", "comunidad", "https://community.example.com"),
    make_source("Official", "fuente_oficial", "https://official.example.com"),
    make_source("Secondary", "medio_secundario", "https://secondary.example.com"),
    make_source("Repository", "repo_tecnico", "https://repo.example.com"),
  ]
  return {
    "version": 2,
    "generatedAt": "2026-07-29T13:28:10Z",
    "cachePolicy": {
      "ttlHours": 24,
      "expiresAt": "2026-07-30T13:28:10Z",
    },
    "sourceCatalog": {
      "provider": "notion",
      "status": "fresh",
    },
    "sources": sources,
    "subagentGroups": [
      {
        "id": "official-verification",
        "sourceUrls": ["https://official.example.com"],
      },
      {
        "id": "technical-repos",
        "sourceUrls": ["https://repo.example.com"],
      },
      {
        "id": "community-discovery",
        "sourceUrls": ["https://community.example.com"],
      },
      {
        "id": "secondary-context",
        "sourceUrls": ["https://secondary.example.com"],
      },
    ],
  }


class SourceManagerCacheTest(unittest.TestCase):
  def test_accepts_a_complete_deterministic_cache(self):
    self.assertEqual(VALIDATOR.validate_cache(make_cache()), [])

  def test_rejects_duplicate_urls_and_stale_groups(self):
    cache = deepcopy(make_cache())
    cache["sources"][1]["url"] = cache["sources"][0]["url"]

    errors = VALIDATOR.validate_cache(cache)

    self.assertTrue(any(error.startswith("duplicate source URLs") for error in errors))
    self.assertIn("subagentGroups do not match active sources", errors)

  def test_rejects_invalid_health_metadata(self):
    cache = make_cache()
    cache["sources"][0]["health"] = "desconocida"
    cache["sources"][0]["consecutiveFailures"] = -1

    errors = VALIDATOR.validate_cache(cache)

    self.assertIn("sources[0].health is invalid", errors)
    self.assertIn(
      "sources[0].consecutiveFailures must be a non-negative integer",
      errors,
    )


if __name__ == "__main__":
  unittest.main()
