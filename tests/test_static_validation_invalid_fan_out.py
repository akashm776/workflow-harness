from __future__ import annotations

import json
from pathlib import Path
import unittest

from compiler.static_validation import validate_invalid_fan_out


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
INVALID_FIXTURE = ROOT / "fixtures" / "invalid" / "invalid-fan-out"


class InvalidFanOutValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass_invalid_fan_out_validation(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            result = validate_invalid_fan_out(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "NodeTypeRegistry.json",
            )

            with self.subTest(fixture=fixture_name):
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def test_invalid_fixture_fails_invalid_fan_out_validation(self) -> None:
        expected = json.loads(
            (INVALID_FIXTURE / "expected" / "error.json").read_text(encoding="utf-8")
        )
        result = validate_invalid_fan_out(
            INVALID_FIXTURE / "input" / "WorkflowSpec.json",
            INVALID_FIXTURE / "input" / "NodeTypeRegistry.json",
        )

        self.assertFalse(result["ok"])
        self.assertIsNotNone(result["diagnostic"])
        self.assertEqual(result["diagnostic"]["error_code"], expected["expected_error_code"])
        self.assertEqual(result["diagnostic"]["component"], expected["expected_component"])
        self.assertEqual(result["diagnostic"]["artifact"], expected["expected_artifact"])
        self.assertIn(expected["expected_message_fragment"], result["diagnostic"]["message"])


if __name__ == "__main__":
    unittest.main()
