from __future__ import annotations

import json
from pathlib import Path
from tests.test_temp_utils import temporary_test_directory
import unittest

from compiler.static_validation import (
    validate_static_inputs,
    validate_unsupported_approval_bindings,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

UNSUPPORTED_APPROVAL_BINDING_KEYS = (
    "approval_binding",
    "approval_bindings",
    "approval_token",
    "approval_tokens",
    "approval_carryover",
    "reusable_approval",
    "reusable_approvals",
    "standing_approval",
    "standing_approvals",
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class UnsupportedApprovalBindingValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            for artifact_name in (
                "WorkflowSpec.json",
                "RequestedAuth.json",
                "ApprovalRequests.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=artifact_name):
                    result = validate_unsupported_approval_bindings(
                        fixture_input / artifact_name,
                        artifact_name,
                    )
                    self.assertTrue(result["ok"])
                    self.assertIsNone(result["diagnostic"])

    def test_workflow_spec_each_unsupported_key_is_rejected(self) -> None:
        for key in UNSUPPORTED_APPROVAL_BINDING_KEYS:
            with self.subTest(key=key):
                with temporary_test_directory('static-validation-unsupported-approval-binding-tests') as tmp:
                    workflow_spec = _load_json(
                        SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json"
                    )
                    workflow_spec["nodes"][0][key] = {"display_only": True}
                    path = _write_json(
                        Path(tmp) / "WorkflowSpec.json", workflow_spec
                    )

                    result = validate_unsupported_approval_bindings(
                        path,
                        "WorkflowSpec.json",
                    )

                self.assertFalse(result["ok"])
                diagnostic = result["diagnostic"]
                self.assertEqual(
                    diagnostic["error_code"], "UNSUPPORTED_APPROVAL_BINDING"
                )
                self.assertEqual(
                    diagnostic["component"], "approval_binding_validator"
                )
                self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
                self.assertIn(f"$.nodes[0].{key}", diagnostic["message"])
                self.assertTrue(
                    diagnostic["message"].startswith(
                        "unsupported approval-binding field in "
                        "WorkflowSpec.json; V1 safe no-op does not accept "
                        "planner-supplied approval bindings, approval tokens, "
                        "approval carryover, reusable approvals, or standing "
                        "approvals; approvals remain explicit, operator-owned, "
                        "and current-run/request scoped: "
                    )
                )

    def test_requested_auth_reusable_approval_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-approval-binding-tests') as tmp:
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            requested_auth["reusable_approvals"] = [{"display_only": True}]
            path = _write_json(Path(tmp) / "RequestedAuth.json", requested_auth)

            result = validate_unsupported_approval_bindings(
                path,
                "RequestedAuth.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_APPROVAL_BINDING")
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.reusable_approvals", diagnostic["message"])

    def test_approval_requests_standing_approval_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-approval-binding-tests') as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["requests"][0]["standing_approval"] = True
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_approval_bindings(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_APPROVAL_BINDING")
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.requests[0].standing_approval", diagnostic["message"])

    def test_approval_requests_approval_carryover_key_is_rejected(self) -> None:
        with temporary_test_directory('static-validation-unsupported-approval-binding-tests') as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["approval_carryover"] = {"display_only": True}
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_approval_bindings(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_APPROVAL_BINDING")
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.approval_carryover", diagnostic["message"])

    def test_benign_string_mentioning_reusable_approval_is_not_rejected(
        self,
    ) -> None:
        # The words appear only inside a string value, not as object keys.
        with temporary_test_directory('static-validation-unsupported-approval-binding-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["display_name"] = (
                "Explain reusable_approval and standing_approval policy"
            )
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_approval_bindings(
                path,
                "WorkflowSpec.json",
            )

        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_aggregate_static_validation_surfaces_approval_binding_rejection(
        self,
    ) -> None:
        with temporary_test_directory('static-validation-unsupported-approval-binding-tests') as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["approval_binding"] = {"display_only": True}

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
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_APPROVAL_BINDING")
        self.assertEqual(diagnostic["component"], "approval_binding_validator")
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.approval_binding", diagnostic["message"])

    def test_valid_approval_required_fixture_passes_aggregate_validation(
        self,
    ) -> None:
        # Approval resolution inputs without binding-claim keys remain valid;
        # this guard does not change approval resolution behavior.
        fixture_input = (
            ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
        )
        result = validate_static_inputs(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["diagnostics"], [])


if __name__ == "__main__":
    unittest.main()
