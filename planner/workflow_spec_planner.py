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
