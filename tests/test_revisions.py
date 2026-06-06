from __future__ import annotations

import unittest

from compiler.revisions import (
    compute_approval_subject_hash,
    compute_graph_revision_id,
    compute_node_revision_id,
    compute_workflow_revision_id,
)


class RevisionTests(unittest.TestCase):
    def test_graph_revision_id_is_stable_for_equivalent_graph_payload(self) -> None:
        left = {"edges": [["a", "b"]], "nodes": ["a", "b"]}
        right = {"nodes": ["a", "b"], "edges": [["a", "b"]]}

        self.assertEqual(compute_graph_revision_id(left), compute_graph_revision_id(right))

    def test_workflow_revision_changes_with_policy_bundle_digest(self) -> None:
        run_context = {"mode": "review"}
        graph_revision_id = compute_graph_revision_id({"nodes": ["a"], "edges": []})

        left = compute_workflow_revision_id(
            graph_revision_id=graph_revision_id,
            policy_bundle_digest="digest-a",
            executable_run_context=run_context,
        )
        right = compute_workflow_revision_id(
            graph_revision_id=graph_revision_id,
            policy_bundle_digest="digest-b",
            executable_run_context=run_context,
        )

        self.assertNotEqual(left, right)

    def test_workflow_revision_changes_with_executable_run_context(self) -> None:
        graph_revision_id = compute_graph_revision_id({"nodes": ["a"], "edges": []})

        left = compute_workflow_revision_id(
            graph_revision_id=graph_revision_id,
            policy_bundle_digest="digest-a",
            executable_run_context={"mode": "review"},
        )
        right = compute_workflow_revision_id(
            graph_revision_id=graph_revision_id,
            policy_bundle_digest="digest-a",
            executable_run_context={"mode": "autopilot"},
        )

        self.assertNotEqual(left, right)

    def test_node_revision_changes_with_node_local_input_change(self) -> None:
        left = {"node_id": "retrieve-1", "query": "alpha"}
        right = {"node_id": "retrieve-1", "query": "beta"}

        self.assertNotEqual(compute_node_revision_id(left), compute_node_revision_id(right))

    def test_approval_subject_hash_changes_when_authority_changes(self) -> None:
        left = {"permission": "jira.read", "scope": {"project": "ABC"}}
        right = {"permission": "jira.read", "scope": {"project": "XYZ"}}

        self.assertNotEqual(
            compute_approval_subject_hash(left),
            compute_approval_subject_hash(right),
        )


if __name__ == "__main__":
    unittest.main()
