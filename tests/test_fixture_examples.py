from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)


EXAMPLE_FILES = {
    "WorkflowSpec.json": {
        "schema": "WorkflowSpec.schema.json",
        "required_fields": [
            "workflow_id",
            "graph_revision_id",
            "workflow_revision_id",
            "policy_bundle_digest",
            "artifact_lifecycle_state",
            "nodes",
            "edges",
        ],
    },
    "NodeTypeRegistry.json": {
        "schema": "NodeTypeRegistry.schema.json",
        "required_fields": [
            "registry_version",
            "node_types",
        ],
    },
    "RequestedAuth.json": {
        "schema": "RequestedAuth.schema.json",
        "required_fields": [
            "node_id",
            "workflow_revision_id",
            "artifact_lifecycle_state",
        ],
    },
    "ApprovalRequests.json": {
        "schema": "ApprovalRequests.schema.json",
        "required_fields": [
            "workflow_revision_id",
            "artifact_lifecycle_state",
            "requests",
        ],
    },
    "ApprovalDecisions.json": {
        "schema": "ApprovalDecisions.schema.json",
        "required_fields": [
            "workflow_revision_id",
            "artifact_lifecycle_state",
            "decisions",
        ],
    },
    "EffectivePolicy.json": {
        "schema": "EffectivePolicy.schema.json",
        "required_fields": [
            "node_id",
            "workflow_revision_id",
            "policy_bundle_digest",
            "artifact_lifecycle_state",
        ],
    },
    "ExecutionBindings.json": {
        "schema": "ExecutionBindings.schema.json",
        "required_fields": [
            "node_id",
            "workflow_revision_id",
            "policy_bundle_digest",
            "artifact_lifecycle_state",
        ],
    },
    "CompilationReport.json": {
        "schema": "CompilationReport.schema.json",
        "required_fields": [
            "graph_revision_id",
            "workflow_revision_id",
            "policy_bundle_digest",
            "artifact_lifecycle_state",
            "status",
        ],
    },
    "CompiledArtifactIndex.json": {
        "schema": "CompiledArtifactIndex.schema.json",
        "required_fields": [
            "graph_revision_id",
            "workflow_revision_id",
            "policy_bundle_digest",
            "artifact_lifecycle_state",
            "compiler_version",
            "hash_algorithm",
            "canonicalization_version",
            "declared_input_dependency_digests",
            "artifacts",
        ],
    },
    "AuditEvent.json": {
        "schema": "AuditEvent.schema.json",
        "required_fields": [
            "event_id",
            "timestamp",
            "event_type",
            "actor",
        ],
    },
}


class FixtureExampleTests(unittest.TestCase):
    def test_valid_fixture_example_files_and_matching_schemas_load(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            for file_name, contract in EXAMPLE_FILES.items():
                with self.subTest(fixture=fixture_name, artifact=file_name):
                    payload = json.loads((fixture_input / file_name).read_text(encoding="utf-8"))
                    schema = json.loads((SCHEMAS / contract["schema"]).read_text(encoding="utf-8"))

                    self.assertIn("$schema", schema)
                    self.assertIn("title", schema)
                    self.assertIn("type", schema)
                    self.assertIn("required", schema)

                    for field in contract["required_fields"]:
                        self.assertIn(field, payload)
                        self.assertIn(field, schema["required"])

    def test_valid_workflows_have_top_level_edges(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            workflow = json.loads((fixture_input / "WorkflowSpec.json").read_text(encoding="utf-8"))
            with self.subTest(fixture=fixture_name):
                self.assertIn("edges", workflow)
                self.assertIsInstance(workflow["edges"], list)
                self.assertGreater(len(workflow["edges"]), 0)

    def test_valid_workflows_have_non_empty_compiled_artifacts(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            artifact_index = json.loads((fixture_input / "CompiledArtifactIndex.json").read_text(encoding="utf-8"))
            with self.subTest(fixture=fixture_name):
                self.assertIn("artifacts", artifact_index)
                self.assertIsInstance(artifact_index["artifacts"], list)
                self.assertGreater(len(artifact_index["artifacts"]), 0)

    def test_valid_node_type_registry_entries_declare_max_outgoing_edges(self) -> None:
        schema = json.loads((SCHEMAS / "NodeTypeRegistry.schema.json").read_text(encoding="utf-8"))
        registry_item_schema = schema["properties"]["node_types"]["items"]

        self.assertIn("max_outgoing_edges", registry_item_schema["required"])
        self.assertIn("max_outgoing_edges", registry_item_schema["properties"])

        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            registry = json.loads((fixture_input / "NodeTypeRegistry.json").read_text(encoding="utf-8"))

            for entry in registry["node_types"]:
                with self.subTest(fixture=fixture_name, node_type=entry["node_type"]):
                    self.assertIn("max_outgoing_edges", entry)
                    self.assertIsInstance(entry["max_outgoing_edges"], int)
                    self.assertGreaterEqual(entry["max_outgoing_edges"], 0)


if __name__ == "__main__":
    unittest.main()
