"""Prompt-to-WorkflowSpec planner skeleton.

This is a deterministic stub planner. It accepts a plain-text goal and produces a
candidate input bundle shaped like the existing simple-workflow fixture. It is a
proposal generator only:

- It does not call an LLM.
- It does not infer real authority.
- It does not execute anything.
- It does not write compiled artifacts.

Planner output is **non-authoritative**. Candidate artifacts are untrusted
proposals until the deterministic compiler validates and compiles them. The
compiler remains the sole authority boundary; nothing here grants authority. The
original goal is carried only as non-authoritative metadata and is never written
into the candidate authority-bearing artifacts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any


PLANNER_VERSION = "planner-stub-v1"

# The candidate artifact files this stub proposes. NodeTypeRegistry is static
# governance and is intentionally not produced by the planner.
CANDIDATE_ARTIFACT_FILES = (
    "WorkflowSpec.json",
    "RequestedAuth.json",
    "ApprovalRequests.json",
)


def _goal_slug(goal: str) -> str:
    """Derive a stable, deterministic slug from the goal text.

    Used only to make candidate identifiers reproducible per goal. This is not
    the canonical artifact hashing and carries no authority meaning.
    """

    return hashlib.sha256(goal.encode("utf-8")).hexdigest()[:12]


def _build_workflow_spec(slug: str) -> dict[str, Any]:
    return {
        "schema_version": "m1",
        "workflow_id": f"planner-stub-workflow-{slug}",
        "graph_revision_id": f"planner-graph-rev-{slug}",
        "workflow_revision_id": f"planner-workflow-rev-{slug}",
        "policy_bundle_digest": f"planner-policy-bundle-digest-{slug}",
        "artifact_lifecycle_state": "proposed",
        "executable_run_context": {"environment": "planner-stub"},
        "nodes": [
            {
                "node_id": "retrieve-1",
                "node_type": "retrieve",
                "display_name": "Retrieve Evidence",
                "task": {"summary": "Collect one evidence bundle."},
            },
            {
                "node_id": "synthesize-1",
                "node_type": "synthesize",
                "display_name": "Synthesize Evidence",
                "task": {"summary": "Write one grounded synthesis."},
            },
        ],
        "edges": [
            {
                "from_node_id": "retrieve-1",
                "to_node_id": "synthesize-1",
                "edge_type": "data-flow",
            }
        ],
    }


def _build_requested_auth(slug: str) -> dict[str, Any]:
    return {
        "schema_version": "m1",
        "node_id": "retrieve-1",
        "workflow_revision_id": f"planner-workflow-rev-{slug}",
        "artifact_lifecycle_state": "proposed",
        "requested_tools": [
            {"tool_name": "local-file-reader", "access_mode": "read"}
        ],
        "requested_connectors": [
            {"connector_name": "fixture-catalog", "scope": "read:fixtures/simple"}
        ],
        "requested_permissions": [
            {"permission": "read", "target": "fixtures/valid/simple-workflow/input"}
        ],
    }


def _build_approval_requests(slug: str) -> dict[str, Any]:
    return {
        "schema_version": "m1",
        "workflow_revision_id": f"planner-workflow-rev-{slug}",
        "artifact_lifecycle_state": "approval_pending",
        "requests": [
            {
                "request_id": f"planner-approval-request-{slug}",
                "node_id": "retrieve-1",
                "approval_subject_hash": f"planner-approval-subject-{slug}",
                "reason": "Stub planner approval request.",
            }
        ],
    }


def build_stub_planner_candidate(goal: str) -> dict[str, Any]:
    """Build a deterministic stub candidate bundle for ``goal``.

    The return value carries the goal as non-authoritative metadata and an
    ``artifacts`` mapping of candidate-input filename -> proposed object. The
    artifacts themselves never contain the goal text.
    """

    slug = _goal_slug(goal)
    return {
        "planner_version": PLANNER_VERSION,
        "deterministic": True,
        # Non-authoritative metadata only. Not written into candidate artifacts.
        "goal": goal,
        "goal_slug": slug,
        "artifacts": {
            "WorkflowSpec.json": _build_workflow_spec(slug),
            "RequestedAuth.json": _build_requested_auth(slug),
            "ApprovalRequests.json": _build_approval_requests(slug),
        },
    }


STUB_TEMPLATE = "stub"
INNOVATION_TEMPLATE = "innovation"

# Stable keywords that select the innovation template. Matched on word boundaries
# (so "ideal" does not match "idea"); deterministic and non-authoritative.
_INNOVATION_GOAL_PATTERN = re.compile(r"\b(innovation|ideas?|mvp)\b")


def _is_innovation_goal(goal: str) -> bool:
    return _INNOVATION_GOAL_PATTERN.search(goal.lower()) is not None


def _build_innovation_workflow_spec(slug: str) -> dict[str, Any]:
    # Linear chain only: every node has at most one outgoing edge, so it compiles
    # against the simple-workflow registry (retrieve/synthesize, max_outgoing=1).
    return {
        "schema_version": "m1",
        "workflow_id": f"planner-innovation-workflow-{slug}",
        "graph_revision_id": f"planner-innovation-graph-rev-{slug}",
        "workflow_revision_id": f"planner-innovation-workflow-rev-{slug}",
        "policy_bundle_digest": f"planner-innovation-policy-bundle-digest-{slug}",
        "artifact_lifecycle_state": "proposed",
        "executable_run_context": {"environment": "planner-innovation"},
        "nodes": [
            {
                "node_id": "retrieve-1",
                "node_type": "retrieve",
                "display_name": "Load Program Data",
                "task": {"summary": "Load and inspect governed program data."},
            },
            {
                "node_id": "retrieve-2",
                "node_type": "retrieve",
                "display_name": "Gather Example Context",
                "task": {
                    "summary": (
                        "Gather example Bitbucket, Confluence, and issue-tracker "
                        "context."
                    )
                },
            },
            {
                "node_id": "synthesize-1",
                "node_type": "synthesize",
                "display_name": "Generate Idea Candidates",
                "task": {"summary": "Generate grounded idea candidates."},
            },
            {
                "node_id": "synthesize-2",
                "node_type": "synthesize",
                "display_name": "Score Against Rubric",
                "task": {"summary": "Score idea candidates against a rubric."},
            },
            {
                "node_id": "synthesize-3",
                "node_type": "synthesize",
                "display_name": "Synthesize MVP Plans",
                "task": {"summary": "Synthesize MVP plans for top ideas."},
            },
        ],
        "edges": [
            {
                "from_node_id": "retrieve-1",
                "to_node_id": "retrieve-2",
                "edge_type": "data-flow",
            },
            {
                "from_node_id": "retrieve-2",
                "to_node_id": "synthesize-1",
                "edge_type": "data-flow",
            },
            {
                "from_node_id": "synthesize-1",
                "to_node_id": "synthesize-2",
                "edge_type": "data-flow",
            },
            {
                "from_node_id": "synthesize-2",
                "to_node_id": "synthesize-3",
                "edge_type": "data-flow",
            },
        ],
    }


def _build_innovation_requested_auth(slug: str) -> dict[str, Any]:
    # Proposal-only authority. Example-prefixed connector/tool names; nothing is
    # called or executed. The compiler validates these as proposals.
    return {
        "schema_version": "m1",
        "node_id": "retrieve-1",
        "workflow_revision_id": f"planner-innovation-workflow-rev-{slug}",
        "artifact_lifecycle_state": "proposed",
        "requested_tools": [
            {"tool_name": "example-local-file-reader", "access_mode": "read"}
        ],
        "requested_connectors": [
            {"connector_name": "example-bitbucket", "scope": "read:example/repo"},
            {"connector_name": "example-confluence", "scope": "read:example/space"},
            {
                "connector_name": "example-issue-tracker",
                "scope": "read:example/project",
            },
        ],
        "requested_permissions": [
            {"permission": "read", "target": "example/program-data"}
        ],
    }


def _build_innovation_approval_requests(slug: str) -> dict[str, Any]:
    return {
        "schema_version": "m1",
        "workflow_revision_id": f"planner-innovation-workflow-rev-{slug}",
        "artifact_lifecycle_state": "approval_pending",
        "requests": [
            {
                "request_id": f"planner-innovation-approval-request-{slug}",
                "node_id": "retrieve-1",
                "approval_subject_hash": (
                    f"planner-innovation-approval-subject-{slug}"
                ),
                "reason": "Innovation template approval request.",
            }
        ],
    }


def build_innovation_planner_candidate(goal: str) -> dict[str, Any]:
    """Build a deterministic innovation-agent candidate bundle for ``goal``.

    A linear retrieve/synthesize chain with innovation-oriented metadata. It is a
    non-authoritative proposal only: it calls nothing, executes nothing, and the
    goal text is never written into the candidate artifacts.
    """

    slug = _goal_slug(goal)
    return {
        "planner_version": PLANNER_VERSION,
        "deterministic": True,
        "goal": goal,
        "goal_slug": slug,
        "artifacts": {
            "WorkflowSpec.json": _build_innovation_workflow_spec(slug),
            "RequestedAuth.json": _build_innovation_requested_auth(slug),
            "ApprovalRequests.json": _build_innovation_approval_requests(slug),
        },
    }


def select_planner_candidate(goal: str) -> tuple[str, dict[str, Any]]:
    """Select a deterministic template by goal keywords.

    Returns ``(template_name, candidate)``. The innovation template is chosen for
    innovation-style goals; otherwise the stub template is the default fallback.
    Selection is non-authoritative.
    """

    if _is_innovation_goal(goal):
        return INNOVATION_TEMPLATE, build_innovation_planner_candidate(goal)
    return STUB_TEMPLATE, build_stub_planner_candidate(goal)


def write_planner_candidate(
    candidate: dict[str, Any], output_dir: str | Path
) -> dict[str, Any]:
    """Write only the candidate input JSON files to ``output_dir``.

    Writes nothing else: no compiled artifacts, no runtime artifacts, no goal
    metadata file. Returns a manifest of what was written.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    artifacts = candidate["artifacts"]
    written: list[str] = []
    for file_name in CANDIDATE_ARTIFACT_FILES:
        artifact = artifacts[file_name]
        (output_path / file_name).write_text(
            json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written.append(file_name)

    return {
        "output_dir": str(output_path),
        "written": written,
    }
