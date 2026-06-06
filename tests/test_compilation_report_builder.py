from __future__ import annotations

import json
from pathlib import Path
import unittest

from compiler.canonical_json import canonical_json_text
from compiler.compilation_report import build_compilation_report


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
INVALID_FIXTURE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"


class CompilationReportBuilderTests(unittest.TestCase):
    def test_valid_fixtures_build_successful_compilation_reports(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            workflow_spec = json.loads(
                (fixture_input / "WorkflowSpec.json").read_text(encoding="utf-8")
            )

            report = build_compilation_report(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "NodeTypeRegistry.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "ApprovalRequests.json",
            )

            with self.subTest(fixture=fixture_name):
                self.assertEqual(
                    report,
                    {
                        "schema_version": "m1",
                        "graph_revision_id": workflow_spec["graph_revision_id"],
                        "workflow_revision_id": workflow_spec["workflow_revision_id"],
                        "policy_bundle_digest": workflow_spec["policy_bundle_digest"],
                        "artifact_lifecycle_state": "compiled",
                        "status": "compiled",
                        "diagnostics": [],
                    },
                )

    def test_invalid_fixture_builds_failed_compilation_report(self) -> None:
        report = build_compilation_report(
            INVALID_FIXTURE / "WorkflowSpec.json",
            INVALID_FIXTURE / "NodeTypeRegistry.json",
            INVALID_FIXTURE / "RequestedAuth.json",
            INVALID_FIXTURE / "ApprovalRequests.json",
        )

        self.assertEqual(report["schema_version"], "m1")
        self.assertEqual(report["graph_revision_id"], "graph-rev-invalid-001")
        self.assertEqual(report["workflow_revision_id"], "workflow-rev-invalid-001")
        self.assertEqual(report["policy_bundle_digest"], "policy-bundle-digest-invalid-001")
        self.assertEqual(report["artifact_lifecycle_state"], "failed")
        self.assertEqual(report["status"], "failed")
        self.assertEqual(len(report["diagnostics"]), 1)
        self.assertEqual(report["diagnostics"][0]["error_code"], "UNKNOWN_NODE_TYPE")

    def test_compilation_report_canonical_json_is_deterministic(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

        report_left = build_compilation_report(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
        )
        report_right = build_compilation_report(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
        )

        self.assertEqual(canonical_json_text(report_left), canonical_json_text(report_right))
        self.assertEqual(
            canonical_json_text(report_left),
            '{"artifact_lifecycle_state":"compiled","diagnostics":[],"graph_revision_id":"graph-rev-simple-001","policy_bundle_digest":"policy-bundle-digest-001","schema_version":"m1","status":"compiled","workflow_revision_id":"workflow-rev-simple-001"}',
        )


if __name__ == "__main__":
    unittest.main()
