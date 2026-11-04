import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
COLLECTORS = ROOT / "scripts" / "collectors"
sys.path.insert(0, str(COLLECTORS))

import collect_nasa


class NasaRunnerSafetyTests(unittest.TestCase):
    def test_live_collection_is_blocked_without_explicit_flag(self):
        with patch.object(sys, "argv", ["collect_nasa.py"]):
            self.assertEqual(collect_nasa.main(), 2)

    def test_invalid_page_size_is_rejected_before_network(self):
        with patch.object(sys, "argv", ["collect_nasa.py", "--allow-network", "--page-size", "101"]):
            with patch.object(collect_nasa, "reserve_rate_limit") as reserve:
                self.assertEqual(collect_nasa.main(), 2)
                reserve.assert_not_called()

    def test_rate_limit_must_be_reserved_before_nasa_fetch(self):
        events = []

        def reserve():
            events.append("rate_limit")

        def fetch(query, page_size):
            events.append("nasa")
            return {"collection": {"items": []}}

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "nasa_nail.json"
            with patch.object(collect_nasa, "OUTPUT", output):
                with patch.object(collect_nasa, "reserve_rate_limit", side_effect=reserve):
                    with patch.object(collect_nasa, "fetch_nasa_page", side_effect=fetch):
                        collect_nasa.collect("earth", 5)

        self.assertEqual(events, ["rate_limit", "nasa"])
        self.assertTrue(output.exists())

    def test_missing_rate_limit_configuration_blocks(self):
        with patch.dict(os.environ, {"TVBRASIL_RATE_LIMIT_URL": "", "RATE_LIMIT_ADMIN_TOKEN": ""}):
            with self.assertRaises(collect_nasa.CollectionBlocked):
                collect_nasa.reserve_rate_limit()


if __name__ == "__main__":
    unittest.main()
