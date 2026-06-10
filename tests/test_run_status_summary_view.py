from __future__ import annotations

import copy
import unittest

from tui.run_status_summary_view import render_run_status_summary_view


def _sample_summary() -> dict:
    return {
        "run_dir": "/tmp/demo",
        "complete_safe_noop_run": True,
        "artifacts": {
            "CompilationReport.json": {"exists": True},
            "ExecutionResult.json": {"exists": True},
        },
        "candidate_dir_present": True,
        "compilation_status": "compiled",
        "execution_status": "blocked",
        "review_required": True,
        "blocked_by_review": True,
        "status_command": "python -m cli.run_status_cli --run-dir /tmp/demo --view",
    }


class RunStatusSummaryViewTests(unittest.TestCase):
    def test_render_includes_all_summary_fields(self) -> None:
        rendered = render_run_status_summary_view(_sample_summary())

        self.assertIn("Safe No-Op Run Summary", rendered)
        self.assertIn("run_dir: /tmp/demo", rendered)
        self.assertIn("complete_safe_noop_run: true", rendered)
        self.assertIn("compilation_status: compiled", rendered)
        self.assertIn("execution_status: blocked", rendered)
        self.assertIn("review_required: true", rendered)
        self.assertIn("blocked_by_review: true", rendered)
        self.assertIn("candidate_dir_present: true", rendered)
        self.assertIn("[x] CompilationReport.json", rendered)
        self.assertIn("[x] ExecutionResult.json", rendered)
        self.assertIn(
            "status command: python -m cli.run_status_cli --run-dir /tmp/demo --view",
            rendered,
        )

    def test_render_does_not_mutate_input(self) -> None:
        summary = _sample_summary()
        original = copy.deepcopy(summary)

        render_run_status_summary_view(summary)

        self.assertEqual(summary, original)

    def test_render_includes_governance_lifecycle_stage_section(self) -> None:
        summary = _sample_summary()
        summary["governance_lifecycle_stage"] = {
            "stage": "blocked_awaiting_operator_approval",
            "next_operator_action": (
                "review and approve or deny requested access for the current "
                "run/request"
            ),
            "authority_boundary": (
                "compiler-owned authorization only; planner is non-authoritative"
            ),
            "approval_scope": "current run/request only",
            "execution_mode": "safe_noop_only",
            "display_only": True,
        }

        rendered = render_run_status_summary_view(summary)

        self.assertIn("Governance Lifecycle Stage:", rendered)
        self.assertIn("stage: blocked_awaiting_operator_approval", rendered)
        self.assertIn(
            "authority_boundary: compiler-owned authorization only; planner is "
            "non-authoritative",
            rendered,
        )
        self.assertIn("approval_scope: current run/request only", rendered)
        self.assertIn("execution_mode: safe_noop_only", rendered)
        self.assertIn("display_only: true", rendered)

    def test_governance_lifecycle_stage_renders_after_review_gate(self) -> None:
        summary = self._summary_with_candidate_workflow()
        summary["review_gate"] = {"blocked_reason": "review_required"}
        summary["approval_request_count"] = 1
        summary["governance_lifecycle_stage"] = {
            "stage": "blocked_awaiting_operator_approval",
            "display_only": True,
        }

        rendered = render_run_status_summary_view(summary)

        review_gate_idx = rendered.index("Review Gate:")
        stage_idx = rendered.index("Governance Lifecycle Stage:")
        candidate_idx = rendered.index("Candidate Workflow:")
        self.assertLess(review_gate_idx, stage_idx)
        self.assertLess(stage_idx, candidate_idx)

    def test_render_without_governance_lifecycle_stage_has_no_section(self) -> None:
        # The base sample summary has no governance_lifecycle_stage key.
        rendered = render_run_status_summary_view(_sample_summary())
        self.assertNotIn("Governance Lifecycle Stage:", rendered)

    def _summary_with_candidate_workflow(self) -> dict:
        summary = _sample_summary()
        summary["candidate_workflow"] = {
            "workflow_id": "planner-innovation-workflow-abc",
            "workflow_revision_id": "planner-innovation-workflow-rev-abc",
            "nodes": [
                {"node_id": "retrieve-1", "node_type": "retrieve",
                 "display_name": "Load Program Data"},
                {"node_id": "retrieve-2", "node_type": "retrieve",
                 "display_name": "Gather Example Context"},
                {"node_id": "synthesize-1", "node_type": "synthesize",
                 "display_name": "Generate Idea Candidates"},
            ],
            "edges": [
                {"from_node_id": "retrieve-1", "to_node_id": "retrieve-2",
                 "edge_type": "data-flow"},
                {"from_node_id": "retrieve-2", "to_node_id": "synthesize-1",
                 "edge_type": "data-flow"},
            ],
        }
        return summary

    def test_render_includes_candidate_workflow_section(self) -> None:
        rendered = render_run_status_summary_view(
            self._summary_with_candidate_workflow()
        )

        self.assertIn("Candidate Workflow:", rendered)
        self.assertIn("- retrieve-1 [retrieve] Load Program Data", rendered)
        self.assertIn("  -> retrieve-2", rendered)
        self.assertIn("- retrieve-2 [retrieve] Gather Example Context", rendered)
        self.assertIn("  -> synthesize-1", rendered)
        self.assertIn("- synthesize-1 [synthesize] Generate Idea Candidates", rendered)

    def test_render_does_not_mutate_input_with_candidate_workflow(self) -> None:
        summary = self._summary_with_candidate_workflow()
        original = copy.deepcopy(summary)

        render_run_status_summary_view(summary)

        self.assertEqual(summary, original)

    def test_render_without_candidate_workflow_has_no_section(self) -> None:
        # The base sample summary has no candidate_workflow key.
        rendered = render_run_status_summary_view(_sample_summary())
        self.assertNotIn("Candidate Workflow:", rendered)

    def test_render_unknown_fields(self) -> None:
        summary = {
            "run_dir": "/tmp/missing",
            "complete_safe_noop_run": False,
            "artifacts": {},
            "candidate_dir_present": False,
            "compilation_status": "unknown",
            "execution_status": "unknown",
            "review_required": None,
            "blocked_by_review": False,
            "status_command": "python -m cli.run_status_cli --run-dir /tmp/missing --view",
        }

        rendered = render_run_status_summary_view(summary)

        self.assertIn("compilation_status: unknown", rendered)
        self.assertIn("execution_status: unknown", rendered)
        self.assertIn("review_required: unknown", rendered)
        self.assertIn("blocked_by_review: false", rendered)


if __name__ == "__main__":
    unittest.main()
