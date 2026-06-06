from __future__ import annotations

import json
from pathlib import Path
import unittest

from compiler.static_validation import validate_missing_required_scope


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
INVALID_FIXTURE = ROOT / "fixtures" / "invalid" / "missing-scope"


class MissingScopeValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass_missing_scope_validation(self) -> None:
        for fixture_name in VALID_FIXTURES:
            requested_auth_path = (
                ROOT / "fixtures" / "valid" / fixture_name / "input" / "RequestedAuth.json"
            )
            result = validate_missing_required_scope(requested_auth_path)

            with self.subTest(fixture=fixture_name):
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def test_invalid_fixture_fails_missing_scope_validation(self) -> None:
        expected = json.loads(
            (INVALID_FIXTURE / "expected" / "error.json").read_text(encoding="utf-8")
        )
        result = validate_missing_required_scope(
            INVALID_FIXTURE / "input" / "RequestedAuth.json"
        )

        self.assertFalse(result["ok"])
        self.assertIsNotNone(result["diagnostic"])
        self.assertEqual(result["diagnostic"]["error_code"], expected["expected_error_code"])
        self.assertEqual(result["diagnostic"]["component"], expected["expected_component"])
        self.assertEqual(result["diagnostic"]["artifact"], expected["expected_artifact"])
        self.assertIn(
            expected["expected_message_fragment"],
            result["diagnostic"]["message"],
        )

    def test_blank_string_scope_fails_missing_scope_validation(self) -> None:
        result = validate_missing_required_scope(
            INVALID_FIXTURE / "input" / "RequestedAuth-blank-scope.json"
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["diagnostic"]["error_code"], "MISSING_REQUIRED_SCOPE")
        self.assertEqual(result["diagnostic"]["component"], "scope_validator")
        self.assertEqual(result["diagnostic"]["artifact"], "RequestedAuth.json")
        self.assertIn("missing required scope", result["diagnostic"]["message"])


if __name__ == "__main__":
    unittest.main()
