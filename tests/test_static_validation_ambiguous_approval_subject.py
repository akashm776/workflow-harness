from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from compiler.static_validation import validate_ambiguous_approval_subjects


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
INVALID_FIXTURE = ROOT / "fixtures" / "invalid" / "ambiguous-approval-subject"


class AmbiguousApprovalSubjectValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass_ambiguous_approval_subject_validation(self) -> None:
        for fixture_name in VALID_FIXTURES:
            approval_requests_path = (
                ROOT / "fixtures" / "valid" / fixture_name / "input" / "ApprovalRequests.json"
            )
            result = validate_ambiguous_approval_subjects(approval_requests_path)

            with self.subTest(fixture=fixture_name):
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def test_invalid_fixture_fails_ambiguous_approval_subject_validation(self) -> None:
        expected = json.loads(
            (INVALID_FIXTURE / "expected" / "error.json").read_text(encoding="utf-8")
        )
        result = validate_ambiguous_approval_subjects(
            INVALID_FIXTURE / "input" / "ApprovalRequests.json"
        )

        self.assertFalse(result["ok"])
        self.assertIsNotNone(result["diagnostic"])
        self.assertEqual(result["diagnostic"]["error_code"], expected["expected_error_code"])
        self.assertEqual(result["diagnostic"]["component"], expected["expected_component"])
        self.assertEqual(result["diagnostic"]["artifact"], expected["expected_artifact"])
        self.assertIn(expected["expected_message_fragment"], result["diagnostic"]["message"])

    def test_duplicate_same_node_and_subject_with_different_request_ids_fails(self) -> None:
        payload = {
            "schema_version": "m1",
            "workflow_revision_id": "workflow-rev-ambiguous-approval-002",
            "artifact_lifecycle_state": "approval_pending",
            "requests": [
                {
                    "request_id": "approval-request-duplicate-001",
                    "node_id": "execute-1",
                    "approval_subject_hash": "approval-subject-duplicate-001",
                },
                {
                    "request_id": "approval-request-duplicate-002",
                    "node_id": "execute-1",
                    "approval_subject_hash": "approval-subject-duplicate-001",
                },
            ],
        }

        with patch("compiler.static_validation._load_json", return_value=payload):
            result = validate_ambiguous_approval_subjects("ignored.json")

        self.assertFalse(result["ok"])
        self.assertEqual(result["diagnostic"]["error_code"], "AMBIGUOUS_APPROVAL_SUBJECT")
        self.assertEqual(result["diagnostic"]["component"], "approval_validator")
        self.assertEqual(result["diagnostic"]["artifact"], "ApprovalRequests.json")
        self.assertIn("ambiguous approval subject", result["diagnostic"]["message"])


if __name__ == "__main__":
    unittest.main()
