from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from compiler.static_validation import (
    validate_static_inputs,
    validate_unsupported_authority_artifacts,
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


class UnsupportedAuthorityArtifactValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            for artifact_name in (
                "WorkflowSpec.json",
                "RequestedAuth.json",
                "ApprovalRequests.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=artifact_name):
                    result = validate_unsupported_authority_artifacts(
                        fixture_input / artifact_name,
                        artifact_name,
                    )
                    self.assertTrue(result["ok"])
                    self.assertIsNone(result["diagnostic"])

    def test_workflow_spec_compiled_execution_plan_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["compiled_execution_plan"] = {
                "display_only": True
            }
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_authority_artifacts(
                path,
                "WorkflowSpec.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_AUTHORITY_ARTIFACT")
        self.assertEqual(
            diagnostic["component"],
            "authority_artifact_ownership_validator",
        )
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("$.nodes[0].compiled_execution_plan", diagnostic["message"])
        self.assertTrue(
            diagnostic["message"].startswith(
                "unsupported compiler/runtime/operator-owned authority artifact "
                "field in WorkflowSpec.json; V1 safe no-op does not accept "
                "planner-supplied compiled plans, authority manifests, "
                "diagnostics, execution results, audit artifacts, evidence "
                "lineage, or approval decisions: "
            )
        )

    def test_requested_auth_execution_manifest_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            requested_auth["execution_manifest"] = {"display_only": True}
            path = _write_json(Path(tmp) / "RequestedAuth.json", requested_auth)

            result = validate_unsupported_authority_artifacts(
                path,
                "RequestedAuth.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_AUTHORITY_ARTIFACT")
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.execution_manifest", diagnostic["message"])

    def test_approval_requests_approval_decisions_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            approval_requests["approval_decisions"] = [{"request_id": "future-only"}]
            path = _write_json(Path(tmp) / "ApprovalRequests.json", approval_requests)

            result = validate_unsupported_authority_artifacts(
                path,
                "ApprovalRequests.json",
            )

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_AUTHORITY_ARTIFACT")
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("$.approval_decisions", diagnostic["message"])

    def test_benign_string_mentioning_execution_manifest_is_not_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            workflow_spec["nodes"][0]["display_name"] = "Display execution manifest only"
            path = _write_json(Path(tmp) / "WorkflowSpec.json", workflow_spec)

            result = validate_unsupported_authority_artifacts(
                path,
                "WorkflowSpec.json",
            )

        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_aggregate_static_validation_surfaces_authority_artifact_rejection(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["verifier_output"] = {"display_only": True}

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
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_AUTHORITY_ARTIFACT")
        self.assertEqual(
            diagnostic["component"],
            "authority_artifact_ownership_validator",
        )
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("$.verifier_output", diagnostic["message"])


if __name__ == "__main__":
    unittest.main()
