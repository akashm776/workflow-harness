from __future__ import annotations

import unittest

from planner.workflow_strategy_preview import (
    WorkflowStrategyPreviewError,
    preview_workflow_strategy,
)


class WorkflowStrategyPreviewTests(unittest.TestCase):
    def test_innovation_goal_selects_workflow_orchestration_and_fan_out(self) -> None:
        preview = preview_workflow_strategy(
            "Find AI innovation opportunities from program docs and repo context"
        )

        self.assertEqual(
            preview["strategy_type"], "workflow_orchestration_preview"
        )
        self.assertEqual(
            preview["selected_pattern_family"], "fan_out_and_synthesize"
        )

    def test_code_goal_selects_plan_and_solve(self) -> None:
        preview = preview_workflow_strategy(
            "Debug a repository bugfix and plan the implementation steps"
        )

        self.assertEqual(
            preview["strategy_type"], "workflow_orchestration_preview"
        )
        self.assertEqual(preview["selected_pattern_family"], "plan_and_solve")

    def test_compare_goal_selects_agent_team_and_ranking(self) -> None:
        preview = preview_workflow_strategy(
            "Compare alternatives and rank candidate approaches"
        )

        self.assertEqual(preview["strategy_type"], "agent_team_preview")
        self.assertEqual(
            preview["selected_pattern_family"], "tournament_or_ranking"
        )

    def test_audit_goal_selects_subagent_and_adversarial_verification(self) -> None:
        preview = preview_workflow_strategy(
            "Audit and critique the current proposal for risky gaps"
        )

        self.assertEqual(preview["strategy_type"], "subagent_preview")
        self.assertEqual(
            preview["selected_pattern_family"], "adversarial_verification"
        )

    def test_classify_goal_selects_skill_and_classify(self) -> None:
        preview = preview_workflow_strategy(
            "Classify and extract fields from one file"
        )

        self.assertEqual(preview["strategy_type"], "skill_preview")
        self.assertEqual(preview["selected_pattern_family"], "classify_and_act")

    def test_unknown_goal_selects_generic_fallback(self) -> None:
        preview = preview_workflow_strategy("Handle this unusual request")

        self.assertEqual(
            preview["strategy_type"], "generic_governed_workflow_preview"
        )
        self.assertEqual(
            preview["selected_pattern_family"], "generic_governed_workflow"
        )

    def test_empty_goal_fails_closed(self) -> None:
        with self.assertRaises(WorkflowStrategyPreviewError) as raised:
            preview_workflow_strategy("   ")

        self.assertEqual(raised.exception.error_code, "EMPTY_GOAL")

    def test_preview_contains_common_safety_flags_and_expected_surfaces(self) -> None:
        preview = preview_workflow_strategy(
            "Find AI innovation opportunities from program docs and repo context"
        )

        for field_name in (
            "display_only",
            "non_authoritative",
            "not_compiler_input",
            "not_authority",
            "not_approval",
            "not_execution",
            "not_broker_request",
            "no_model_calls",
            "no_tool_calls",
        ):
            self.assertIs(preview[field_name], True)

        self.assertEqual(
            preview["expected_candidate_artifacts"],
            [
                "candidate/WorkflowSpec.json",
                "candidate/RequestedAuth.json",
                "candidate/ApprovalRequests.json",
            ],
        )
        self.assertEqual(
            preview["expected_governance_surfaces"],
            [
                "compiler validation",
                "review gate",
                "operator approval decisions",
                "broker handoff readiness preview",
                "approved capability handoff projection",
            ],
        )
        self.assertIn("compiler validation", preview["next_safe_step"].lower())
        self.assertGreater(len(preview["expected_phases"]), 0)
        first_phase = preview["expected_phases"][0]
        self.assertEqual(first_phase["authority_boundary"], "proposal_only")
        self.assertIn("approval_surface", first_phase)
        self.assertEqual(
            preview["selection_mode"], "deterministic_baseline_preview"
        )
        self.assertIs(preview["future_selector_ready"], True)
        self.assertNotIn("candidate_pattern_rankings", preview)

        future_selector_notes = " ".join(preview["future_selector_notes"]).lower()
        self.assertIn("future llm/hermes workflow selection", future_selector_notes)
        self.assertIn(
            "may choose a different workflow strategy or pattern family",
            future_selector_notes,
        )

        selection_limitations = " ".join(preview["selection_limitations"]).lower()
        self.assertIn("deterministic", selection_limitations)
        self.assertIn("auditable", selection_limitations)
        self.assertIn("not the final workflow planner", selection_limitations)


if __name__ == "__main__":
    unittest.main()
