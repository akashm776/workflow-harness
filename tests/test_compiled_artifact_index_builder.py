from __future__ import annotations

import json
from pathlib import Path
import unittest

from compiler.canonical_json import canonical_json_text, canonical_sha256_hex
from compiler.compilation_report import build_compilation_report
from compiler.compiled_artifact_index import build_compiled_artifact_index
from compiler.dependency_digest import CANONICALIZATION_VERSION, HASH_ALGORITHM
from compiler.effective_policy import build_effective_policy
from compiler.execution_bindings import build_execution_bindings


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)


class CompiledArtifactIndexBuilderTests(unittest.TestCase):
    def test_valid_fixtures_build_stable_identity_fields(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            workflow_spec = json.loads(
                (fixture_input / "WorkflowSpec.json").read_text(encoding="utf-8")
            )
            compilation_report = build_compilation_report(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "NodeTypeRegistry.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "ApprovalRequests.json",
            )
            effective_policy = build_effective_policy(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "NodeTypeRegistry.json",
            )
            execution_bindings = build_execution_bindings(effective_policy)

            index = build_compiled_artifact_index(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "NodeTypeRegistry.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "ApprovalRequests.json",
                compilation_report,
                fixture_input / "CompilationReport.json",
                effective_policy,
                fixture_input / "EffectivePolicy.json",
                execution_bindings,
                fixture_input / "ExecutionBindings.json",
                repo_root=ROOT,
            )

            with self.subTest(fixture=fixture_name):
                self.assertEqual(index["schema_version"], "m1")
                self.assertEqual(
                    index["graph_revision_id"], workflow_spec["graph_revision_id"]
                )
                self.assertEqual(
                    index["workflow_revision_id"], workflow_spec["workflow_revision_id"]
                )
                self.assertEqual(
                    index["policy_bundle_digest"], workflow_spec["policy_bundle_digest"]
                )
                self.assertEqual(index["artifact_lifecycle_state"], "compiled")
                self.assertEqual(index["compiler_version"], "m1-local")
                self.assertEqual(index["hash_algorithm"], HASH_ALGORITHM)
                self.assertEqual(
                    index["canonicalization_version"], CANONICALIZATION_VERSION
                )

    def test_dependency_digest_entries_include_required_metadata(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compilation_report = build_compilation_report(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
        )
        effective_policy = build_effective_policy(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "NodeTypeRegistry.json",
        )
        execution_bindings = build_execution_bindings(effective_policy)

        index = build_compiled_artifact_index(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            compilation_report,
            fixture_input / "CompilationReport.json",
            effective_policy,
            fixture_input / "EffectivePolicy.json",
            execution_bindings,
            fixture_input / "ExecutionBindings.json",
            repo_root=ROOT,
        )

        entries = index["declared_input_dependency_digests"]
        self.assertEqual(len(entries), 4)
        self.assertEqual(
            {entry["artifact_group"] for entry in entries},
            {"proposal", "static_governance", "run_scoped_governance"},
        )
        for entry in entries:
            self.assertIn("artifact_path", entry)
            self.assertIn("content_digest", entry)
            self.assertEqual(entry["hash_algorithm"], HASH_ALGORITHM)
            self.assertEqual(
                entry["canonicalization_version"], CANONICALIZATION_VERSION
            )
            self.assertFalse(entry["artifact_path"].startswith("C:/"))
            self.assertFalse(entry["artifact_path"].startswith("/"))
            self.assertNotIn("Users/u230212", entry["artifact_path"])

    def test_compilation_report_artifact_entry_has_deterministic_content_digest(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compilation_report = build_compilation_report(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
        )
        effective_policy = build_effective_policy(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "NodeTypeRegistry.json",
        )
        execution_bindings = build_execution_bindings(effective_policy)

        index = build_compiled_artifact_index(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            compilation_report,
            fixture_input / "CompilationReport.json",
            effective_policy,
            fixture_input / "EffectivePolicy.json",
            execution_bindings,
            fixture_input / "ExecutionBindings.json",
            repo_root=ROOT,
        )

        self.assertEqual(
            [entry["artifact_name"] for entry in index["artifacts"]],
            ["CompilationReport", "EffectivePolicy", "ExecutionBindings"],
        )
        artifact_entry = index["artifacts"][0]
        self.assertEqual(
            artifact_entry["content_digest"], canonical_sha256_hex(compilation_report)
        )
        self.assertEqual(
            artifact_entry["artifact_revision_id"],
            compilation_report["workflow_revision_id"],
        )
        self.assertEqual(
            index["artifacts"][1]["content_digest"], canonical_sha256_hex(effective_policy)
        )
        self.assertEqual(
            index["artifacts"][2]["content_digest"],
            canonical_sha256_hex(execution_bindings),
        )
        for artifact_entry in index["artifacts"]:
            self.assertFalse(artifact_entry["artifact_path"].startswith("C:/"))
            self.assertFalse(artifact_entry["artifact_path"].startswith("/"))
            self.assertNotIn("Users/u230212", artifact_entry["artifact_path"])

    def test_compiled_artifact_index_canonical_json_is_deterministic(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compilation_report = build_compilation_report(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
        )
        effective_policy = build_effective_policy(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "NodeTypeRegistry.json",
        )
        execution_bindings = build_execution_bindings(effective_policy)

        index_left = build_compiled_artifact_index(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            compilation_report,
            fixture_input / "CompilationReport.json",
            effective_policy,
            fixture_input / "EffectivePolicy.json",
            execution_bindings,
            fixture_input / "ExecutionBindings.json",
            repo_root=ROOT,
        )
        index_right = build_compiled_artifact_index(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            compilation_report,
            fixture_input / "CompilationReport.json",
            effective_policy,
            fixture_input / "EffectivePolicy.json",
            execution_bindings,
            fixture_input / "ExecutionBindings.json",
            repo_root=ROOT,
        )

        self.assertEqual(canonical_json_text(index_left), canonical_json_text(index_right))
        self.assertEqual(
            index_left["declared_input_dependency_digests"][0]["artifact_path"],
            "fixtures/valid/simple-workflow/input/RequestedAuth.json",
        )
        self.assertEqual(
            index_left["declared_input_dependency_digests"][1]["artifact_path"],
            "fixtures/valid/simple-workflow/input/WorkflowSpec.json",
        )
        self.assertEqual(
            index_left["declared_input_dependency_digests"][2]["artifact_path"],
            "fixtures/valid/simple-workflow/input/ApprovalRequests.json",
        )
        self.assertEqual(
            index_left["declared_input_dependency_digests"][3]["artifact_path"],
            "fixtures/valid/simple-workflow/input/NodeTypeRegistry.json",
        )
        self.assertEqual(
            [entry["artifact_path"] for entry in index_left["artifacts"]],
            [
                "fixtures/valid/simple-workflow/input/CompilationReport.json",
                "fixtures/valid/simple-workflow/input/EffectivePolicy.json",
                "fixtures/valid/simple-workflow/input/ExecutionBindings.json",
            ],
        )


if __name__ == "__main__":
    unittest.main()
