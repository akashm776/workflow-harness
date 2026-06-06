from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)


def load_fixture_json(fixture_name: str, file_name: str) -> dict:
    fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
    return json.loads((fixture_input / file_name).read_text(encoding="utf-8"))


class FixtureIdentityConsistencyTests(unittest.TestCase):
    def test_workflow_revision_id_matches_across_workflow_scoped_artifacts(self) -> None:
        for fixture_name in VALID_FIXTURES:
            expected = load_fixture_json(fixture_name, "WorkflowSpec.json")["workflow_revision_id"]

            for file_name in (
                "WorkflowSpec.json",
                "RequestedAuth.json",
                "ApprovalRequests.json",
                "ApprovalDecisions.json",
                "EffectivePolicy.json",
                "ExecutionBindings.json",
                "CompilationReport.json",
                "CompiledArtifactIndex.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=file_name):
                    payload = load_fixture_json(fixture_name, file_name)
                    self.assertEqual(payload["workflow_revision_id"], expected)

    def test_graph_revision_id_matches_across_graph_scoped_artifacts(self) -> None:
        for fixture_name in VALID_FIXTURES:
            expected = load_fixture_json(fixture_name, "WorkflowSpec.json")["graph_revision_id"]

            for file_name in (
                "WorkflowSpec.json",
                "CompilationReport.json",
                "CompiledArtifactIndex.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=file_name):
                    payload = load_fixture_json(fixture_name, file_name)
                    self.assertEqual(payload["graph_revision_id"], expected)

    def test_policy_bundle_digest_matches_across_policy_scoped_artifacts(self) -> None:
        for fixture_name in VALID_FIXTURES:
            expected = load_fixture_json(fixture_name, "WorkflowSpec.json")["policy_bundle_digest"]

            for file_name in (
                "WorkflowSpec.json",
                "EffectivePolicy.json",
                "ExecutionBindings.json",
                "CompilationReport.json",
                "CompiledArtifactIndex.json",
            ):
                with self.subTest(fixture=fixture_name, artifact=file_name):
                    payload = load_fixture_json(fixture_name, file_name)
                    self.assertEqual(payload["policy_bundle_digest"], expected)

    def test_compiled_artifact_index_artifact_paths_exist(self) -> None:
        for fixture_name in VALID_FIXTURES:
            artifact_index = load_fixture_json(fixture_name, "CompiledArtifactIndex.json")

            for artifact in artifact_index["artifacts"]:
                with self.subTest(fixture=fixture_name, artifact_path=artifact["artifact_path"]):
                    artifact_path = ROOT / Path(artifact["artifact_path"])
                    self.assertTrue(artifact_path.is_file(), artifact["artifact_path"])

    def test_compiled_artifact_index_dependency_paths_exist(self) -> None:
        for fixture_name in VALID_FIXTURES:
            artifact_index = load_fixture_json(fixture_name, "CompiledArtifactIndex.json")

            for dependency in artifact_index["declared_input_dependency_digests"]:
                with self.subTest(fixture=fixture_name, artifact_path=dependency["artifact_path"]):
                    artifact_path = ROOT / Path(dependency["artifact_path"])
                    self.assertTrue(artifact_path.is_file(), dependency["artifact_path"])


if __name__ == "__main__":
    unittest.main()
