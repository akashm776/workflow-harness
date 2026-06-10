from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from compiler.static_validation import (
    validate_static_inputs,
    validate_unsupported_secret_fields,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class UnsupportedSecretFieldValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            for artifact_name in (
                "WorkflowSpec.json",
                "RequestedAuth.json",
                "ApprovalRequests.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=artifact_name):
                    result = validate_unsupported_secret_fields(
                        fixture_input / artifact_name,
                        artifact_name,
                    )
                    self.assertTrue(result["ok"])
                    self.assertIsNone(result["diagnostic"])

    def test_workflow_spec_nested_secret_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["metadata"] = {"secret": "forbidden"}
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_secret_fields(
                path,
                "WorkflowSpec.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_SECRET_FIELD")
        self.assertEqual(diagnostic["component"], "secret_field_validator")
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("$.nodes[0].metadata.secret", diagnostic["message"])
        self.assertTrue(
            diagnostic["message"].startswith(
                "unsupported secret-bearing field in WorkflowSpec.json; "
                "V1 safe no-op does not accept planner-supplied tokens, secrets, "
                "passwords, API keys, private keys, or credentials: "
            )
        )

    def test_requested_auth_credentials_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            requested_auth["credentials"] = {"mode": "forbidden"}
            path = _write_json(Path(tmp) / "RequestedAuth.json", requested_auth)

            result = validate_unsupported_secret_fields(
                path,
                "RequestedAuth.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_SECRET_FIELD")
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.credentials", diagnostic["message"])

    def test_approval_requests_api_keys_field_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["requests"][0]["api_keys"] = ["forbidden"]
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_secret_fields(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_SECRET_FIELD")
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.requests[0].api_keys", diagnostic["message"])

    def test_benign_string_mentioning_secret_is_not_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["display_name"] = "Review secret field policy"
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_secret_fields(
                path,
                "WorkflowSpec.json",
            )

        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_aggregate_static_validation_surfaces_secret_field_rejection(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["credentials"] = {"mode": "forbidden"}

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(len(result["diagnostics"]), 1)
        diagnostic = result["diagnostics"][0]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_SECRET_FIELD")
        self.assertEqual(diagnostic["component"], "secret_field_validator")
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.credentials", diagnostic["message"])


if __name__ == "__main__":
    unittest.main()
