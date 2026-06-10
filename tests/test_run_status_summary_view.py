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

    def test_render_includes_governance_readiness_checklist_section(self) -> None:
        summary = self._summary_with_candidate_workflow()
        summary["governance_readiness_checklist"] = [
            {
                "label": "Compiler static validation",
                "status": "satisfied",
                "reason": "Compilation status is compiled.",
            },
            {
                "label": "Operator approval gate",
                "status": "missing",
                "reason": (
                    "Explicit current-run approval is required to unblock this "
                    "safe no-op run."
                ),
            },
        ]

        rendered = render_run_status_summary_view(summary)

        self.assertIn("Governance Readiness Checklist:", rendered)
        self.assertIn("- Compiler static validation: satisfied", rendered)
        self.assertIn("  Reason: Compilation status is compiled.", rendered)
        self.assertIn("- Operator approval gate: missing", rendered)
        self.assertIn(
            "  Reason: Explicit current-run approval is required to unblock this "
            "safe no-op run.",
            rendered,
        )

    def test_governance_readiness_checklist_renders_after_stage_and_before_candidate(
        self,
    ) -> None:
        summary = self._summary_with_candidate_workflow()
        summary["review_gate"] = {"blocked_reason": "review_required"}
        summary["approval_request_count"] = 1
        summary["governance_lifecycle_stage"] = {
            "stage": "blocked_awaiting_operator_approval",
            "display_only": True,
        }
        summary["governance_readiness_checklist"] = [
            {
                "label": "Compiler static validation",
                "status": "satisfied",
                "reason": "Compilation status is compiled.",
            }
        ]

        rendered = render_run_status_summary_view(summary)

        stage_idx = rendered.index("Governance Lifecycle Stage:")
        checklist_idx = rendered.index("Governance Readiness Checklist:")
        candidate_idx = rendered.index("Candidate Workflow:")
        self.assertLess(stage_idx, checklist_idx)
        self.assertLess(checklist_idx, candidate_idx)

    def test_render_without_governance_readiness_checklist_has_no_section(self) -> None:
        rendered = render_run_status_summary_view(_sample_summary())
        self.assertNotIn("Governance Readiness Checklist:", rendered)

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

    def _summary_with_operator_review_notes(self) -> dict:
        summary = self._summary_with_candidate_workflow()
        summary["operator_review_notes"] = {
            "display_only": True,
            "operator_authored": True,
            "not_authority": True,
            "not_approval": True,
            "not_compiler_input": True,
            "not_control_plane_artifact": True,
            "current_run_scope_only": True,
            "notes_path": "/tmp/demo/candidate/OperatorReviewNotes.json",
            "note_count": 2,
            "notes_by_node": {
                "retrieve-1": [
                    {
                        "note_type": "scope_too_broad",
                        "note": "Use Bitbucket and Confluence only; do not include SharePoint yet.",
                        "requested_action": "narrow_scope",
                        "reviewer": "operator",
                    }
                ],
                "synthesize-1": [
                    {
                        "note_type": "needs_revision",
                        "note": "Split MVP synthesis from scoring evidence.",
                        "requested_action": "split_node",
                        "reviewer": "operator",
                    }
                ],
            },
        }
        return summary

    def test_render_includes_operator_review_notes_section(self) -> None:
        rendered = render_run_status_summary_view(
            self._summary_with_operator_review_notes()
        )

        self.assertIn("Operator Review Notes:", rendered)
        self.assertIn("- retrieve-1", rendered)
        self.assertIn(
            "  - scope_too_broad: Use Bitbucket and Confluence only; do not include SharePoint yet.",
            rendered,
        )
        self.assertIn("    requested_action: narrow_scope", rendered)
        self.assertIn("    reviewer: operator", rendered)
        self.assertIn("- synthesize-1", rendered)
        self.assertIn(
            "  - needs_revision: Split MVP synthesis from scoring evidence.",
            rendered,
        )

    def test_operator_review_notes_render_after_candidate_and_before_fixture_lineage(
        self,
    ) -> None:
        summary = self._summary_with_operator_review_notes()
        summary["fixture_lineage"] = {
            "display_only": True,
            "not_loaded": True,
            "not_control_plane_inputs": True,
            "paths": ["fixtures/future/example.json"],
        }

        rendered = render_run_status_summary_view(summary)

        candidate_idx = rendered.index("Candidate Workflow:")
        notes_idx = rendered.index("Operator Review Notes:")
        fixture_idx = rendered.index("Fixture Lineage:")
        self.assertLess(candidate_idx, notes_idx)
        self.assertLess(notes_idx, fixture_idx)

    def test_render_without_operator_review_notes_has_no_section(self) -> None:
        rendered = render_run_status_summary_view(self._summary_with_candidate_workflow())
        self.assertNotIn("Operator Review Notes:", rendered)

    def test_render_with_malformed_operator_review_notes_has_no_section(self) -> None:
        summary = self._summary_with_candidate_workflow()
        summary["operator_review_notes"] = {"notes_by_node": "bad-shape"}

        rendered = render_run_status_summary_view(summary)

        self.assertNotIn("Operator Review Notes:", rendered)

    def test_render_does_not_mutate_input_with_operator_review_notes(self) -> None:
        summary = self._summary_with_operator_review_notes()
        original = copy.deepcopy(summary)

        render_run_status_summary_view(summary)

        self.assertEqual(summary, original)

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
