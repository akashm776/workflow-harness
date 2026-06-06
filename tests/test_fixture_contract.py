from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"


class FixtureContractTests(unittest.TestCase):
    def test_valid_fixtures_have_input_and_expected_directories(self) -> None:
        valid_root = FIXTURES / "valid"
        for fixture_dir in valid_root.iterdir():
            if not fixture_dir.is_dir():
                continue
            self.assertTrue((fixture_dir / "input").is_dir(), fixture_dir.name)
            self.assertTrue((fixture_dir / "expected").is_dir(), fixture_dir.name)

    def test_invalid_fixtures_have_input_and_expected_error_json(self) -> None:
        invalid_root = FIXTURES / "invalid"
        for fixture_dir in invalid_root.iterdir():
            if not fixture_dir.is_dir():
                continue
            self.assertTrue((fixture_dir / "input").is_dir(), fixture_dir.name)
            error_path = fixture_dir / "expected" / "error.json"
            self.assertTrue(error_path.is_file(), fixture_dir.name)
            payload = json.loads(error_path.read_text(encoding="utf-8"))
            self.assertIn("expected_error_code", payload)
            self.assertIn("expected_component", payload)
            self.assertIn("expected_artifact", payload)
            self.assertIn("expected_message_fragment", payload)


if __name__ == "__main__":
    unittest.main()
