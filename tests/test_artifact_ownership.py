from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
OWNERSHIP_REGISTRY = ROOT / "registry" / "ArtifactOwnership.json"

EXPECTED_OWNERSHIP = {
    "WorkflowSpec.json": "planner",
    "AgentCard.json": "planner",
    "Task.json": "planner",
    "RequestedAuth.json": "planner",
    "NodeReviewConfig.json": "human_governance",
    "NodeChangeRequest.json": "human_governance",
    "ApprovalDecisions.json": "human_governance",
    "ApprovalRequests.json": "compiler",
    "EffectivePolicy.json": "compiler",
    "ExecutionBindings.json": "compiler",
    "CompilationReport.json": "compiler",
    "CompiledArtifactIndex.json": "compiler",
    "EvidenceArtifact.json": "runtime",
    "EvidenceManifest.json": "runtime",
    "ExecutionManifest.json": "runtime",
    "SideEffectManifest.json": "runtime",
    "NodeRerunHistory.json": "runtime",
    "AuditLog.jsonl": "audit_subsystem",
}


def load_registry() -> dict:
    return json.loads(OWNERSHIP_REGISTRY.read_text(encoding="utf-8"))


class ArtifactOwnershipTests(unittest.TestCase):
    def test_ownership_registry_loads_as_json(self) -> None:
        payload = load_registry()
        self.assertIn("artifact_writers", payload)
        self.assertIsInstance(payload["artifact_writers"], dict)

    def test_every_canonical_artifact_has_exactly_one_allowed_writer_component(self) -> None:
        payload = load_registry()
        artifact_writers = payload["artifact_writers"]

        self.assertEqual(set(artifact_writers.keys()), set(EXPECTED_OWNERSHIP.keys()))

        for artifact_name, writer in artifact_writers.items():
            with self.subTest(artifact=artifact_name):
                self.assertIsInstance(writer, str)
                self.assertTrue(writer)
                self.assertEqual(writer, EXPECTED_OWNERSHIP[artifact_name])

    def test_compiled_authority_artifacts_are_owned_only_by_compiler(self) -> None:
        artifact_writers = load_registry()["artifact_writers"]

        for artifact_name in (
            "ApprovalRequests.json",
            "EffectivePolicy.json",
            "ExecutionBindings.json",
            "CompilationReport.json",
            "CompiledArtifactIndex.json",
        ):
            with self.subTest(artifact=artifact_name):
                self.assertEqual(artifact_writers[artifact_name], "compiler")

    def test_human_governance_owned_artifacts_do_not_include_compiled_authority_artifacts(self) -> None:
        artifact_writers = load_registry()["artifact_writers"]
        human_governance_artifacts = {
            artifact_name
            for artifact_name, writer in artifact_writers.items()
            if writer == "human_governance"
        }

        self.assertNotIn("EffectivePolicy.json", human_governance_artifacts)
        self.assertNotIn("ExecutionBindings.json", human_governance_artifacts)
        self.assertNotIn("CompiledArtifactIndex.json", human_governance_artifacts)


if __name__ == "__main__":
    unittest.main()
