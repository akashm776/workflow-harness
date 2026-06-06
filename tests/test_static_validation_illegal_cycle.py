from __future__ import annotations

import json
from pathlib import Path
import unittest

from compiler.static_validation import validate_illegal_graph_cycle


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
INVALID_FIXTURE = ROOT / "fixtures" / "invalid" / "illegal-cycle"


class IllegalCycleValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass_illegal_cycle_validation(self) -> None:
        for fixture_name in VALID_FIXTURES:
            workflow_spec_path = ROOT / "fixtures" / "valid" / fixture_name / "input" / "WorkflowSpec.json"
            result = validate_illegal_graph_cycle(workflow_spec_path)

            with self.subTest(fixture=fixture_name):
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def test_invalid_fixture_fails_illegal_cycle_validation(self) -> None:
        expected = json.loads(
            (INVALID_FIXTURE / "expected" / "error.json").read_text(encoding="utf-8")
        )
        result = validate_illegal_graph_cycle(INVALID_FIXTURE / "input" / "WorkflowSpec.json")

        self.assertFalse(result["ok"])
        self.assertIsNotNone(result["diagnostic"])
        self.assertEqual(result["diagnostic"]["error_code"], expected["expected_error_code"])
        self.assertEqual(result["diagnostic"]["component"], expected["expected_component"])
        self.assertEqual(result["diagnostic"]["artifact"], expected["expected_artifact"])
        self.assertIn(expected["expected_message_fragment"], result["diagnostic"]["message"])


if __name__ == "__main__":
    unittest.main()
