from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from cli.workflow_demo_cli import run_workflow_demo
from examples.safe_innovation_demo import run_safe_innovation_demo
from orchestrator.safe_run import safe_noop_run
from runtime.run_status_summary import (
    _build_governance_lifecycle_stage,
    summarize_run_directory,
)


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
SIMPLE_NODE_TYPE_REGISTRY = SIMPLE_WORKFLOW / "NodeTypeRegistry.json"
INNOVATION_CONTEXT_FIXTURE_PATHS = (
    "fixtures/future/innovation-context/ProgramContext.json",
    "fixtures/future/innovation-context/RepoContextSummary.json",
    "fixtures/future/innovation-context/ConfluenceContextSummary.json",
    "fixtures/future/innovation-context/IssueTrackerContextSummary.json",
    "fixtures/future/innovation-context/Rubric.json",
)
INNOVATION_REVIEW_PROPOSED_TOOL_ACCESS = {
    "display_only": True,
    "proposal_only": True,
    "no_execution": True,
    "no_connector_support": True,
    "tools": [
        {"tool_name": "example-local-file-reader", "access_mode": "read"},
    ],
    "connectors": [
        {"connector_name": "example-bitbucket", "scope": "read:example/repo"},
        {"connector_name": "example-confluence", "scope": "read:example/space"},
        {
            "connector_name": "example-issue-tracker",
            "scope": "read:example/project",
        },
    ],
}
INNOVATION_REVIEW_COMPILER_AUTHORIZATION_PROJECTION = {
    "display_only": True,
    "compiler_owned_summary": True,
    "not_executable": True,
    "not_persisted_as_artifact": True,
    "no_runtime_authority": True,
    "current_run_scope_only": True,
    "requested_authority": [
        "tool: example-local-file-reader access_mode=read",
        "connector: example-bitbucket scope=read:example/repo",
        "connector: example-confluence scope=read:example/space",
        "connector: example-issue-tracker scope=read:example/project",
        "permission: read target=example/program-data",
    ],
    "approval_required": [
        "tool: example-local-file-reader access_mode=read",
        "connector: example-bitbucket scope=read:example/repo",
        "connector: example-confluence scope=read:example/space",
        "connector: example-issue-tracker scope=read:example/project",
        "permission: read target=example/program-data",
    ],
    "blocked_authority": [
        "tool: example-local-file-reader access_mode=read",
        "connector: example-bitbucket scope=read:example/repo",
        "connector: example-confluence scope=read:example/space",
        "connector: example-issue-tracker scope=read:example/project",
        "permission: read target=example/program-data",
    ],
    "unsupported_authority": [],
}
INNOVATION_REVIEW_OPERATOR_REVIEW_PACKET = {
    "review_required": True,
    "blocked_by_review": True,
    "decision_scope": "current run/request only",
    "execution_mode": "safe_noop_only",
    "included_sections": [
        "Review Gate",
        "Candidate Workflow",
        "Fixture Lineage",
        "Proposed Tool Access",
        "Compiler Authorization Projection",
        "Approval Binding Summary",
        "Verifier / Evidence Status",
        "Broker Boundary Status",
    ],
}


class SummarizeRunDirectoryTests(unittest.TestCase):
    def _completed_run(self, output_dir: Path) -> None:
        safe_noop_run(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

    def test_completed_run_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            self._completed_run(run_dir)

            summary = summarize_run_directory(run_dir)

            self.assertEqual(summary["run_dir"], str(run_dir))
            self.assertTrue(summary["complete_safe_noop_run"])
            self.assertEqual(summary["compilation_status"], "compiled")
            self.assertEqual(summary["execution_status"], "completed")
            self.assertIs(summary["review_required"], False)
            self.assertFalse(summary["blocked_by_review"])
            self.assertFalse(summary["approval_requests_present"])
            self.assertEqual(summary["approval_request_count"], 0)
            self.assertIsNone(summary["approval_requests_path"])
            self.assertIsNone(summary["review_gate"])
            self.assertFalse(summary["candidate_dir_present"])
            self.assertIsNone(summary["compiler_authorization_projection"])
            self.assertIsNone(summary["operator_review_packet"])
            stage = summary["governance_lifecycle_stage"]
            self.assertEqual(stage["stage"], "completed_safe_noop")
            self.assertEqual(stage["execution_mode"], "safe_noop_only")
            self.assertIs(stage["display_only"], True)
            self.assertIn("artifacts", summary)
            self.assertIn(
                f"python -m cli.run_status_cli --run-dir {run_dir} --view",
                summary["status_command"],
            )

    def test_blocked_demo_run_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="blocked demo",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )

            summary = summarize_run_directory(run_dir)
            approval_requests = json.loads(
                (run_dir / "candidate" / "ApprovalRequests.json").read_text(
                    encoding="utf-8"
                )
            )
            first_request = approval_requests["requests"][0]

            self.assertTrue(summary["complete_safe_noop_run"])
            self.assertEqual(summary["compilation_status"], "compiled")
            self.assertEqual(summary["execution_status"], "blocked")
            self.assertIs(summary["review_required"], True)
            self.assertTrue(summary["blocked_by_review"])
            self.assertTrue(summary["approval_requests_present"])
            self.assertEqual(summary["approval_request_count"], 1)
            self.assertIsNotNone(summary["approval_requests_path"])
            self.assertIn("ApprovalRequests.json", summary["approval_requests_path"])
            self.assertIsNotNone(summary["review_gate"])
            self.assertEqual(
                summary["review_gate"]["blocked_reason"], "review_required"
            )
            self.assertEqual(
                summary["review_gate"]["guidance"],
                "Explicit current-run approval is required to unblock this "
                "safe no-op run.",
            )
            self.assertEqual(
                summary["review_gate"]["request_id"], first_request["request_id"]
            )
            self.assertEqual(summary["review_gate"]["node_id"], first_request["node_id"])
            self.assertEqual(
                summary["review_gate"]["reason"], first_request["reason"]
            )
            self.assertTrue(summary["candidate_dir_present"])
            stage = summary["governance_lifecycle_stage"]
            self.assertEqual(
                stage["stage"], "blocked_awaiting_operator_approval"
            )
            self.assertEqual(stage["approval_scope"], "current run/request only")
            self.assertIs(stage["display_only"], True)

    def test_missing_directory_is_fail_soft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "does-not-exist"

            summary = summarize_run_directory(run_dir)

            self.assertFalse(summary["complete_safe_noop_run"])
            self.assertEqual(summary["compilation_status"], "unknown")
            self.assertEqual(summary["execution_status"], "unknown")
            self.assertIsNone(summary["review_required"])
            self.assertFalse(summary["blocked_by_review"])
            self.assertFalse(summary["approval_requests_present"])
            self.assertEqual(summary["approval_request_count"], 0)
            self.assertIsNone(summary["approval_requests_path"])
            self.assertIsNone(summary["review_gate"])
            self.assertFalse(summary["candidate_dir_present"])
            self.assertEqual(
                summary["governance_lifecycle_stage"]["stage"], "unknown"
            )

    def test_malformed_json_is_fail_soft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            for name in (
                "CompilationReport.json",
                "ExecutionManifest.json",
                "ExecutionResult.json",
                "EffectivePolicy.json",
            ):
                (run_dir / name).write_text("{ not valid json", encoding="utf-8")

            summary = summarize_run_directory(run_dir)

            self.assertEqual(summary["compilation_status"], "unknown")
            self.assertEqual(summary["execution_status"], "unknown")
            self.assertIsNone(summary["review_required"])
            self.assertFalse(summary["blocked_by_review"])

    def test_summary_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            self._completed_run(run_dir)
            before = sorted(p.name for p in run_dir.iterdir())

            summarize_run_directory(run_dir)

            after = sorted(p.name for p in run_dir.iterdir())
            self.assertEqual(before, after)

    def test_innovation_demo_run_includes_candidate_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="generate innovation ideas from program data",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )

            candidate_workflow = summarize_run_directory(run_dir)["candidate_workflow"]

            self.assertIsNotNone(candidate_workflow)
            self.assertEqual(len(candidate_workflow["nodes"]), 5)
            self.assertEqual(len(candidate_workflow["edges"]), 4)
            display_names = {
                node.get("display_name") for node in candidate_workflow["nodes"]
            }
            self.assertEqual(
                display_names,
                {
                    "Load Program Data",
                    "Gather Example Context",
                    "Generate Idea Candidates",
                    "Score Against Rubric",
                    "Synthesize MVP Plans",
                },
            )
            node_types = {node["node_type"] for node in candidate_workflow["nodes"]}
            self.assertTrue(node_types.issubset({"retrieve", "synthesize"}))

    def test_innovation_review_demo_run_includes_candidate_workflow_and_review_gate(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            summary = summarize_run_directory(run_dir)
            candidate_workflow = summary["candidate_workflow"]

            self.assertIsNotNone(candidate_workflow)
            self.assertEqual(len(candidate_workflow["nodes"]), 7)
            self.assertEqual(len(candidate_workflow["edges"]), 6)
            display_names = [
                node.get("display_name") for node in candidate_workflow["nodes"]
            ]
            self.assertEqual(
                display_names,
                [
                    "Load Program Data",
                    "Gather Example Context",
                    "Dedupe Against Existing Work",
                    "Generate Idea Candidates",
                    "Score Against Rubric",
                    "Critique Top Ideas",
                    "Synthesize MVP Plans",
                ],
            )
            self.assertTrue(summary["blocked_by_review"])
            self.assertIsNotNone(summary["review_gate"])
            self.assertEqual(
                summary["fixture_lineage"],
                {
                    "display_only": True,
                    "not_loaded": True,
                    "not_control_plane_inputs": True,
                    "paths": list(INNOVATION_CONTEXT_FIXTURE_PATHS),
                },
            )
            self.assertEqual(
                summary["proposed_tool_access"],
                INNOVATION_REVIEW_PROPOSED_TOOL_ACCESS,
            )
            self.assertEqual(
                summary["compiler_authorization_projection"],
                INNOVATION_REVIEW_COMPILER_AUTHORIZATION_PROJECTION,
            )
            self.assertEqual(
                summary["operator_review_packet"],
                INNOVATION_REVIEW_OPERATOR_REVIEW_PACKET,
            )

    def test_default_innovation_demo_run_does_not_include_fixture_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="generate innovation ideas from program data",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )

            summary = summarize_run_directory(run_dir)

            self.assertIsNone(summary["fixture_lineage"])
            self.assertIsNone(summary["proposed_tool_access"])
            self.assertIsNone(summary["compiler_authorization_projection"])
            self.assertEqual(
                summary["operator_review_packet"],
                {
                    "review_required": True,
                    "blocked_by_review": True,
                    "decision_scope": "current run/request only",
                    "execution_mode": "safe_noop_only",
                    "included_sections": ["Review Gate", "Candidate Workflow"],
                },
            )

    def test_fixture_lineage_is_display_only_and_never_reads_fixture_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            original_exists = Path.exists
            original_read_text = Path.read_text
            original_open = Path.open
            original_stat = Path.stat

            def _is_fixture_path(path: Path) -> bool:
                normalized = str(path).replace("\\", "/")
                return "fixtures/future/innovation-context/" in normalized

            def guarded_exists(path: Path) -> bool:
                if _is_fixture_path(path):
                    raise AssertionError(f"fixture path exists() should not be called: {path}")
                return original_exists(path)

            def guarded_read_text(path: Path, *args: object, **kwargs: object) -> str:
                if _is_fixture_path(path):
                    raise AssertionError(
                        f"fixture path read_text() should not be called: {path}"
                    )
                return original_read_text(path, *args, **kwargs)

            def guarded_open(path: Path, *args: object, **kwargs: object):
                if _is_fixture_path(path):
                    raise AssertionError(f"fixture path open() should not be called: {path}")
                return original_open(path, *args, **kwargs)

            def guarded_stat(path: Path, *args: object, **kwargs: object):
                if _is_fixture_path(path):
                    raise AssertionError(f"fixture path stat() should not be called: {path}")
                return original_stat(path, *args, **kwargs)

            with (
                mock.patch.object(Path, "exists", guarded_exists),
                mock.patch.object(Path, "read_text", guarded_read_text),
                mock.patch.object(Path, "open", guarded_open),
                mock.patch.object(Path, "stat", guarded_stat),
            ):
                summary = summarize_run_directory(run_dir)

            self.assertIsNotNone(summary["fixture_lineage"])
            self.assertEqual(
                summary["fixture_lineage"]["paths"],
                list(INNOVATION_CONTEXT_FIXTURE_PATHS),
            )

    def test_compiler_authorization_projection_is_display_only_and_never_reads_future_fixture_paths(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            original_exists = Path.exists
            original_read_text = Path.read_text
            original_open = Path.open
            original_stat = Path.stat

            def _is_projection_fixture_path(path: Path) -> bool:
                normalized = str(path).replace("\\", "/")
                return (
                    "fixtures/future/compiler-authorization-summary/"
                    in normalized
                )

            def guarded_exists(path: Path) -> bool:
                if _is_projection_fixture_path(path):
                    raise AssertionError(
                        f"projection fixture exists() should not be called: {path}"
                    )
                return original_exists(path)

            def guarded_read_text(path: Path, *args: object, **kwargs: object) -> str:
                if _is_projection_fixture_path(path):
                    raise AssertionError(
                        f"projection fixture read_text() should not be called: {path}"
                    )
                return original_read_text(path, *args, **kwargs)

            def guarded_open(path: Path, *args: object, **kwargs: object):
                if _is_projection_fixture_path(path):
                    raise AssertionError(
                        f"projection fixture open() should not be called: {path}"
                    )
                return original_open(path, *args, **kwargs)

            def guarded_stat(path: Path, *args: object, **kwargs: object):
                if _is_projection_fixture_path(path):
                    raise AssertionError(
                        f"projection fixture stat() should not be called: {path}"
                    )
                return original_stat(path, *args, **kwargs)

            with (
                mock.patch.object(Path, "exists", guarded_exists),
                mock.patch.object(Path, "read_text", guarded_read_text),
                mock.patch.object(Path, "open", guarded_open),
                mock.patch.object(Path, "stat", guarded_stat),
            ):
                summary = summarize_run_directory(run_dir)

            self.assertEqual(
                summary["compiler_authorization_projection"],
                INNOVATION_REVIEW_COMPILER_AUTHORIZATION_PROJECTION,
            )

    def test_compiler_authorization_projection_uses_existing_diagnostics_when_present(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            compilation_report_path = run_dir / "CompilationReport.json"
            compilation_report = json.loads(
                compilation_report_path.read_text(encoding="utf-8")
            )
            compilation_report["diagnostics"] = [
                {
                    "error_code": "UNSUPPORTED_EXECUTION_BINDING",
                    "artifact": "RequestedAuth.json",
                    "path": "$.requested_tools[0]",
                }
            ]
            compilation_report_path.write_text(
                json.dumps(compilation_report), encoding="utf-8"
            )

            summary = summarize_run_directory(run_dir)

            self.assertEqual(
                summary["compiler_authorization_projection"]["unsupported_authority"],
                [
                    "UNSUPPORTED_EXECUTION_BINDING artifact=RequestedAuth.json "
                    "path=$.requested_tools[0]"
                ],
            )

    def test_compiler_authorization_projection_ignores_unrelated_diagnostics(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            compilation_report_path = run_dir / "CompilationReport.json"
            compilation_report = json.loads(
                compilation_report_path.read_text(encoding="utf-8")
            )
            compilation_report["diagnostics"] = [
                {
                    "error_code": "UNKNOWN_NODE_TYPE",
                    "artifact": "WorkflowSpec.json",
                    "path": "$.nodes[0].node_type",
                },
                {
                    "error_code": "INVALID_ARTIFACT_SCHEMA",
                    "artifact": "RequestedAuth.json",
                    "path": "$.requested_tools",
                },
            ]
            compilation_report_path.write_text(
                json.dumps(compilation_report), encoding="utf-8"
            )

            summary = summarize_run_directory(run_dir)

            self.assertEqual(
                summary["compiler_authorization_projection"]["unsupported_authority"],
                [],
            )

    def test_approval_binding_summary_present_for_blocked_innovation_review(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            summary = summarize_run_directory(run_dir)

        approval_binding_summary = summary["approval_binding_summary"]
        self.assertIsNotNone(approval_binding_summary)
        for flag in (
            "display_only",
            "operator_owned",
            "not_reusable_authority",
            "no_approval_carryover",
            "no_runtime_authority",
            "current_run_scope_only",
            "current_request_scope_only",
        ):
            self.assertIs(approval_binding_summary[flag], True)

        self.assertEqual(len(approval_binding_summary["approval_subjects"]), 1)
        subject = approval_binding_summary["approval_subjects"][0]
        self.assertTrue(
            subject["request_id"].startswith(
                "planner-innovation-review-approval-request-"
            )
        )
        self.assertEqual(subject["node_id"], "retrieve-1")
        self.assertTrue(
            subject["approval_subject_hash"].startswith(
                "planner-innovation-review-approval-subject-"
            )
        )
        self.assertIs(subject["binds_to_current_request"], True)
        self.assertIs(subject["binds_to_candidate_artifact"], True)
        self.assertIs(subject["binds_to_requested_authority"], True)
        self.assertEqual(approval_binding_summary["unsupported_binding_claims"], [])

        # The packet enumerates the new section after the projection.
        self.assertIn(
            "Approval Binding Summary",
            summary["operator_review_packet"]["included_sections"],
        )

    def test_approval_binding_summary_not_present_for_approved_innovation_review_run(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_safe_innovation_demo(
                run_root=Path(tmp),
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                planner_template="innovation_review",
                demo_approve_current_request=True,
            )

            approved_run_dir = Path(tmp) / "innovation-approved"
            summary = summarize_run_directory(approved_run_dir)

        self.assertEqual(summary["execution_status"], "completed")
        self.assertIsNone(summary["approval_binding_summary"])

    def test_approval_binding_summary_not_present_for_blocked_stub_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="generate innovation ideas from program data",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )

            summary = summarize_run_directory(run_dir)

        self.assertTrue(summary["blocked_by_review"])
        self.assertIsNone(summary["approval_binding_summary"])

    def test_approval_binding_summary_surfaces_unsupported_binding_diagnostic(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            compilation_report_path = run_dir / "CompilationReport.json"
            compilation_report = json.loads(
                compilation_report_path.read_text(encoding="utf-8")
            )
            compilation_report["diagnostics"] = [
                {
                    "error_code": "UNSUPPORTED_APPROVAL_BINDING",
                    "artifact": "ApprovalRequests.json",
                    "path": "$.requests[0].reusable_approval",
                }
            ]
            compilation_report_path.write_text(
                json.dumps(compilation_report), encoding="utf-8"
            )

            summary = summarize_run_directory(run_dir)

        self.assertEqual(
            summary["approval_binding_summary"]["unsupported_binding_claims"],
            [
                "UNSUPPORTED_APPROVAL_BINDING artifact=ApprovalRequests.json "
                "path=$.requests[0].reusable_approval"
            ],
        )

    def test_approval_binding_summary_ignores_unrelated_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            compilation_report_path = run_dir / "CompilationReport.json"
            compilation_report = json.loads(
                compilation_report_path.read_text(encoding="utf-8")
            )
            compilation_report["diagnostics"] = [
                {
                    "error_code": "UNSUPPORTED_EXECUTION_BINDING",
                    "artifact": "WorkflowSpec.json",
                    "path": "$.nodes[0].tool_binding",
                }
            ]
            compilation_report_path.write_text(
                json.dumps(compilation_report), encoding="utf-8"
            )

            summary = summarize_run_directory(run_dir)

        self.assertEqual(
            summary["approval_binding_summary"]["unsupported_binding_claims"],
            [],
        )

    def test_approval_binding_summary_is_fail_soft_for_missing_approval_requests(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )
            (run_dir / "candidate" / "ApprovalRequests.json").unlink()

            summary = summarize_run_directory(run_dir)

        approval_binding_summary = summary["approval_binding_summary"]
        self.assertIsNotNone(approval_binding_summary)
        self.assertEqual(approval_binding_summary["approval_subjects"], [])
        self.assertIs(approval_binding_summary["display_only"], True)

    def test_verifier_evidence_status_present_for_blocked_innovation_review(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            summary = summarize_run_directory(run_dir)

        verifier_evidence_status = summary["verifier_evidence_status"]
        self.assertIsNotNone(verifier_evidence_status)
        for flag in (
            "display_only",
            "reporting_only",
            "not_authority",
            "not_verifier_output_artifact",
            "not_evidence_lineage_artifact",
            "no_runtime_authority",
            "no_execution",
            "no_approval",
            "current_run_scope_only",
        ):
            self.assertIs(verifier_evidence_status[flag], True)

        self.assertEqual(verifier_evidence_status["manifest_status"], "present")
        self.assertEqual(
            verifier_evidence_status["execution_result_status"], "present"
        )
        self.assertEqual(verifier_evidence_status["audit_log_status"], "present")
        self.assertEqual(verifier_evidence_status["produced_evidence_count"], 0)
        self.assertEqual(verifier_evidence_status["side_effect_count"], 0)
        self.assertEqual(
            verifier_evidence_status["verification_status"], "not_implemented"
        )
        self.assertEqual(len(verifier_evidence_status["findings"]), 1)

        # The packet enumerates the new section after the approval binding summary.
        included_sections = summary["operator_review_packet"]["included_sections"]
        self.assertIn("Verifier / Evidence Status", included_sections)
        self.assertGreater(
            included_sections.index("Verifier / Evidence Status"),
            included_sections.index("Approval Binding Summary"),
        )

    def test_verifier_evidence_status_not_present_for_approved_innovation_review_run(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_safe_innovation_demo(
                run_root=Path(tmp),
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                planner_template="innovation_review",
                demo_approve_current_request=True,
            )

            approved_run_dir = Path(tmp) / "innovation-approved"
            summary = summarize_run_directory(approved_run_dir)

        self.assertEqual(summary["execution_status"], "completed")
        self.assertIsNone(summary["verifier_evidence_status"])

    def test_verifier_evidence_status_not_present_for_blocked_stub_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="generate innovation ideas from program data",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )

            summary = summarize_run_directory(run_dir)

        self.assertTrue(summary["blocked_by_review"])
        self.assertIsNone(summary["verifier_evidence_status"])

    def test_verifier_evidence_status_is_fail_soft_for_missing_audit_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )
            (run_dir / "AuditLog.jsonl").unlink()

            summary = summarize_run_directory(run_dir)

        verifier_evidence_status = summary["verifier_evidence_status"]
        self.assertIsNotNone(verifier_evidence_status)
        self.assertEqual(verifier_evidence_status["audit_log_status"], "missing")
        self.assertIs(verifier_evidence_status["display_only"], True)
        self.assertEqual(
            verifier_evidence_status["verification_status"], "not_implemented"
        )

    def test_broker_boundary_status_present_for_blocked_innovation_review(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )

            summary = summarize_run_directory(run_dir)

        broker_boundary_status = summary["broker_boundary_status"]
        self.assertIsNotNone(broker_boundary_status)
        for flag in (
            "display_only",
            "reporting_only",
            "not_authority",
            "not_broker_request_artifact",
            "not_broker_decision_artifact",
            "not_broker_result_artifact",
            "no_broker_implementation",
            "no_sandbox_implementation",
            "no_runtime_authority",
            "no_execution",
            "no_approval",
            "current_run_scope_only",
        ):
            self.assertIs(broker_boundary_status[flag], True)

        self.assertEqual(
            broker_boundary_status["broker_request_status"], "not_generated"
        )
        self.assertEqual(
            broker_boundary_status["broker_decision_status"], "not_generated"
        )
        self.assertEqual(
            broker_boundary_status["broker_result_status"], "not_generated"
        )
        self.assertEqual(broker_boundary_status["sandbox_status"], "not_implemented")
        self.assertEqual(
            broker_boundary_status["execution_status"], "safe_noop_only"
        )
        self.assertEqual(len(broker_boundary_status["findings"]), 1)

        # The packet enumerates the new section after the verifier/evidence status.
        included_sections = summary["operator_review_packet"]["included_sections"]
        self.assertIn("Broker Boundary Status", included_sections)
        self.assertGreater(
            included_sections.index("Broker Boundary Status"),
            included_sections.index("Verifier / Evidence Status"),
        )

    def test_broker_boundary_status_not_present_for_approved_innovation_review_run(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_safe_innovation_demo(
                run_root=Path(tmp),
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                planner_template="innovation_review",
                demo_approve_current_request=True,
            )

            approved_run_dir = Path(tmp) / "innovation-approved"
            summary = summarize_run_directory(approved_run_dir)

        self.assertEqual(summary["execution_status"], "completed")
        self.assertIsNone(summary["broker_boundary_status"])

    def test_broker_boundary_status_not_present_for_blocked_stub_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="generate innovation ideas from program data",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )

            summary = summarize_run_directory(run_dir)

        self.assertTrue(summary["blocked_by_review"])
        self.assertIsNone(summary["broker_boundary_status"])

    def test_blocked_innovation_review_summary_writes_no_new_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )
            before = sorted(
                str(path.relative_to(run_dir))
                for path in run_dir.rglob("*")
            )

            summarize_run_directory(run_dir)

            after = sorted(
                str(path.relative_to(run_dir))
                for path in run_dir.rglob("*")
            )
            self.assertEqual(before, after)

    def test_compiler_authorization_projection_not_present_for_approved_innovation_review_run(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_safe_innovation_demo(
                run_root=Path(tmp),
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                planner_template="innovation_review",
                demo_approve_current_request=True,
            )

            approved_run_dir = Path(tmp) / "innovation-approved"
            summary = summarize_run_directory(approved_run_dir)

            self.assertEqual(summary["execution_status"], "completed")
            self.assertIs(summary["review_required"], False)
            self.assertFalse(summary["blocked_by_review"])
            self.assertIsNone(summary["compiler_authorization_projection"])
            self.assertIsNone(summary["operator_review_packet"])

    def test_malformed_requested_auth_is_fail_soft_for_proposed_tool_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )
            (run_dir / "candidate" / "RequestedAuth.json").write_text(
                "{ not valid json", encoding="utf-8"
            )

            summary = summarize_run_directory(run_dir)

            self.assertIsNotNone(summary["fixture_lineage"])
            self.assertIsNone(summary["proposed_tool_access"])
            self.assertIsNotNone(summary["compiler_authorization_projection"])
            self.assertEqual(
                summary["operator_review_packet"]["included_sections"],
                [
                    "Review Gate",
                    "Candidate Workflow",
                    "Fixture Lineage",
                    "Compiler Authorization Projection",
                    "Approval Binding Summary",
                    "Verifier / Evidence Status",
                    "Broker Boundary Status",
                ],
            )

    def test_missing_requested_auth_is_fail_soft_for_proposed_tool_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="review innovation options",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
                planner_template="innovation_review",
            )
            (run_dir / "candidate" / "RequestedAuth.json").unlink()

            summary = summarize_run_directory(run_dir)

            self.assertIsNotNone(summary["fixture_lineage"])
            self.assertIsNone(summary["proposed_tool_access"])
            self.assertIsNotNone(summary["compiler_authorization_projection"])
            self.assertEqual(
                summary["operator_review_packet"]["included_sections"],
                [
                    "Review Gate",
                    "Candidate Workflow",
                    "Fixture Lineage",
                    "Compiler Authorization Projection",
                    "Approval Binding Summary",
                    "Verifier / Evidence Status",
                    "Broker Boundary Status",
                ],
            )

    def test_missing_candidate_workflow_is_none(self) -> None:
        # A completed safe_noop_run has no candidate/ directory.
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            run_dir.mkdir()
            self._completed_run(run_dir)

            summary = summarize_run_directory(run_dir)
            self.assertIsNone(summary["candidate_workflow"])
            self.assertIsNone(summary["fixture_lineage"])
            self.assertIsNone(summary["proposed_tool_access"])
            self.assertIsNone(summary["compiler_authorization_projection"])
            self.assertIsNone(summary["operator_review_packet"])

    def test_missing_approval_requests_is_fail_soft_for_blocked_review_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="blocked demo",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )
            (run_dir / "candidate" / "ApprovalRequests.json").unlink()

            summary = summarize_run_directory(run_dir)

            self.assertTrue(summary["blocked_by_review"])
            self.assertFalse(summary["approval_requests_present"])
            self.assertEqual(summary["approval_request_count"], 0)
            self.assertIsNone(summary["approval_requests_path"])
            self.assertIsNotNone(summary["review_gate"])
            self.assertEqual(
                summary["review_gate"]["blocked_reason"], "review_required"
            )
            self.assertNotIn("request_id", summary["review_gate"])

    def test_malformed_approval_requests_is_fail_soft_for_blocked_review_gate(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "demo"
            run_workflow_demo(
                goal="blocked demo",
                node_type_registry_path=SIMPLE_NODE_TYPE_REGISTRY,
                run_dir=run_dir,
            )
            approval_requests_path = run_dir / "candidate" / "ApprovalRequests.json"
            approval_requests_path.write_text("{ not valid json", encoding="utf-8")

            summary = summarize_run_directory(run_dir)

            self.assertTrue(summary["blocked_by_review"])
            self.assertTrue(summary["approval_requests_present"])
            self.assertEqual(summary["approval_request_count"], 0)
            self.assertEqual(summary["approval_requests_path"], str(approval_requests_path))
            self.assertIsNotNone(summary["review_gate"])
            self.assertEqual(
                summary["review_gate"]["approval_requests_path"],
                str(approval_requests_path),
            )
            self.assertNotIn("request_id", summary["review_gate"])

    def test_malformed_candidate_workflow_is_fail_soft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            (run_dir / "candidate").mkdir(parents=True)
            (run_dir / "candidate" / "WorkflowSpec.json").write_text(
                "{ not valid json", encoding="utf-8"
            )

            summary = summarize_run_directory(run_dir)
            self.assertIsNone(summary["candidate_workflow"])
            self.assertIsNone(summary["proposed_tool_access"])
            self.assertIsNone(summary["operator_review_packet"])


class GovernanceLifecycleStageTests(unittest.TestCase):
    """Deterministic stage derivation from existing status fields only."""

    def test_compile_failed_takes_precedence(self) -> None:
        stage = _build_governance_lifecycle_stage(
            compilation_status="failed",
            execution_status="blocked",
            review_required=True,
            blocked_by_review=True,
        )
        self.assertEqual(stage["stage"], "compile_failed")
        self.assertIn("compiler diagnostics", stage["next_operator_action"])

    def test_blocked_awaiting_operator_approval(self) -> None:
        stage = _build_governance_lifecycle_stage(
            compilation_status="compiled",
            execution_status="blocked",
            review_required=True,
            blocked_by_review=True,
        )
        self.assertEqual(stage["stage"], "blocked_awaiting_operator_approval")
        self.assertIn("approve or deny", stage["next_operator_action"])

    def test_completed_safe_noop(self) -> None:
        stage = _build_governance_lifecycle_stage(
            compilation_status="compiled",
            execution_status="completed",
            review_required=False,
            blocked_by_review=False,
        )
        self.assertEqual(stage["stage"], "completed_safe_noop")
        self.assertIn("no real execution", stage["next_operator_action"])

    def test_compiled_no_review_required(self) -> None:
        stage = _build_governance_lifecycle_stage(
            compilation_status="compiled",
            execution_status="ready_to_execute",
            review_required=False,
            blocked_by_review=False,
        )
        self.assertEqual(stage["stage"], "compiled_no_review_required")

    def test_unknown_when_indeterminate(self) -> None:
        stage = _build_governance_lifecycle_stage(
            compilation_status="unknown",
            execution_status="unknown",
            review_required=None,
            blocked_by_review=False,
        )
        self.assertEqual(stage["stage"], "unknown")

    def test_constant_framing_fields_are_display_only(self) -> None:
        stage = _build_governance_lifecycle_stage(
            compilation_status="compiled",
            execution_status="completed",
            review_required=False,
            blocked_by_review=False,
        )
        self.assertEqual(
            stage["authority_boundary"],
            "compiler-owned authorization only; planner is non-authoritative",
        )
        self.assertEqual(stage["approval_scope"], "current run/request only")
        self.assertEqual(stage["execution_mode"], "safe_noop_only")
        self.assertIs(stage["display_only"], True)


if __name__ == "__main__":
    unittest.main()
