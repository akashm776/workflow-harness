from __future__ import annotations

import json
from pathlib import Path
from tests.test_temp_utils import temporary_test_directory
import unittest

from compiler.static_validation import (
    validate_static_inputs,
    validate_unsupported_audit_evidence_authority_claims,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM_KEYS = (
    "audit_authority",
    "audit_approval",
    "audit_grant",
    "audit_override",
    "audit_decision",
    "audit_authorizes",
    "audit_approved_by",
    "audit_satisfies_approval",
    "audit_satisfies_authority",
    "audit_override_diagnostics",
    "evidence_approval",
    "evidence_grant",
    "evidence_override",
    "evidence_decision",
    "evidence_authorizes",
    "evidence_approved_by",
    "evidence_satisfies_approval",
    "evidence_satisfies_authority",
    "evidence_override_diagnostics",
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class UnsupportedAuditEvidenceAuthorityClaimValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            for artifact_name in (
                "WorkflowSpec.json",
                "RequestedAuth.json",
                "ApprovalRequests.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=artifact_name):
                    result = validate_unsupported_audit_evidence_authority_claims(
                        fixture_input / artifact_name,
                        artifact_name,
                    )
                    self.assertTrue(result["ok"])
                    self.assertIsNone(result["diagnostic"])

    def test_workflow_spec_each_unsupported_key_is_rejected(self) -> None:
        for key in UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM_KEYS:
            with self.subTest(key=key):
                with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
                    workflow_spec = _load_json(
                        SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json"
                    )
                    workflow_spec["nodes"][0][key] = {"display_only": True}
                    path = _write_json(
                        Path(tmp) / "WorkflowSpec.json", workflow_spec
                    )

                    result = validate_unsupported_audit_evidence_authority_claims(
                        path,
                        "WorkflowSpec.json",
                    )

                self.assertFalse(result["ok"])
                diagnostic = result["diagnostic"]
                self.assertEqual(
                    diagnostic["error_code"],
                    "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
                )
                self.assertEqual(
                    diagnostic["component"], "audit_evidence_authority_validator"
                )
                self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
                self.assertIn(f"$.nodes[0].{key}", diagnostic["message"])

    def test_workflow_spec_evidence_approval_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["evidence_approval"] = {"display_only": True}
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_audit_evidence_authority_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("$.nodes[0].evidence_approval", diagnostic["message"])

    def test_workflow_spec_audit_override_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["audit_override"] = {"display_only": True}
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_audit_evidence_authority_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("$.nodes[0].audit_override", diagnostic["message"])
        self.assertTrue(
            diagnostic["message"].startswith(
                "unsupported audit/evidence authority claim in "
                "WorkflowSpec.json; audit and evidence records are reporting "
                "material only and cannot approve, authorize, grant "
                "capabilities, override diagnostics, satisfy approval, or "
                "create authority in planner-controlled artifacts: "
            )
        )

    def test_requested_auth_audit_grant_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            requested_auth["audit_grant"] = {"display_only": True}
            path = _write_json(Path(tmp) / "RequestedAuth.json", requested_auth)

            result = validate_unsupported_audit_evidence_authority_claims(
                path,
                "RequestedAuth.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.audit_grant", diagnostic["message"])

    def test_requested_auth_evidence_authorizes_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            requested_auth["evidence_authorizes"] = {"display_only": True}
            path = _write_json(Path(tmp) / "RequestedAuth.json", requested_auth)

            result = validate_unsupported_audit_evidence_authority_claims(
                path,
                "RequestedAuth.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.evidence_authorizes", diagnostic["message"])

    def test_approval_requests_evidence_satisfies_approval_key_is_rejected(
        self,
    ) -> None:
        with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["requests"][0]["evidence_satisfies_approval"] = True
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_audit_evidence_authority_claims(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn(
            "$.requests[0].evidence_satisfies_approval", diagnostic["message"]
        )

    def test_approval_requests_audit_satisfies_authority_key_is_rejected(
        self,
    ) -> None:
        with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["audit_satisfies_authority"] = {"display_only": True}
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_audit_evidence_authority_claims(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.audit_satisfies_authority", diagnostic["message"])

    def test_benign_string_mentioning_audit_approval_is_not_rejected(self) -> None:
        # The words appear only inside a string value, not as object keys.
        with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["display_name"] = (
                "Explain audit_approval and evidence_override policy"
            )
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_audit_evidence_authority_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_aggregate_static_validation_surfaces_audit_evidence_rejection(
        self,
    ) -> None:
        with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["evidence_grant"] = {"display_only": True}

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
            diagnostic["error_code"], "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM"
        )
        self.assertEqual(
            diagnostic["component"], "audit_evidence_authority_validator"
        )
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.evidence_grant", diagnostic["message"])

    def test_approval_decisions_audit_evidence_keys_not_rejected_by_this_validator(
        self,
    ) -> None:
        # ApprovalDecisions.json is operator-authored, not a planner proposal;
        # this validator does not scan it, and audit/evidence-authority-like
        # fields there pass aggregate static validation.
        with temporary_test_directory('static-validation-unsupported-audit-evidence-authority-claim-tests') as tmp:
            fixture_input = (
                ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
            )
            approval_decisions_src = fixture_input / "ApprovalDecisions.json"
            if not approval_decisions_src.exists():
                self.skipTest("no ApprovalDecisions.json fixture available")

            approval_decisions = _load_json(approval_decisions_src)
            approval_decisions["evidence_approval"] = {"display_only": True}
            approval_decisions["audit_satisfies_authority"] = {"display_only": True}
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
