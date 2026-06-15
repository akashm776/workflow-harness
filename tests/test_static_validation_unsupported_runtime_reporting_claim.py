from __future__ import annotations

import json
from pathlib import Path
from tests.test_temp_utils import temporary_test_directory
import unittest

from compiler.static_validation import (
    validate_static_inputs,
    validate_unsupported_runtime_reporting_claims,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

UNSUPPORTED_RUNTIME_REPORTING_CLAIM_KEYS = (
    "verifier_result",
    "broker_request",
    "broker_decision",
    "broker_result",
    "broker_boundary",
    "sandbox_attestation",
    "sandbox_status",
    "runtime_authority",
    "broker_authority",
    "verifier_authority",
    "evidence_authority",
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class UnsupportedRuntimeReportingClaimValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            for artifact_name in (
                "WorkflowSpec.json",
                "RequestedAuth.json",
                "ApprovalRequests.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=artifact_name):
                    result = validate_unsupported_runtime_reporting_claims(
                        fixture_input / artifact_name,
                        artifact_name,
                    )
                    self.assertTrue(result["ok"])
                    self.assertIsNone(result["diagnostic"])

    def test_workflow_spec_each_unsupported_key_is_rejected(self) -> None:
        for key in UNSUPPORTED_RUNTIME_REPORTING_CLAIM_KEYS:
            with self.subTest(key=key):
                with temporary_test_directory('static-validation-unsupported-runtime-reporting-claim-tests') as tmp:
                    workflow_spec = _load_json(
                        SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json"
                    )
                    workflow_spec["nodes"][0][key] = {"display_only": True}
                    path = _write_json(
                        Path(tmp) / "WorkflowSpec.json", workflow_spec
                    )

                    result = validate_unsupported_runtime_reporting_claims(
                        path,
                        "WorkflowSpec.json",
                    )

                self.assertFalse(result["ok"])
                diagnostic = result["diagnostic"]
                self.assertEqual(
                    diagnostic["error_code"], "UNSUPPORTED_RUNTIME_REPORTING_CLAIM"
                )
                self.assertEqual(
                    diagnostic["component"], "runtime_reporting_boundary_validator"
                )
                self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
                self.assertIn(f"$.nodes[0].{key}", diagnostic["message"])

    def test_workflow_spec_broker_request_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-runtime-reporting-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["broker_request"] = {"display_only": True}
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_runtime_reporting_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_RUNTIME_REPORTING_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("$.nodes[0].broker_request", diagnostic["message"])
        self.assertTrue(
            diagnostic["message"].startswith(
                "unsupported runtime-reporting/broker claim in "
                "WorkflowSpec.json; evidence/verifier/broker/sandbox reporting "
                "and broker artifacts are not planner-authoritative and are not "
                "V1 control-plane inputs: "
            )
        )

    def test_requested_auth_broker_decision_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-runtime-reporting-claim-tests') as tmp:
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            requested_auth["broker_decision"] = {"display_only": True}
            path = _write_json(Path(tmp) / "RequestedAuth.json", requested_auth)

            result = validate_unsupported_runtime_reporting_claims(
                path,
                "RequestedAuth.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_RUNTIME_REPORTING_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.broker_decision", diagnostic["message"])

    def test_approval_requests_broker_result_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-runtime-reporting-claim-tests') as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["requests"][0]["broker_result"] = {
                "display_only": True
            }
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_runtime_reporting_claims(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_RUNTIME_REPORTING_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.requests[0].broker_result", diagnostic["message"])

    def test_approval_requests_sandbox_attestation_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-runtime-reporting-claim-tests') as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["sandbox_attestation"] = {"display_only": True}
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_runtime_reporting_claims(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_RUNTIME_REPORTING_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.sandbox_attestation", diagnostic["message"])

    def test_benign_string_mentioning_broker_request_is_not_rejected(self) -> None:
        # The words appear only inside a string value, not as object keys.
        with temporary_test_directory('static-validation-unsupported-runtime-reporting-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["display_name"] = (
                "Explain broker_request and sandbox_status policy"
            )
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_runtime_reporting_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_aggregate_static_validation_surfaces_runtime_reporting_rejection(
        self,
    ) -> None:
        with temporary_test_directory('static-validation-unsupported-runtime-reporting-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["broker_request"] = {"display_only": True}

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
            diagnostic["error_code"], "UNSUPPORTED_RUNTIME_REPORTING_CLAIM"
        )
        self.assertEqual(
            diagnostic["component"], "runtime_reporting_boundary_validator"
        )
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.broker_request", diagnostic["message"])

    def test_approval_decisions_broker_result_is_not_rejected_by_this_validator(
        self,
    ) -> None:
        # ApprovalDecisions.json is operator-authored, not a planner proposal;
        # this validator does not scan it, and a broker_result-like field there
        # passes aggregate static validation (no validator rejects it).
        with temporary_test_directory('static-validation-unsupported-runtime-reporting-claim-tests') as tmp:
            fixture_input = (
                ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
            )
            approval_decisions_src = fixture_input / "ApprovalDecisions.json"
            if not approval_decisions_src.exists():
                self.skipTest("no ApprovalDecisions.json fixture available")

            approval_decisions = _load_json(approval_decisions_src)
            approval_decisions["broker_result"] = {"display_only": True}
            approval_decisions["sandbox_attestation"] = {"display_only": True}
            approval_decisions_path = _write_json(
                Path(tmp) / "ApprovalDecisions.json", approval_decisions
            )

            # The dedicated validator is never called for ApprovalDecisions; the
            # aggregate run with the modified ApprovalDecisions stays green.
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
