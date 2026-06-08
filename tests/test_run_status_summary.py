from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from cli.workflow_demo_cli import run_workflow_demo
from orchestrator.safe_run import safe_noop_run
from runtime.run_status_summary import summarize_run_directory


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


if __name__ == "__main__":
    unittest.main()
