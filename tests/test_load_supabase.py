import json
import unittest
from unittest.mock import Mock, patch

from scripts.load_supabase import get_local_credentials, main


class LoadSupabaseTest(unittest.TestCase):
  @patch("scripts.load_supabase.subprocess.run")
  def test_gets_local_credentials_without_printing_them(self, mocked_run):
    mocked_run.return_value = Mock(
      stdout=json.dumps({
        "API_URL": "http://127.0.0.1:54321",
        "SECRET_KEY": "sb_secret_local",
      })
    )

    credentials = get_local_credentials()

    self.assertEqual(
      credentials,
      ("http://127.0.0.1:54321", "sb_secret_local"),
    )
    command = mocked_run.call_args.args[0]
    self.assertIn("supabase@2.110.0", command)
    self.assertIn("--agent", command)

  @patch("scripts.load_supabase.upsert_persistence_bundle")
  @patch("scripts.load_supabase.get_local_credentials")
  def test_applies_to_local_instance_without_environment_variables(
    self,
    mocked_credentials,
    mocked_upsert,
  ):
    mocked_credentials.return_value = (
      "http://127.0.0.1:54321",
      "sb_secret_local",
    )
    mocked_upsert.return_value = {"tables": [], "totalRows": 325}

    with patch("builtins.print") as mocked_print:
      exit_code = main(["--local", "--apply"])

    self.assertEqual(exit_code, 0)
    self.assertEqual(
      mocked_upsert.call_args.kwargs["supabase_url"],
      "http://127.0.0.1:54321",
    )
    self.assertEqual(
      mocked_upsert.call_args.kwargs["secret_key"],
      "sb_secret_local",
    )
    output = mocked_print.call_args.args[0]
    self.assertIn('"target": "local"', output)
    self.assertNotIn("sb_secret_local", output)


if __name__ == "__main__":
  unittest.main()
