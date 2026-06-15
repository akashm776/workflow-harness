from __future__ import annotations

import json
from pathlib import Path
from tests.test_temp_utils import temporary_test_directory
import unittest

from compiler.static_validation import (
    validate_static_inputs,
    validate_unsupported_approval_scope_claims,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

UNSUPPORTED_APPROVAL_SCOPE_CLAIM_KEYS = (
    "approval_reuse",
    "persistent_approval",
    "global_approval",
    "cross_run_approval",
    "prior_run_approval",
    "inherited_approval",
    "approval_inheritance",
    "approval_subsumption",
    "approval_valid_for_future_runs",
    "approval_valid_across_requests",
    "approval_valid_across_runs",
    "approval_expires_never",
    "approval_scope_override",
    "request_scope_override",
    "run_scope_override",
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class UnsupportedApprovalScopeClaimValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            for artifact_name in (
                "WorkflowSpec.json",
                "RequestedAuth.json",
                "ApprovalRequests.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=artifact_name):
                    result = validate_unsupported_approval_scope_claims(
                        fixture_input / artifact_name,
                        artifact_name,
                    )
                    self.assertTrue(result["ok"])
                    self.assertIsNone(result["diagnostic"])

    def test_workflow_spec_each_unsupported_key_is_rejected(self) -> None:
        for key in UNSUPPORTED_APPROVAL_SCOPE_CLAIM_KEYS:
            with self.subTest(key=key):
                with temporary_test_directory('static-validation-unsupported-approval-scope-claim-tests') as tmp:
                    workflow_spec = _load_json(
                        SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json"
                    )
                    workflow_spec["nodes"][0][key] = {"display_only": True}
                    path = _write_json(
                        Path(tmp) / "WorkflowSpec.json", workflow_spec
                    )

                    result = validate_unsupported_approval_scope_claims(
                        path,
                        "WorkflowSpec.json",
                    )

                self.assertFalse(result["ok"])
                diagnostic = result["diagnostic"]
                self.assertEqual(
                    diagnostic["error_code"], "UNSUPPORTED_APPROVAL_SCOPE_CLAIM"
                )
                self.assertEqual(
                    diagnostic["component"], "approval_scope_validator"
                )
                self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
                self.assertIn(f"$.nodes[0].{key}", diagnostic["message"])

    def test_workflow_spec_approval_carryover_is_owned_by_approval_binding(
        self,
    ) -> None:
        # approval_carryover is owned by the approval-binding validator and must
        # not be claimed by this validator; this validator leaves it alone.
        with temporary_test_directory('static-validation-unsupported-approval-scope-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["approval_carryover"] = {"display_only": True}
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_approval_scope_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_workflow_spec_cross_run_approval_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-approval-scope-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["cross_run_approval"] = {"display_only": True}
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_approval_scope_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_SCOPE_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("$.nodes[0].cross_run_approval", diagnostic["message"])
        self.assertTrue(
            diagnostic["message"].startswith(
                "unsupported approval-scope claim in WorkflowSpec.json; "
                "operator approval is explicit, operator-owned, and "
                "current-run/request scoped, and planner-controlled artifacts "
                "must not claim reusable, persistent, global, inherited, or "
                "cross-run/cross-request approval: "
            )
        )

    def test_requested_auth_global_approval_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-approval-scope-claim-tests') as tmp:
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            requested_auth["global_approval"] = {"display_only": True}
            path = _write_json(Path(tmp) / "RequestedAuth.json", requested_auth)

            result = validate_unsupported_approval_scope_claims(
                path,
                "RequestedAuth.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_SCOPE_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.global_approval", diagnostic["message"])

    def test_approval_requests_approval_valid_across_runs_key_is_rejected(
        self,
    ) -> None:
        with temporary_test_directory('static-validation-unsupported-approval-scope-claim-tests') as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["requests"][0]["approval_valid_across_runs"] = True
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_approval_scope_claims(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_SCOPE_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn(
            "$.requests[0].approval_valid_across_runs", diagnostic["message"]
        )

    def test_approval_requests_approval_scope_override_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-approval-scope-claim-tests') as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["approval_scope_override"] = {"display_only": True}
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_approval_scope_claims(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_SCOPE_CLAIM"
        )
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.approval_scope_override", diagnostic["message"])

    def test_benign_string_mentioning_global_approval_is_not_rejected(self) -> None:
        # The words appear only inside a string value, not as object keys.
        with temporary_test_directory('static-validation-unsupported-approval-scope-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["display_name"] = (
                "Explain global_approval and cross_run_approval policy"
            )
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_approval_scope_claims(
                path,
                "WorkflowSpec.json",
            )

        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_aggregate_static_validation_surfaces_approval_scope_rejection(
        self,
    ) -> None:
        with temporary_test_directory('static-validation-unsupported-approval-scope-claim-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["global_approval"] = {"display_only": True}

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
            diagnostic["error_code"], "UNSUPPORTED_APPROVAL_SCOPE_CLAIM"
        )
        self.assertEqual(diagnostic["component"], "approval_scope_validator")
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.global_approval", diagnostic["message"])

    def test_approval_decisions_approval_scope_keys_not_rejected_by_this_validator(
        self,
    ) -> None:
        # ApprovalDecisions.json is operator-authored, not a planner proposal;
        # this validator does not scan it, and approval-scope-like fields there
        # pass aggregate static validation.
        with temporary_test_directory('static-validation-unsupported-approval-scope-claim-tests') as tmp:
            fixture_input = (
                ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
            )
            approval_decisions_src = fixture_input / "ApprovalDecisions.json"
            if not approval_decisions_src.exists():
                self.skipTest("no ApprovalDecisions.json fixture available")

            approval_decisions = _load_json(approval_decisions_src)
            approval_decisions["approval_valid_across_runs"] = True
            approval_decisions["approval_scope_override"] = {"display_only": True}
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
