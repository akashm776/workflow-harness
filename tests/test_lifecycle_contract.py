from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
LIFECYCLE_REGISTRY = ROOT / "registry" / "LifecycleStates.json"
FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

LIFECYCLE_ARTIFACTS = (
    "WorkflowSpec.json",
    "RequestedAuth.json",
    "ApprovalRequests.json",
    "ApprovalDecisions.json",
    "EffectivePolicy.json",
    "ExecutionBindings.json",
    "CompilationReport.json",
    "CompiledArtifactIndex.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class LifecycleContractTests(unittest.TestCase):
    def test_lifecycle_registry_loads_and_declares_artifact_local_field(self) -> None:
        payload = load_json(LIFECYCLE_REGISTRY)
        self.assertEqual(payload["field_name"], "artifact_lifecycle_state")
        self.assertIn("artifact-local", payload["note"])
        self.assertIn("allowed_states", payload)
        self.assertEqual(len(payload["allowed_states"]), len(set(payload["allowed_states"])))

    def test_simple_workflow_artifact_lifecycle_state_is_present_and_allowed(self) -> None:
        allowed_states = set(load_json(LIFECYCLE_REGISTRY)["allowed_states"])

        for file_name in LIFECYCLE_ARTIFACTS:
            with self.subTest(artifact=file_name):
                payload = load_json(FIXTURE_INPUT / file_name)
                self.assertIn("artifact_lifecycle_state", payload)
                self.assertIn(payload["artifact_lifecycle_state"], allowed_states)


if __name__ == "__main__":
    unittest.main()
