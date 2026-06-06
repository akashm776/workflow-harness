from __future__ import annotations

import json
from pathlib import Path
import unittest

from compiler.canonical_json import canonical_json_text
from compiler.compile_run import compile_static_artifacts, summarize_compile_result


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
INVALID_FIXTURE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"
CONFLICTING_APPROVAL_FIXTURE = (
    ROOT / "fixtures" / "invalid" / "conflicting-approval-decisions" / "input"
)
CONFLICTING_APPROVAL_ERROR = (
    ROOT
    / "fixtures"
    / "invalid"
    / "conflicting-approval-decisions"
    / "expected"
    / "error.json"
)
EMPTY_APPROVAL_DECISIONS = (
    ROOT / "fixtures" / "valid" / "simple-workflow" / "input" / "ApprovalDecisions-empty.json"
)


class CompileRunTests(unittest.TestCase):
    def test_simple_workflow_compiles_into_all_artifact_dicts(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

        result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            set(result["artifacts"].keys()),
            {
                "CompilationReport.json",
                "EffectivePolicy.json",
                "ExecutionBindings.json",
                "CompiledArtifactIndex.json",
            },
        )
        self.assertEqual(
            result["artifacts"]["CompilationReport.json"]["status"], "compiled"
        )
        self.assertEqual(
            result["artifacts"]["EffectivePolicy.json"]["artifact_lifecycle_state"],
            "compiled",
        )
        self.assertEqual(
            result["artifacts"]["ExecutionBindings.json"]["artifact_lifecycle_state"],
            "compiled",
        )
        self.assertEqual(
            result["artifacts"]["CompiledArtifactIndex.json"]["artifact_lifecycle_state"],
            "compiled",
        )
        self.assertFalse(result["artifacts"]["EffectivePolicy.json"]["review_required"])

    def test_approval_required_workflow_compiles_into_all_artifact_dicts(self) -> None:
        fixture_input = (
            ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
        )

        result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        self.assertTrue(result["ok"])
        self.assertEqual(
            result["artifacts"]["CompilationReport.json"]["status"], "compiled"
        )
        self.assertEqual(
            result["artifacts"]["EffectivePolicy.json"]["artifact_lifecycle_state"],
            "compiled",
        )
        self.assertEqual(
            result["artifacts"]["ExecutionBindings.json"]["artifact_lifecycle_state"],
            "compiled",
        )
        self.assertEqual(
            result["artifacts"]["CompiledArtifactIndex.json"]["artifact_lifecycle_state"],
            "compiled",
        )
        self.assertFalse(result["artifacts"]["EffectivePolicy.json"]["review_required"])
        self.assertEqual(
            [entry["artifact_name"] for entry in result["artifacts"]["CompiledArtifactIndex.json"]["artifacts"]],
            ["CompilationReport", "EffectivePolicy", "ExecutionBindings"],
        )

    def test_unknown_node_type_invalid_fixture_returns_failed_artifacts(self) -> None:
        result = compile_static_artifacts(
            INVALID_FIXTURE / "WorkflowSpec.json",
            INVALID_FIXTURE / "NodeTypeRegistry.json",
            INVALID_FIXTURE / "RequestedAuth.json",
            INVALID_FIXTURE / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        compilation_report = result["artifacts"]["CompilationReport.json"]
        compiled_artifact_index = result["artifacts"]["CompiledArtifactIndex.json"]

        self.assertFalse(result["ok"])
        self.assertEqual(set(result["artifacts"].keys()), {"CompilationReport.json", "CompiledArtifactIndex.json"})
        self.assertEqual(compilation_report["status"], "failed")
        self.assertEqual(compiled_artifact_index["artifact_lifecycle_state"], "failed")
        self.assertEqual(len(compilation_report["diagnostics"]), 1)
        self.assertEqual(
            compilation_report["diagnostics"][0]["error_code"], "UNKNOWN_NODE_TYPE"
        )

    def test_conflicting_approval_decisions_return_failed_artifacts(self) -> None:
        expected_error = json.loads(CONFLICTING_APPROVAL_ERROR.read_text(encoding="utf-8"))

        result = compile_static_artifacts(
            CONFLICTING_APPROVAL_FIXTURE / "WorkflowSpec.json",
            CONFLICTING_APPROVAL_FIXTURE / "NodeTypeRegistry.json",
            CONFLICTING_APPROVAL_FIXTURE / "RequestedAuth.json",
            CONFLICTING_APPROVAL_FIXTURE / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        compilation_report = result["artifacts"]["CompilationReport.json"]
        compiled_artifact_index = result["artifacts"]["CompiledArtifactIndex.json"]

        self.assertFalse(result["ok"])
        self.assertEqual(
            set(result["artifacts"].keys()),
            {"CompilationReport.json", "CompiledArtifactIndex.json"},
        )
        self.assertEqual(compilation_report["status"], "failed")
        self.assertEqual(compilation_report["artifact_lifecycle_state"], "failed")
        self.assertEqual(compiled_artifact_index["artifact_lifecycle_state"], "failed")
        self.assertEqual(len(compiled_artifact_index["artifacts"]), 1)
        self.assertEqual(
            compiled_artifact_index["artifacts"][0]["artifact_name"], "CompilationReport"
        )
        self.assertEqual(
            compiled_artifact_index["artifacts"][0]["artifact_path"],
            "fixtures/invalid/conflicting-approval-decisions/input/CompilationReport.json",
        )
        self.assertEqual(len(compilation_report["diagnostics"]), 1)
        diagnostic = compilation_report["diagnostics"][0]
        self.assertEqual(diagnostic["error_code"], expected_error["expected_error_code"])
        self.assertEqual(diagnostic["component"], expected_error["expected_component"])
        self.assertEqual(diagnostic["artifact"], expected_error["expected_artifact"])
        self.assertIn(expected_error["expected_message_fragment"], diagnostic["message"])

    def test_compile_run_canonical_json_is_deterministic(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"

            left = compile_static_artifacts(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "NodeTypeRegistry.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "ApprovalRequests.json",
                repo_root=ROOT,
            )
            right = compile_static_artifacts(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "NodeTypeRegistry.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "ApprovalRequests.json",
                repo_root=ROOT,
            )

            with self.subTest(fixture=fixture_name):
                self.assertEqual(canonical_json_text(left), canonical_json_text(right))

    def test_summary_for_valid_approved_workflow(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

        result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        summary = summarize_compile_result(result)

        self.assertEqual(
            summary,
            {
                "ok": True,
                "emitted_artifacts": [
                    "CompilationReport.json",
                    "CompiledArtifactIndex.json",
                    "EffectivePolicy.json",
                    "ExecutionBindings.json",
                ],
                "compilation_status": "compiled",
                "diagnostics": [],
                "may_runtime_start_possible": True,
            },
        )

    def test_summary_for_unknown_node_type_failed_workflow(self) -> None:
        result = compile_static_artifacts(
            INVALID_FIXTURE / "WorkflowSpec.json",
            INVALID_FIXTURE / "NodeTypeRegistry.json",
            INVALID_FIXTURE / "RequestedAuth.json",
            INVALID_FIXTURE / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        summary = summarize_compile_result(result)

        self.assertFalse(summary["ok"])
        self.assertEqual(
            summary["emitted_artifacts"],
            ["CompilationReport.json", "CompiledArtifactIndex.json"],
        )
        self.assertEqual(summary["compilation_status"], "failed")
        self.assertFalse(summary["may_runtime_start_possible"])
        self.assertEqual(len(summary["diagnostics"]), 1)
        self.assertEqual(summary["diagnostics"][0]["error_code"], "UNKNOWN_NODE_TYPE")

    def test_summary_for_conflicting_approval_decisions_failed_workflow(self) -> None:
        result = compile_static_artifacts(
            CONFLICTING_APPROVAL_FIXTURE / "WorkflowSpec.json",
            CONFLICTING_APPROVAL_FIXTURE / "NodeTypeRegistry.json",
            CONFLICTING_APPROVAL_FIXTURE / "RequestedAuth.json",
            CONFLICTING_APPROVAL_FIXTURE / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        summary = summarize_compile_result(result)

        self.assertFalse(summary["ok"])
        self.assertEqual(
            summary["emitted_artifacts"],
            ["CompilationReport.json", "CompiledArtifactIndex.json"],
        )
        self.assertEqual(summary["compilation_status"], "failed")
        self.assertFalse(summary["may_runtime_start_possible"])
        self.assertEqual(len(summary["diagnostics"]), 1)
        self.assertEqual(
            summary["diagnostics"][0]["error_code"], "CONFLICTING_APPROVAL_DECISIONS"
        )

    def test_summary_for_unapproved_workflow_reports_runtime_start_not_possible(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

        result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
            approval_decisions_path=EMPTY_APPROVAL_DECISIONS,
        )

        self.assertTrue(result["ok"])
        self.assertTrue("EffectivePolicy.json" in result["artifacts"])
        self.assertTrue("ExecutionBindings.json" in result["artifacts"])
        self.assertTrue(result["artifacts"]["EffectivePolicy.json"]["review_required"])

        summary = summarize_compile_result(result)

        self.assertFalse(summary["may_runtime_start_possible"])


if __name__ == "__main__":
    unittest.main()
