"""Deterministic, display-only workflow proposal strategy preview.

This module previews what kind of governed workflow strategy would likely be
proposed for a plain-text goal. It is intentionally non-authoritative:

- it does not create candidate artifacts,
- it does not call models, tools, or external systems,
- it does not call compiler, runtime, broker, or sandbox code paths,
- it does not authorize, approve, or execute anything.
"""

from __future__ import annotations

import re
from typing import Any


EXPECTED_CANDIDATE_ARTIFACTS = [
    "candidate/WorkflowSpec.json",
    "candidate/RequestedAuth.json",
    "candidate/ApprovalRequests.json",
]

EXPECTED_GOVERNANCE_SURFACES = [
    "compiler validation",
    "review gate",
    "operator approval decisions",
    "broker handoff readiness preview",
    "approved capability handoff projection",
]


class WorkflowStrategyPreviewError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message


def _keyword_present(goal_lower: str, keyword: str) -> bool:
    if " " in keyword or "-" in keyword:
        return keyword in goal_lower
    return re.search(rf"\b{re.escape(keyword)}\b", goal_lower) is not None


def _matched_keywords(goal_lower: str, keywords: tuple[str, ...]) -> list[str]:
    matched: list[str] = []
    for keyword in keywords:
        if _keyword_present(goal_lower, keyword):
            matched.append(keyword)
    return matched


def _normalized_goal(goal: Any) -> str:
    if not isinstance(goal, str):
        raise WorkflowStrategyPreviewError(
            "EMPTY_GOAL",
            "goal must be a non-empty string",
        )
    normalized = goal.strip()
    if not normalized:
        raise WorkflowStrategyPreviewError(
            "EMPTY_GOAL",
            "goal must be a non-empty string",
        )
    return normalized


STRATEGY_TYPE_NAMES = {
    "skill_preview": "Skill preview",
    "subagent_preview": "Subagent preview",
    "agent_team_preview": "Agent team preview",
    "workflow_orchestration_preview": "Workflow orchestration preview",
    "generic_governed_workflow_preview": "Generic governed workflow preview",
}

PATTERN_NAMES = {
    "classify_and_act": "Classify and act",
    "fan_out_and_synthesize": "Fan-out and synthesize",
    "adversarial_verification": "Adversarial verification",
    "generate_and_filter": "Generate and filter",
    "tournament_or_ranking": "Tournament or ranking",
    "loop_until_done": "Loop until done",
    "plan_and_solve": "Plan and solve",
    "react_like_tool_use_preview": "ReAct-like tool-use preview",
    "research_synthesis": "Research synthesis",
    "generic_governed_workflow": "Generic governed workflow",
}

SKILL_KEYWORDS = (
    "format",
    "lint",
    "classify",
    "extract",
    "route",
    "tag",
    "single file",
    "one file",
)
SUBAGENT_KEYWORDS = (
    "review",
    "audit",
    "inspect",
    "investigate",
    "critique",
    "verify",
    "red team",
)
AGENT_TEAM_KEYWORDS = (
    "compare",
    "debate",
    "tournament",
    "rank",
    "ranking",
    "alternatives",
    "evaluate candidates",
    "evaluate options",
    "choose between",
)
WORKFLOW_KEYWORDS = (
    "build",
    "implement",
    "plan",
    "generate workflow",
    "innovation",
    "opportunities",
    "proposal",
    "proposals",
    "mvp",
    "end-to-end",
    "workflow",
    "orchestration",
)
WORKFLOW_PRIORITY_KEYWORDS = (
    "build",
    "implement",
    "plan",
    "generate workflow",
    "innovation",
    "opportunities",
    "mvp",
    "end-to-end",
    "workflow",
    "orchestration",
)

INNOVATION_KEYWORDS = (
    "innovation",
    "opportunities",
    "opportunity",
    "proposal",
    "proposals",
    "mvp",
)
MULTI_SOURCE_KEYWORDS = (
    "program",
    "docs",
    "documents",
    "repo",
    "repository",
    "context",
    "sources",
)
RESEARCH_KEYWORDS = (
    "research",
    "summarize",
    "summary",
    "brief",
    "report",
    "document",
    "documents",
    "docs",
)
COMPARE_KEYWORDS = (
    "compare",
    "rank",
    "ranking",
    "alternatives",
    "tournament",
    "choose",
)
VERIFY_KEYWORDS = (
    "critique",
    "audit",
    "review",
    "verify",
    "investigate",
    "red team",
)
GENERATE_FILTER_KEYWORDS = (
    "generate",
    "filter",
    "shortlist",
    "candidate",
    "candidates",
    "brainstorm",
)
PLAN_SOLVE_KEYWORDS = (
    "debug",
    "fix",
    "bugfix",
    "repository",
    "repo",
    "implementation",
    "implement",
    "diff",
    "pull request",
    "code change",
    "code changes",
)
REACT_PREVIEW_KEYWORDS = (
    "observe",
    "step by step",
    "iterate",
    "tool",
    "tools",
)
CLASSIFY_KEYWORDS = (
    "classify",
    "extract",
    "route",
    "decide",
    "tag",
)
LOOP_KEYWORDS = (
    "loop",
    "iterate",
    "retry",
    "until done",
    "keep trying",
)

PATTERN_PHASES = {
    "classify_and_act": [
        {
            "phase_id": "classify_input",
            "phase_name": "Classify input",
            "purpose": (
                "Sort the goal into a bounded governed task shape that would "
                "likely drive a future proposal."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_workflow_spec",
        },
        {
            "phase_id": "route_follow_up",
            "phase_name": "Route follow-up",
            "purpose": (
                "Route the likely next governed action without creating any "
                "candidate artifacts yet."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
    "fan_out_and_synthesize": [
        {
            "phase_id": "retrieve_context",
            "phase_name": "Retrieve context",
            "purpose": (
                "Collect relevant local or project context that would likely "
                "ground a future proposal."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_requested_auth",
        },
        {
            "phase_id": "fan_out_sources",
            "phase_name": "Fan out sources",
            "purpose": (
                "Read multiple governed context sources that would likely feed "
                "the proposal."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_requested_auth",
        },
        {
            "phase_id": "synthesize_findings",
            "phase_name": "Synthesize findings",
            "purpose": (
                "Combine retrieved context into candidate opportunities or "
                "proposal structure."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_approval_requests",
        },
        {
            "phase_id": "draft_mvp_plan",
            "phase_name": "Draft MVP plan",
            "purpose": (
                "Shape a likely workflow proposal and operator review story for "
                "top ideas."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
    "adversarial_verification": [
        {
            "phase_id": "inspect_subject",
            "phase_name": "Inspect subject",
            "purpose": (
                "Inspect the target artifact or proposal area that would likely "
                "be challenged."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_requested_auth",
        },
        {
            "phase_id": "challenge_assumptions",
            "phase_name": "Challenge assumptions",
            "purpose": (
                "Apply critique or verification passes to likely weak spots in "
                "the future proposal."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
        {
            "phase_id": "record_findings",
            "phase_name": "Record findings",
            "purpose": (
                "Summarize blocked, risky, or uncertain areas that would need "
                "compiler and operator scrutiny."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
    "generate_and_filter": [
        {
            "phase_id": "generate_candidates",
            "phase_name": "Generate candidates",
            "purpose": (
                "Produce a likely set of candidate approaches in preview form "
                "only."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_workflow_spec",
        },
        {
            "phase_id": "filter_candidates",
            "phase_name": "Filter candidates",
            "purpose": (
                "Reduce the candidate set to the likely shortlist for a future "
                "proposal."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
        {
            "phase_id": "shortlist_candidates",
            "phase_name": "Shortlist candidates",
            "purpose": (
                "Present the likely shortlist that would be turned into a "
                "future candidate bundle."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
    "tournament_or_ranking": [
        {
            "phase_id": "gather_candidates",
            "phase_name": "Gather candidates",
            "purpose": (
                "Collect the alternatives that would likely be compared in a "
                "future governed workflow."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_requested_auth",
        },
        {
            "phase_id": "evaluate_candidates",
            "phase_name": "Evaluate candidates",
            "purpose": (
                "Score or critique the alternatives under a likely reviewable "
                "rubric."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
        {
            "phase_id": "rank_alternatives",
            "phase_name": "Rank alternatives",
            "purpose": (
                "Produce a likely ranking outcome for a future proposal bundle."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
    "loop_until_done": [
        {
            "phase_id": "define_stop_condition",
            "phase_name": "Define stop condition",
            "purpose": (
                "State the bounded completion condition that a future proposal "
                "would likely use."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_workflow_spec",
        },
        {
            "phase_id": "iterate_step",
            "phase_name": "Iterate step",
            "purpose": (
                "Repeat a likely bounded step while keeping the flow proposal "
                "only."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_requested_auth",
        },
        {
            "phase_id": "assess_completion",
            "phase_name": "Assess completion",
            "purpose": (
                "Check the likely stop condition without implying execution or "
                "authority."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
    "plan_and_solve": [
        {
            "phase_id": "inspect_context",
            "phase_name": "Inspect context",
            "purpose": (
                "Inspect repository or task context that would likely inform a "
                "future proposal."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_requested_auth",
        },
        {
            "phase_id": "plan_changes",
            "phase_name": "Plan changes",
            "purpose": (
                "Lay out the likely ordered steps that a governed workflow "
                "would propose."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_workflow_spec",
        },
        {
            "phase_id": "verify_plan",
            "phase_name": "Verify plan",
            "purpose": (
                "Preview how the future proposal would likely check its own "
                "outputs before operator review."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
    "react_like_tool_use_preview": [
        {
            "phase_id": "observe_state",
            "phase_name": "Observe state",
            "purpose": (
                "Observe likely task state transitions without performing any "
                "tool or connector calls."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_requested_auth",
        },
        {
            "phase_id": "choose_next_action",
            "phase_name": "Choose next action",
            "purpose": (
                "Preview a likely next-step loop while keeping the result "
                "non-authoritative."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_workflow_spec",
        },
        {
            "phase_id": "iterate_observation_loop",
            "phase_name": "Iterate observation loop",
            "purpose": (
                "Bound a likely observe-act cycle without creating any runtime "
                "or broker behavior."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
    "research_synthesis": [
        {
            "phase_id": "retrieve_sources",
            "phase_name": "Retrieve sources",
            "purpose": (
                "Collect the likely governed sources that would inform a future "
                "proposal."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_requested_auth",
        },
        {
            "phase_id": "summarize_sources",
            "phase_name": "Summarize sources",
            "purpose": (
                "Condense the retrieved material into grounded intermediate "
                "notes for a future candidate workflow."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_approval_requests",
        },
        {
            "phase_id": "synthesize_report",
            "phase_name": "Synthesize report",
            "purpose": (
                "Shape the likely synthesis or report outcome that would be "
                "represented in future candidate artifacts."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
    "generic_governed_workflow": [
        {
            "phase_id": "collect_context",
            "phase_name": "Collect context",
            "purpose": (
                "Collect enough context to preview a future governed workflow "
                "without generating artifacts yet."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_requested_auth",
        },
        {
            "phase_id": "propose_structure",
            "phase_name": "Propose structure",
            "purpose": (
                "Draft the likely proposal structure that would later become "
                "candidate artifacts."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_workflow_spec",
        },
        {
            "phase_id": "surface_governance",
            "phase_name": "Surface governance",
            "purpose": (
                "Preview the likely governance surfaces that would still require "
                "compiler validation and current-run approval."
            ),
            "authority_boundary": "proposal_only",
            "approval_surface": "future_operator_review",
        },
    ],
}

PATTERN_RISK_NOTES = {
    "classify_and_act": [
        "Misclassification could route the future proposal into the wrong governed path.",
    ],
    "fan_out_and_synthesize": [
        "Potential prompt-injection risk exists if retrieved context is untrusted.",
    ],
    "adversarial_verification": [
        "Verification preview quality depends on the completeness of local evidence and review criteria.",
    ],
    "generate_and_filter": [
        "Shortlisting could discard viable options if future evaluation criteria are weak.",
    ],
    "tournament_or_ranking": [
        "Ranking outcomes could overfit incomplete evidence if candidate context is weak.",
    ],
    "loop_until_done": [
        "A future loop would need explicit stop conditions to stay bounded and reviewable.",
    ],
    "plan_and_solve": [
        "Any future code-change flow must keep repository diffs scoped, reviewable, and compiler-validated.",
    ],
    "react_like_tool_use_preview": [
        "Any future tool-like observation loop would still require compiler-authorized requested access and explicit approval.",
    ],
    "research_synthesis": [
        "Research summaries could inherit source bias or stale evidence if future retrieval scope is weak.",
    ],
    "generic_governed_workflow": [
        "The fallback preview is conservative and may omit narrower future pattern choices.",
    ],
}


def _select_strategy(goal_lower: str) -> tuple[str, list[str]]:
    matched_agent_team = _matched_keywords(goal_lower, AGENT_TEAM_KEYWORDS)
    if matched_agent_team:
        return (
            "agent_team_preview",
            [
                f"Goal mentions {', '.join(matched_agent_team[:2])}.",
                "Goal implies parallel or side-by-side evaluation of alternatives.",
            ],
        )

    matched_subagent = _matched_keywords(goal_lower, SUBAGENT_KEYWORDS)
    matched_workflow_priority = _matched_keywords(goal_lower, WORKFLOW_PRIORITY_KEYWORDS)
    if matched_subagent and not matched_workflow_priority:
        return (
            "subagent_preview",
            [
                f"Goal mentions {', '.join(matched_subagent[:2])}.",
                "Goal implies focused delegated analysis rather than direct execution.",
            ],
        )

    matched_workflow = _matched_keywords(goal_lower, WORKFLOW_KEYWORDS)
    if matched_workflow:
        return (
            "workflow_orchestration_preview",
            [
                f"Goal mentions {', '.join(matched_workflow[:2])}.",
                "Goal likely needs a multi-step governed flow with intermediate artifacts and operator review.",
            ],
        )

    if matched_subagent:
        return (
            "subagent_preview",
            [
                f"Goal mentions {', '.join(matched_subagent[:2])}.",
                "Goal implies focused delegated analysis rather than direct execution.",
            ],
        )

    matched_skill = _matched_keywords(goal_lower, SKILL_KEYWORDS)
    if matched_skill:
        return (
            "skill_preview",
            [
                f"Goal mentions {', '.join(matched_skill[:2])}.",
                "Goal looks like a bounded reusable operation that could stay narrowly scoped.",
            ],
        )

    return (
        "generic_governed_workflow_preview",
        [
            "No narrow deterministic strategy keyword dominated the goal.",
            "Fallback remains a generic governed workflow preview until a future candidate is shaped.",
        ],
    )


def _select_pattern(goal_lower: str) -> tuple[str, list[str]]:
    matched_innovation = _matched_keywords(goal_lower, INNOVATION_KEYWORDS)
    matched_multi_source = _matched_keywords(goal_lower, MULTI_SOURCE_KEYWORDS)
    if matched_innovation and matched_multi_source:
        return (
            "fan_out_and_synthesize",
            [
                f"Goal mentions {', '.join(matched_innovation[:2])}.",
                f"Goal also mentions {', '.join(matched_multi_source[:2])}, which implies multiple governed context sources.",
            ],
        )

    matched_compare = _matched_keywords(goal_lower, COMPARE_KEYWORDS)
    if matched_compare:
        return (
            "tournament_or_ranking",
            [
                f"Goal mentions {', '.join(matched_compare[:2])}.",
                "Goal implies side-by-side evaluation or ranking of alternatives.",
            ],
        )

    matched_verify = _matched_keywords(goal_lower, VERIFY_KEYWORDS)
    if matched_verify:
        return (
            "adversarial_verification",
            [
                f"Goal mentions {', '.join(matched_verify[:2])}.",
                "Goal implies critique or verification rather than a single forward pass.",
            ],
        )

    matched_classify = _matched_keywords(goal_lower, CLASSIFY_KEYWORDS)
    if matched_classify:
        return (
            "classify_and_act",
            [
                f"Goal mentions {', '.join(matched_classify[:2])}.",
                "Goal implies a bounded classify-or-route style preview.",
            ],
        )

    matched_research = _matched_keywords(goal_lower, RESEARCH_KEYWORDS)
    if matched_research:
        return (
            "research_synthesis",
            [
                f"Goal mentions {', '.join(matched_research[:2])}.",
                "Goal implies gathering and synthesizing multiple pieces of context into a governed report shape.",
            ],
        )

    matched_generate_filter = _matched_keywords(goal_lower, GENERATE_FILTER_KEYWORDS)
    if matched_generate_filter:
        return (
            "generate_and_filter",
            [
                f"Goal mentions {', '.join(matched_generate_filter[:2])}.",
                "Goal implies producing multiple candidate outputs and narrowing them down.",
            ],
        )

    matched_plan_solve = _matched_keywords(goal_lower, PLAN_SOLVE_KEYWORDS)
    if matched_plan_solve:
        matched_react = _matched_keywords(goal_lower, REACT_PREVIEW_KEYWORDS)
        if matched_react:
            return (
                "react_like_tool_use_preview",
                [
                    f"Goal mentions {', '.join(matched_plan_solve[:2])}.",
                    f"Goal also mentions {', '.join(matched_react[:2])}, which implies an iterative observe-act preview.",
                ],
            )
        return (
            "plan_and_solve",
            [
                f"Goal mentions {', '.join(matched_plan_solve[:2])}.",
                "Goal implies an ordered inspect-plan-verify shape for a future governed workflow.",
            ],
        )

    matched_loop = _matched_keywords(goal_lower, LOOP_KEYWORDS)
    if matched_loop:
        return (
            "loop_until_done",
            [
                f"Goal mentions {', '.join(matched_loop[:2])}.",
                "Goal implies a bounded repeated-step preview with an explicit stop condition.",
            ],
        )

    return (
        "generic_governed_workflow",
        [
            "No narrow deterministic pattern keyword dominated the goal.",
            "Fallback remains a generic governed workflow preview.",
        ],
    )


def _copied_expected_phases(pattern_family: str) -> list[dict[str, str]]:
    phases = PATTERN_PHASES[pattern_family]
    return [dict(phase) for phase in phases]


def preview_workflow_strategy(goal: str) -> dict[str, Any]:
    normalized_goal = _normalized_goal(goal)
    goal_lower = normalized_goal.lower()
    strategy_type, strategy_rationale = _select_strategy(goal_lower)
    pattern_family, pattern_rationale = _select_pattern(goal_lower)

    risk_notes = list(PATTERN_RISK_NOTES[pattern_family])
    risk_notes.append(
        "Future tool or connector access must be compiler-authorized and current-run operator-approved."
    )
    risk_notes.append(
        "No broker request is created and no sandbox/backend is launched by this preview."
    )

    return {
        "display_only": True,
        "non_authoritative": True,
        "not_compiler_input": True,
        "not_authority": True,
        "not_approval": True,
        "not_execution": True,
        "not_broker_request": True,
        "no_model_calls": True,
        "no_tool_calls": True,
        "selection_mode": "deterministic_baseline_preview",
        "selection_method": "deterministic_keyword_preview",
        "future_selector_ready": True,
        "future_selector_notes": [
            "This baseline is a preview and audit scaffold for future LLM/Hermes workflow selection.",
            "Future LLM/Hermes selection may choose a different workflow strategy or pattern family using richer context.",
            "Future intelligent selection must still produce compiler-validatable candidate artifacts.",
            "Compiler validation and current-run operator approval remain required after any future intelligent selection.",
        ],
        "selection_limitations": [
            "Keyword matching is used only to make this preview deterministic, testable, and auditable.",
            "Keyword matching is not the final workflow planner.",
            "The planner LLM/Hermes is expected to make richer workflow choices in a later slice.",
        ],
        "goal": normalized_goal,
        "strategy_type": strategy_type,
        "strategy_type_name": STRATEGY_TYPE_NAMES[strategy_type],
        "strategy_rationale": strategy_rationale,
        "selected_pattern_family": pattern_family,
        "selected_pattern_name": PATTERN_NAMES[pattern_family],
        "pattern_rationale": pattern_rationale,
        "expected_phases": _copied_expected_phases(pattern_family),
        "expected_candidate_artifacts": list(EXPECTED_CANDIDATE_ARTIFACTS),
        "expected_governance_surfaces": list(EXPECTED_GOVERNANCE_SURFACES),
        "risk_notes": risk_notes,
        "next_safe_step": (
            "Generate candidate artifacts only after selecting compiler-facing "
            "workflow and authority shapes; compiler validation remains required "
            "before any approval or runtime surfaces."
        ),
    }
