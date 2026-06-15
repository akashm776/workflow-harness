from __future__ import annotations

import json
from pathlib import Path
import shutil
from tests.test_temp_utils import temporary_test_directory
import unittest

from compiler.canonical_json import canonical_json_text
from compiler.compile_run import compile_static_artifacts, summarize_compile_result
from compiler.authority_value_validator import find_disallowed_authority_values
from planner.workflow_spec_planner import (
    CANDIDATE_ARTIFACT_FILES,
    build_innovation_planner_candidate,
    build_innovation_review_planner_candidate,
    select_planner_candidate,
)


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_NODE_TYPE_REGISTRY = (
    ROOT / "fixtures" / "valid" / "simple-workflow" / "input" / "NodeTypeRegistry.json"
)


class InnovationPlannerTests(unittest.TestCase):
    def test_deterministic_for_same_goal(self) -> None:
        left = build_innovation_planner_candidate("generate innovation ideas")
        right = build_innovation_planner_candidate("generate innovation ideas")
        self.assertEqual(canonical_json_text(left), canonical_json_text(right))

    def test_selector_picks_innovation_for_keyword_goals(self) -> None:
        for goal in (
            "drive innovation this quarter",
            "brainstorm a new idea",
            "collect ideas for Q3",
            "build an mvp plan",
            "MVP for the new product",
        ):
            with self.subTest(goal=goal):
                template, _ = select_planner_candidate(goal)
                self.assertEqual(template, "innovation")

    def test_selector_does_not_match_substring_only_words(self) -> None:
        # "ideal" contains "idea" but must not select the innovation template.
        for goal in (
            "find the ideal candidate",
            "ideally summarize the report",
        ):
            with self.subTest(goal=goal):
                template, _ = select_planner_candidate(goal)
                self.assertEqual(template, "stub")

    def test_selector_falls_back_to_stub_for_unrelated_goals(self) -> None:
        for goal in (
            "summarize the quarterly report",
            "process program data",
            "retrieve evidence",
        ):
            with self.subTest(goal=goal):
                template, _ = select_planner_candidate(goal)
                self.assertEqual(template, "stub")

    def test_explicit_selector_can_choose_innovation_review(self) -> None:
        template, candidate = select_planner_candidate(
            "summarize the quarterly report",
            template_name="innovation_review",
        )
        self.assertEqual(template, "innovation_review")
        self.assertEqual(
            candidate["artifacts"]["WorkflowSpec.json"]["nodes"][2]["node_id"],
            "dedupe-1",
        )

    def test_uses_only_retrieve_and_synthesize_node_types(self) -> None:
        candidate = build_innovation_planner_candidate("innovation ideas")
        node_types = {
            node["node_type"]
            for node in candidate["artifacts"]["WorkflowSpec.json"]["nodes"]
        }
        self.assertTrue(node_types.issubset({"retrieve", "synthesize"}))

    def test_graph_is_linear_with_fan_out_at_most_one(self) -> None:
        spec = build_innovation_planner_candidate("innovation ideas")[
            "artifacts"
        ]["WorkflowSpec.json"]
        from_counts: dict[str, int] = {}
        for edge in spec["edges"]:
            from_counts[edge["from_node_id"]] = (
                from_counts.get(edge["from_node_id"], 0) + 1
            )
        self.assertTrue(all(count <= 1 for count in from_counts.values()))
        # Entry node is retrieve-1.
        self.assertEqual(spec["nodes"][0]["node_id"], "retrieve-1")

    def test_no_disallowed_authority_values(self) -> None:
        candidate = build_innovation_planner_candidate("innovation ideas")
        for artifact in candidate["artifacts"].values():
            self.assertEqual(find_disallowed_authority_values(artifact), [])

    def test_compiles_against_simple_registry(self) -> None:
        candidate = build_innovation_planner_candidate("innovation ideas")
        with temporary_test_directory('innovation-planner-tests') as tmp:
            tmp_dir = Path(tmp)
            for file_name in CANDIDATE_ARTIFACT_FILES:
                (tmp_dir / file_name).write_text(
                    json.dumps(candidate["artifacts"][file_name]), encoding="utf-8"
                )
            shutil.copy(SIMPLE_NODE_TYPE_REGISTRY, tmp_dir / "NodeTypeRegistry.json")

            result = compile_static_artifacts(
                tmp_dir / "WorkflowSpec.json",
                tmp_dir / "NodeTypeRegistry.json",
                tmp_dir / "RequestedAuth.json",
                tmp_dir / "ApprovalRequests.json",
                repo_root=tmp_dir,
            )
            summary = summarize_compile_result(result)
            self.assertTrue(summary["ok"])
            self.assertEqual(summary["compilation_status"], "compiled")

    def test_goal_text_not_in_candidate_artifacts(self) -> None:
        goal = "innovation SENTINELZZZ ideas"
        candidate = build_innovation_planner_candidate(goal)
        for artifact in candidate["artifacts"].values():
            self.assertNotIn("SENTINELZZZ", canonical_json_text(artifact))

    def test_requested_auth_example_prefixed_and_proposal_only(self) -> None:
        requested_auth = build_innovation_planner_candidate("innovation ideas")[
            "artifacts"
        ]["RequestedAuth.json"]
        self.assertEqual(requested_auth["artifact_lifecycle_state"], "proposed")
        for connector in requested_auth["requested_connectors"]:
            self.assertTrue(
                connector["connector_name"].startswith("example-"),
                connector["connector_name"],
            )
            self.assertIsInstance(connector["scope"], str)
        for tool in requested_auth["requested_tools"]:
            self.assertTrue(tool["tool_name"].startswith("example-"))

    def test_innovation_review_is_deterministic_for_same_goal(self) -> None:
        left = build_innovation_review_planner_candidate("review innovation options")
        right = build_innovation_review_planner_candidate("review innovation options")
        self.assertEqual(canonical_json_text(left), canonical_json_text(right))

    def test_innovation_review_has_expected_linear_chain(self) -> None:
        spec = build_innovation_review_planner_candidate("review innovation options")[
            "artifacts"
        ]["WorkflowSpec.json"]

        nodes = [(node["node_id"], node["display_name"]) for node in spec["nodes"]]
        self.assertEqual(
            nodes,
            [
                ("retrieve-1", "Load Program Data"),
                ("retrieve-2", "Gather Example Context"),
                ("dedupe-1", "Dedupe Against Existing Work"),
                ("synthesize-1", "Generate Idea Candidates"),
                ("score-1", "Score Against Rubric"),
                ("critique-1", "Critique Top Ideas"),
                ("synthesize-2", "Synthesize MVP Plans"),
            ],
        )
        self.assertEqual(
            [(edge["from_node_id"], edge["to_node_id"]) for edge in spec["edges"]],
            [
                ("retrieve-1", "retrieve-2"),
                ("retrieve-2", "dedupe-1"),
                ("dedupe-1", "synthesize-1"),
                ("synthesize-1", "score-1"),
                ("score-1", "critique-1"),
                ("critique-1", "synthesize-2"),
            ],
        )

    def test_innovation_review_compiles_against_simple_registry(self) -> None:
        candidate = build_innovation_review_planner_candidate("review innovation options")
        with temporary_test_directory('innovation-planner-tests') as tmp:
            tmp_dir = Path(tmp)
            for file_name in CANDIDATE_ARTIFACT_FILES:
                (tmp_dir / file_name).write_text(
                    json.dumps(candidate["artifacts"][file_name]), encoding="utf-8"
                )
            shutil.copy(SIMPLE_NODE_TYPE_REGISTRY, tmp_dir / "NodeTypeRegistry.json")

            result = compile_static_artifacts(
                tmp_dir / "WorkflowSpec.json",
                tmp_dir / "NodeTypeRegistry.json",
                tmp_dir / "RequestedAuth.json",
                tmp_dir / "ApprovalRequests.json",
                repo_root=tmp_dir,
            )
            summary = summarize_compile_result(result)
            self.assertTrue(summary["ok"])
            self.assertEqual(summary["compilation_status"], "compiled")

    def test_innovation_review_contains_no_unsupported_execution_binding_fields(
        self,
    ) -> None:
        nodes = build_innovation_review_planner_candidate("review innovation options")[
            "artifacts"
        ]["WorkflowSpec.json"]["nodes"]
        for node in nodes:
            for forbidden_key in (
                "tool_binding",
                "tool_access",
                "connector_binding",
                "connector_access",
                "broker_binding",
                "mcp",
                "mcp_binding",
                "mcp_server",
                "mcp_tool",
            ):
                self.assertNotIn(forbidden_key, node)


if __name__ == "__main__":
    unittest.main()
