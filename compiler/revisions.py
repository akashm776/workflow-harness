"""Revision and digest helpers for deterministic M1 identity computation."""

from __future__ import annotations

from typing import Any, Mapping

from .canonical_json import canonical_sha256_hex


def compute_graph_revision_id(graph_payload: Mapping[str, Any]) -> str:
    """Compute the graph-only revision id from graph structure."""

    return canonical_sha256_hex(graph_payload)


def compute_workflow_revision_id(
    *,
    graph_revision_id: str,
    policy_bundle_digest: str,
    executable_run_context: Mapping[str, Any],
) -> str:
    """Compute workflow revision id from graph revision, policy digest, and run context."""

    return canonical_sha256_hex(
        {
            "graph_revision_id": graph_revision_id,
            "policy_bundle_digest": policy_bundle_digest,
            "executable_run_context": executable_run_context,
        }
    )


def compute_node_revision_id(node_payload: Mapping[str, Any]) -> str:
    """Compute node revision id from node-local execution-relevant inputs."""

    return canonical_sha256_hex(node_payload)


def compute_approval_subject_hash(subject_payload: Mapping[str, Any]) -> str:
    """Compute approval-subject hash from canonical authority-bearing subject payload."""

    return canonical_sha256_hex(subject_payload)
