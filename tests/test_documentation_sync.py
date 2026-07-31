import unittest

from scripts.check_documentation_sync import check_documentation_sync


class DocumentationSyncTest(unittest.TestCase):
  def test_canonical_documentation_matches_verifiable_project_facts(self):
    result = check_documentation_sync()

    self.assertTrue(result["inSync"], "\n".join(result["errors"]))
    self.assertEqual(result["facts"]["tests"], 36)
    self.assertEqual(result["facts"]["skills"], 8)
    self.assertEqual(result["facts"]["persistenceRows"], 449)


if __name__ == "__main__":
  unittest.main()
