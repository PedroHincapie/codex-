import unittest
from unittest.mock import patch

from src.persistence import (
  TABLE_ORDER,
  build_persistence_bundle,
  persistence_manifest,
  upsert_persistence_bundle,
  validate_persistence_bundle
)


class PersistenceTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.bundle = build_persistence_bundle()

  def test_builds_all_persistence_tables_from_versioned_data(self):
    self.assertEqual(tuple(self.bundle), TABLE_ORDER)
    self.assertGreater(len(self.bundle["radar_snapshots"]), 0)
    self.assertGreater(len(self.bundle["signals"]), 0)
    self.assertGreater(len(self.bundle["rankings"]), 0)
    self.assertGreater(len(self.bundle["ranking_entries"]), 0)
    self.assertGreater(len(self.bundle["source_candidate_batches"]), 0)
    self.assertGreater(len(self.bundle["source_candidates"]), 0)

  def test_bundle_preserves_relations_and_has_unique_keys(self):
    self.assertEqual(validate_persistence_bundle(self.bundle), [])

    snapshot_dates = {row["radar_date"] for row in self.bundle["radar_snapshots"]}
    signal_ids = {row["id"] for row in self.bundle["signals"]}
    ranking_dates = {row["radar_date"] for row in self.bundle["rankings"]}
    batch_files = {row["source_file"] for row in self.bundle["source_candidate_batches"]}

    self.assertTrue(all(row["radar_date"] in snapshot_dates for row in self.bundle["signals"]))
    self.assertTrue(all(row["ranking_date"] in ranking_dates for row in self.bundle["ranking_entries"]))
    self.assertTrue(all(row["signal_id"] in signal_ids for row in self.bundle["ranking_entries"]))
    self.assertTrue(all(row["batch_file"] in batch_files for row in self.bundle["source_candidates"]))

  def test_manifest_matches_bundle_counts(self):
    manifest = persistence_manifest(self.bundle)
    counts = {item["table"]: item["rows"] for item in manifest["tables"]}

    self.assertEqual(counts, {table: len(self.bundle[table]) for table in TABLE_ORDER})
    self.assertEqual(manifest["totalRows"], sum(counts.values()))

  def test_detects_duplicate_primary_keys(self):
    bundle = {table: [] for table in TABLE_ORDER}
    bundle["radar_snapshots"] = [
      {"radar_date": "2026-07-29"},
      {"radar_date": "2026-07-29"}
    ]

    errors = validate_persistence_bundle(bundle)

    self.assertIn("duplicate key radar_date=('2026-07-29',)", errors)

  @patch("src.persistence.urlopen")
  def test_upserts_tables_in_dependency_order_without_exposing_secret(self, mocked_urlopen):
    response = mocked_urlopen.return_value.__enter__.return_value
    response.status = 201
    minimal_bundle = {table: [] for table in TABLE_ORDER}
    minimal_bundle["radar_snapshots"] = [{"radar_date": "2026-07-29"}]

    result = upsert_persistence_bundle(
      minimal_bundle,
      "https://example.supabase.co",
      "sb_secret_test",
      batch_size=1
    )

    request = mocked_urlopen.call_args.args[0]
    self.assertEqual(result["totalRows"], 1)
    self.assertIn("/rest/v1/radar_snapshots?on_conflict=radar_date", request.full_url)
    self.assertEqual(request.headers["Apikey"], "sb_secret_test")
    self.assertNotIn("Authorization", request.headers)


if __name__ == "__main__":
  unittest.main()
