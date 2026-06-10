from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from compiler.static_validation import (
    validate_static_inputs,
    validate_unsupported_approval_identity_claims,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

UNSUPPORTED_APPROVAL_IDENTITY_CLAIM_KEYS = (
    "approval_id",
    "approval_decision_id",
    "approval_proof",
    "approval_receipt",
    "approval_certificate",
    "approval_signature",
    "operator_signature",
    "approved_by_operator",
    "operator_approved",
    "approval_subject_override",
    "approval_subject_identity",
    "approval_subject_ref",
    "approval_subject_digest_override",
    "approval_run_id",
    "approval_request_id",
    "approval_scope_id",
    "run_approval_id",
    "request_approval_id",
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class UnsupportedApprovalIdentityClaimValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            for artifact_name in (
                "WorkflowSpec.json",
                "RequestedAuth.json",
                "ApprovalRequests.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=artifact_name):
                    result = validate_unsupported_approval_identity_claims(
                        fixture_input / artifact_name,
                        artifact_name,
                    )
                    self.assertTrue(result["ok"])
                    self.assertIsNone(result["diagnostic"])

    def test_workflow_spec_each_unsupported_key_is_rejected(self) -> None:
        for key in UNSUPPORTED_APPROVAL_IDENTITY_CLAIM_KEYS:
            with self.subTest(key=key):
                with tempfile.TemporaryDirectory() as tmp:
                    workflow_spec = _load_json(
                        SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json"
                    )
                    workflow_spec["nodes"][0][key] = "example-identity"
                    path = _write_json(
                        Path(tmp) / "WorkflowSpec.json", workflow_spec
                    )

                    result = validate_unsupported_approval_identity_claims(
                        path,
                        "WorkflowSpec.json",
                    )

                self.assertFalse(result["ok"])
                diagnostic = result["diagnostic"]
                self.assertEqual(
                    diagnostic["error_code"], "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM"
                )
                self.assertEqual(
                    diagnostic["component"], "approval_identity_validator"
                )
                self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
                self.assertIn(f"$.nodes[0].{key}", diagnostic["message"])

    def test_workflow_spec_approval_id_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["approval_id"] = "example-approval-id"
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_approval_identity_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("$.nodes[0].approval_id", diagnostic["message"])
        self.assertTrue(
            diagnostic["message"].startswith(
                "unsupported approval-identity claim in WorkflowSpec.json; "
                "operator approval identity, proof, receipt, signature, and "
                "subject/run/request identifiers are operator-owned and must "
                "not be supplied, spoofed, or overridden by planner-controlled "
                "artifacts: "
            )
        )

    def test_workflow_spec_approval_subject_override_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["approval_subject_override"] = {
                "display_only": True
            }
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_approval_identity_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("$.nodes[0].approval_subject_override", diagnostic["message"])

    def test_requested_auth_approval_receipt_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            requested_auth["approval_receipt"] = {"display_only": True}
            path = _write_json(Path(tmp) / "RequestedAuth.json", requested_auth)

            result = validate_unsupported_approval_identity_claims(
                path,
                "RequestedAuth.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.approval_receipt", diagnostic["message"])

    def test_approval_token_is_owned_by_approval_binding(self) -> None:
        # approval_token is owned by the approval-binding validator and must not
        # be claimed by this validator; this validator leaves it alone.
        with tempfile.TemporaryDirectory() as tmp:
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            requested_auth["approval_token"] = "example-token"
            path = _write_json(Path(tmp) / "RequestedAuth.json", requested_auth)

            result = validate_unsupported_approval_identity_claims(
                path,
                "RequestedAuth.json",
            )

        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_approval_requests_approval_run_id_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["requests"][0]["approval_run_id"] = "example-run"
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_approval_identity_claims(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.requests[0].approval_run_id", diagnostic["message"])

    def test_approval_requests_approval_request_id_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["approval_request_id"] = "example-request"
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_approval_identity_claims(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.approval_request_id", diagnostic["message"])

    def test_approval_requests_approval_subject_digest_override_key_is_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["requests"][0]["approval_subject_digest_override"] = (
                "example-digest"
            )
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_approval_identity_claims(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn(
            "$.requests[0].approval_subject_digest_override", diagnostic["message"]
        )

    def test_benign_string_mentioning_approval_id_is_not_rejected(self) -> None:
        # The words appear only inside a string value, not as object keys.
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["display_name"] = (
                "Explain approval_id and operator_signature policy"
            )
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_approval_identity_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_aggregate_static_validation_surfaces_approval_identity_rejection(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["approval_receipt"] = {"display_only": True}

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
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM"
        )
        self.assertEqual(diagnostic["component"], "approval_identity_validator")
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.approval_receipt", diagnostic["message"])

    def test_approval_decisions_approval_identity_keys_not_rejected_by_this_validator(
        self,
    ) -> None:
        # ApprovalDecisions.json is operator-authored, not a planner proposal;
        # this validator does not scan it, and approval-identity-like fields
        # there pass aggregate static validation.
        with tempfile.TemporaryDirectory() as tmp:
            fixture_input = (
                ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
            )
            approval_decisions_src = fixture_input / "ApprovalDecisions.json"
            if not approval_decisions_src.exists():
                self.skipTest("no ApprovalDecisions.json fixture available")

            approval_decisions = _load_json(approval_decisions_src)
            approval_decisions["approval_id"] = "operator-owned-approval-id"
            approval_decisions["operator_signature"] = "operator-owned-signature"
            approval_decisions_path = _write_json(
                Path(tmp) / "ApprovalDecisions.json", approval_decisions
            )

            result = validate_static_inputs(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "NodeTypeRegistry.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "ApprovalRequests.json",
                approval_decisions_path=approval_decisions_path,
            )

        self.assertTrue(result["ok"])
        self.assertEqual(result["diagnostics"], [])


if __name__ == "__main__":
    unittest.main()
