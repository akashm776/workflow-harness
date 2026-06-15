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

    def _summary_with_compiler_governance_timeline(self) -> dict:
        summary = _sample_summary()
        summary["compiler_governance_timeline"] = [
            {
                "step": "candidate_artifacts",
                "label": "Candidate artifacts",
                "status": "present",
                "detail": (
                    "Candidate workflow and requested authority artifacts are "
                    "local planner outputs."
                ),
            },
            {
                "step": "compilation_report",
                "label": "Compilation report",
                "status": "present",
                "detail": "A local CompilationReport.json artifact was observed.",
            },
            {
                "step": "approval_gate",
                "label": "Approval gate",
                "status": "blocked",
                "detail": (
                    "Current-run approval is required before safe no-op "
                    "completion."
                ),
            },
            {
                "step": "runtime_execution_mode",
                "label": "Runtime execution mode",
                "status": "safe_noop",
                "detail": (
                    "Runtime remains safe no-op; no broker, sandbox, tool, "
                    "connector, MCP, network, or model execution is performed."
                ),
            },
        ]
        return summary

    def test_render_includes_compiler_governance_timeline(self) -> None:
        rendered = render_run_status_summary_view(
            self._summary_with_compiler_governance_timeline()
        )

        self.assertIn("Compiler Governance Timeline:", rendered)
        self.assertIn("- Candidate artifacts: present", rendered)
        self.assertIn(
            "  Candidate workflow and requested authority artifacts are local planner outputs.",
            rendered,
        )
        self.assertIn("- Compilation report: present", rendered)
        self.assertIn(
            "  A local CompilationReport.json artifact was observed.",
            rendered,
        )
        self.assertIn("- Approval gate: blocked", rendered)
        self.assertIn(
            "  Current-run approval is required before safe no-op completion.",
            rendered,
        )
        self.assertIn("- Runtime execution mode: safe_noop", rendered)

    def test_compiler_governance_timeline_renders_after_review_gate_and_before_stage(
        self,
    ) -> None:
        summary = self._summary_with_compiler_governance_timeline()
        summary["review_gate"] = {"blocked_reason": "review_required"}
        summary["approval_request_count"] = 1
        summary["governance_lifecycle_stage"] = {
            "stage": "blocked_awaiting_operator_approval",
            "display_only": True,
        }

        rendered = render_run_status_summary_view(summary)

        review_gate_idx = rendered.index("Review Gate:")
        timeline_idx = rendered.index("Compiler Governance Timeline:")
        stage_idx = rendered.index("Governance Lifecycle Stage:")
        self.assertLess(review_gate_idx, timeline_idx)
        self.assertLess(timeline_idx, stage_idx)

    def test_render_without_compiler_governance_timeline_has_no_section(self) -> None:
        rendered = render_run_status_summary_view(_sample_summary())
        self.assertNotIn("Compiler Governance Timeline:", rendered)

    def test_render_with_malformed_compiler_governance_timeline_has_no_section(
        self,
    ) -> None:
        summary = _sample_summary()
        summary["compiler_governance_timeline"] = {"bad": "shape"}

        rendered = render_run_status_summary_view(summary)

        self.assertNotIn("Compiler Governance Timeline:", rendered)

    def test_render_does_not_mutate_input_with_compiler_governance_timeline(
        self,
    ) -> None:
        summary = self._summary_with_compiler_governance_timeline()
        original = copy.deepcopy(summary)

        render_run_status_summary_view(summary)

        self.assertEqual(summary, original)

    def _summary_with_broker_handoff_readiness_preview(self) -> dict:
        summary = _sample_summary()
        summary["broker_handoff_readiness_preview"] = {
            "display_only": True,
            "future_broker_not_implemented": True,
            "not_authority": True,
            "not_approval": True,
            "not_execution": True,
            "not_broker_request": True,
            "current_run_scope_only": True,
            "status": "blocked_missing_approval",
            "items": [
                {
                    "name": "candidate_workflow",
                    "status": "present",
                    "detail": "Candidate workflow artifact was observed.",
                },
                {
                    "name": "approval_requests",
                    "status": "present",
                    "detail": "1 approval request observed.",
                },
                {
                    "name": "approval_decisions",
                    "status": "missing",
                    "detail": "No local ApprovalDecisions.json artifact was observed.",
                },
                {
                    "name": "runtime_mode",
                    "status": "safe_noop",
                    "detail": (
                        "Runtime remains safe no-op; no broker/sandbox/tool "
                        "execution is performed."
                    ),
                },
                {
                    "name": "future_broker",
                    "status": "not_implemented",
                    "detail": (
                        "No broker request is created and no sandbox/backend is launched."
                    ),
                },
            ],
        }
        return summary

    def _summary_with_approved_capability_handoff_projection(self) -> dict:
        summary = _sample_summary()
        summary["approved_capability_handoff_projection"] = {
            "display_only": True,
            "current_run_scope_only": True,
            "not_authority": True,
            "not_approval": True,
            "not_execution": True,
            "not_broker_request": True,
            "future_broker_not_implemented": True,
            "status": "approved_capabilities_observed",
            "approved_count": 1,
            "entries": [
                {
                    "request_id": "req-1",
                    "node_id": "retrieve-1",
                    "approval_subject_hash": "subject-1",
                    "decision": "approved",
                    "scope": "current_run_request_only",
                    "eligible_for_future_broker_contract": True,
                    "detail": (
                        "Local approved decision observed; no broker request is "
                        "created."
                    ),
                }
            ],
            "blocked_entries": [
                {
                    "request_id": "req-2",
                    "node_id": "retrieve-2",
                    "approval_subject_hash": "subject-2",
                    "reason": "missing_local_approved_decision",
                }
            ],
        }
        return summary

    def test_render_includes_broker_handoff_readiness_preview(self) -> None:
        rendered = render_run_status_summary_view(
            self._summary_with_broker_handoff_readiness_preview()
        )

        self.assertIn("Broker Handoff Readiness Preview:", rendered)
        self.assertIn("Status: blocked_missing_approval", rendered)
        self.assertIn("Display-only: yes", rendered)
        self.assertIn("Future broker implemented: no", rendered)
        self.assertIn("Authority: no", rendered)
        self.assertIn("Approval: no", rendered)
        self.assertIn("Execution: no", rendered)
        self.assertIn("- candidate_workflow: present", rendered)
        self.assertIn("  Candidate workflow artifact was observed.", rendered)
        self.assertIn("- approval_requests: present", rendered)
        self.assertIn("- approval_decisions: missing", rendered)
        self.assertIn("- runtime_mode: safe_noop", rendered)
        self.assertIn("- future_broker: not_implemented", rendered)

    def test_broker_handoff_readiness_preview_renders_after_timeline_and_before_stage(
        self,
    ) -> None:
        summary = self._summary_with_compiler_governance_timeline()
        summary["review_gate"] = {"blocked_reason": "review_required"}
        summary["approval_request_count"] = 1
        summary["broker_handoff_readiness_preview"] = (
            self._summary_with_broker_handoff_readiness_preview()[
                "broker_handoff_readiness_preview"
            ]
        )
        summary["governance_lifecycle_stage"] = {
            "stage": "blocked_awaiting_operator_approval",
            "display_only": True,
        }

        rendered = render_run_status_summary_view(summary)

        review_gate_idx = rendered.index("Review Gate:")
        timeline_idx = rendered.index("Compiler Governance Timeline:")
        preview_idx = rendered.index("Broker Handoff Readiness Preview:")
        stage_idx = rendered.index("Governance Lifecycle Stage:")
        self.assertLess(review_gate_idx, timeline_idx)
        self.assertLess(timeline_idx, preview_idx)
        self.assertLess(preview_idx, stage_idx)

    def test_broker_handoff_readiness_preview_renders_after_review_gate_when_timeline_missing(
        self,
    ) -> None:
        summary = self._summary_with_broker_handoff_readiness_preview()
        summary["review_gate"] = {"blocked_reason": "review_required"}
        summary["approval_request_count"] = 1
        summary["governance_lifecycle_stage"] = {
            "stage": "blocked_awaiting_operator_approval",
            "display_only": True,
        }

        rendered = render_run_status_summary_view(summary)

        review_gate_idx = rendered.index("Review Gate:")
        preview_idx = rendered.index("Broker Handoff Readiness Preview:")
        stage_idx = rendered.index("Governance Lifecycle Stage:")
        self.assertLess(review_gate_idx, preview_idx)
        self.assertLess(preview_idx, stage_idx)

    def test_render_without_broker_handoff_readiness_preview_has_no_section(self) -> None:
        rendered = render_run_status_summary_view(_sample_summary())
        self.assertNotIn("Broker Handoff Readiness Preview:", rendered)

    def test_render_with_malformed_broker_handoff_readiness_preview_has_no_section(
        self,
    ) -> None:
        summary = _sample_summary()
        summary["broker_handoff_readiness_preview"] = {"items": "bad-shape"}

        rendered = render_run_status_summary_view(summary)

        self.assertNotIn("Broker Handoff Readiness Preview:", rendered)

    def test_render_does_not_mutate_input_with_broker_handoff_readiness_preview(
        self,
    ) -> None:
        summary = self._summary_with_broker_handoff_readiness_preview()
        original = copy.deepcopy(summary)

        render_run_status_summary_view(summary)

        self.assertEqual(summary, original)

    def test_render_includes_approved_capability_handoff_projection(self) -> None:
        rendered = render_run_status_summary_view(
            self._summary_with_approved_capability_handoff_projection()
        )

        self.assertIn("Approved Capability Handoff Projection:", rendered)
        self.assertIn("Status: approved_capabilities_observed", rendered)
        self.assertIn("Display-only: yes", rendered)
        self.assertIn("Current-run scope only: yes", rendered)
        self.assertIn("Authority: no", rendered)
        self.assertIn("Approval: no", rendered)
        self.assertIn("Execution: no", rendered)
        self.assertIn("Broker request: no", rendered)
        self.assertIn("Future broker implemented: no", rendered)
        self.assertIn("Approved entries: 1", rendered)
        self.assertIn("- req-1 / retrieve-1: approved", rendered)
        self.assertIn("  approval_subject_hash: subject-1", rendered)
        self.assertIn("  scope: current_run_request_only", rendered)
        self.assertIn("Blocked entries: 1", rendered)
        self.assertIn(
            "- req-2 / retrieve-2: missing_local_approved_decision",
            rendered,
        )

    def test_approved_capability_handoff_projection_renders_after_broker_preview_and_before_stage(
        self,
    ) -> None:
        summary = self._summary_with_compiler_governance_timeline()
        summary["review_gate"] = {"blocked_reason": "review_required"}
        summary["approval_request_count"] = 1
        summary["broker_handoff_readiness_preview"] = (
            self._summary_with_broker_handoff_readiness_preview()[
                "broker_handoff_readiness_preview"
            ]
        )
        summary["approved_capability_handoff_projection"] = (
            self._summary_with_approved_capability_handoff_projection()[
                "approved_capability_handoff_projection"
            ]
        )
        summary["governance_lifecycle_stage"] = {
            "stage": "blocked_awaiting_operator_approval",
            "display_only": True,
        }

        rendered = render_run_status_summary_view(summary)

        broker_preview_idx = rendered.index("Broker Handoff Readiness Preview:")
        projection_idx = rendered.index("Approved Capability Handoff Projection:")
        stage_idx = rendered.index("Governance Lifecycle Stage:")
        self.assertLess(broker_preview_idx, projection_idx)
        self.assertLess(projection_idx, stage_idx)

    def test_approved_capability_handoff_projection_renders_after_timeline_when_broker_preview_missing(
        self,
    ) -> None:
        summary = self._summary_with_compiler_governance_timeline()
        summary["review_gate"] = {"blocked_reason": "review_required"}
        summary["approval_request_count"] = 1
        summary["approved_capability_handoff_projection"] = (
            self._summary_with_approved_capability_handoff_projection()[
                "approved_capability_handoff_projection"
            ]
        )
        summary["governance_lifecycle_stage"] = {
            "stage": "blocked_awaiting_operator_approval",
            "display_only": True,
        }

        rendered = render_run_status_summary_view(summary)

        timeline_idx = rendered.index("Compiler Governance Timeline:")
        projection_idx = rendered.index("Approved Capability Handoff Projection:")
        stage_idx = rendered.index("Governance Lifecycle Stage:")
        self.assertLess(timeline_idx, projection_idx)
        self.assertLess(projection_idx, stage_idx)

    def test_render_with_malformed_approved_capability_handoff_projection_has_no_section(
        self,
    ) -> None:
        summary = _sample_summary()
        summary["approved_capability_handoff_projection"] = {
            "status": "malformed",
            "entries": [],
            "blocked_entries": [],
        }

        rendered = render_run_status_summary_view(summary)

        self.assertNotIn("Approved Capability Handoff Projection:", rendered)

    def test_render_does_not_mutate_input_with_approved_capability_handoff_projection(
        self,
    ) -> None:
        summary = self._summary_with_approved_capability_handoff_projection()
        original = copy.deepcopy(summary)

        render_run_status_summary_view(summary)

        self.assertEqual(summary, original)

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
