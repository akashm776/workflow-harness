from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"


class SchemaSanityTests(unittest.TestCase):
    def test_all_schema_files_load_as_json_and_have_required_top_level_fields(self) -> None:
        schema_files = sorted(SCHEMA_DIR.glob("*.schema.json"))
        self.assertGreater(len(schema_files), 0, "expected at least one schema file")

        for schema_path in schema_files:
            with self.subTest(schema=schema_path.name):
                data = json.loads(schema_path.read_text(encoding="utf-8"))
                self.assertIn("$schema", data)
                self.assertIn("title", data)
                self.assertIn("type", data)

    def test_workflow_spec_schema_requires_core_identity_and_node_fields(self) -> None:
        schema_path = SCHEMA_DIR / "WorkflowSpec.schema.json"
        data = json.loads(schema_path.read_text(encoding="utf-8"))

        for field in (
            "workflow_id",
            "graph_revision_id",
            "workflow_revision_id",
            "policy_bundle_digest",
            "nodes",
            "edges",
        ):
            self.assertIn(field, data["required"])

        node_items = data["properties"]["nodes"]["items"]
        self.assertEqual(node_items["type"], "object")
        self.assertIn("node_id", node_items["required"])
        self.assertIn("node_type", node_items["required"])
        self.assertIn("node_id", node_items["properties"])
        self.assertIn("node_type", node_items["properties"])

    def test_compiled_artifact_index_schema_requires_dependency_digest_contract(self) -> None:
        schema_path = SCHEMA_DIR / "CompiledArtifactIndex.schema.json"
        data = json.loads(schema_path.read_text(encoding="utf-8"))

        for field in (
            "graph_revision_id",
            "workflow_revision_id",
            "policy_bundle_digest",
            "compiler_version",
            "hash_algorithm",
            "canonicalization_version",
            "declared_input_dependency_digests",
            "artifacts",
        ):
            self.assertIn(field, data["required"])

        digest_items = data["properties"]["declared_input_dependency_digests"]["items"]
        self.assertEqual(digest_items["type"], "object")

        for field in (
            "artifact_group",
            "artifact_path",
            "content_digest",
            "hash_algorithm",
            "canonicalization_version",
        ):
            self.assertIn(field, digest_items["required"])
            self.assertIn(field, digest_items["properties"])

        artifact_items = data["properties"]["artifacts"]["items"]
        self.assertEqual(data["properties"]["artifacts"]["minItems"], 1)
        self.assertEqual(artifact_items["type"], "object")

        for field in (
            "artifact_name",
            "artifact_path",
            "content_digest",
        ):
            self.assertIn(field, artifact_items["required"])
            self.assertIn(field, artifact_items["properties"])


if __name__ == "__main__":
    unittest.main()
