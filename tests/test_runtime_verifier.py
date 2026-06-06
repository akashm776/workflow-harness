from __future__ import annotations

from pathlib import Path
import unittest

from compiler.canonical_json import canonical_sha256_hex
from compiler.compile_run import compile_static_artifacts
from runtime.runtime_verifier import verify_node_start


ROOT = Path(__file__).resolve().parent.parent


class RuntimeVerifierTests(unittest.TestCase):
    def test_compiled_artifacts_with_review_required_true_are_rejected(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
            approval_decisions_path=fixture_input / "ApprovalDecisions-empty.json",
        )

        verifier_result = verify_node_start(
            compile_result["artifacts"].get("EffectivePolicy.json"),
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compile_result["artifacts"].get("CompiledArtifactIndex.json"),
            "retrieve-1",
        )

        self.assertTrue(compile_result["ok"])
        self.assertEqual(
            verifier_result,
            {
                "ok": False,
                "message": "approval required before node may start",
            },
        )

    def test_verifier_accepts_matching_compiled_artifacts_when_review_not_required(
        self,
    ) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        verifier_result = verify_node_start(
            compile_result["artifacts"].get("EffectivePolicy.json"),
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compile_result["artifacts"].get("CompiledArtifactIndex.json"),
            "retrieve-1",
        )

        self.assertEqual(verifier_result, {"ok": True, "message": "node may start"})

    def test_verifier_rejects_mismatched_node_id(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = canonical_sha256_hex(effective_policy)

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "synthesize-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertIn("node_id mismatch", verifier_result["message"])

    def test_verifier_rejects_missing_indexed_execution_bindings_artifact(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact)
            for artifact in compiled_artifact_index["artifacts"]
            if artifact["artifact_name"] != "ExecutionBindings"
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = canonical_sha256_hex(effective_policy)

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertIn("missing required artifacts", verifier_result["message"])

    def test_verifier_rejects_workflow_identity_mismatch(self) -> None:
        fixture_input = (
            ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
        )
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        execution_bindings = dict(compile_result["artifacts"]["ExecutionBindings.json"])
        execution_bindings["workflow_revision_id"] = "workflow-rev-mismatch-001"
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = canonical_sha256_hex(effective_policy)

        verifier_result = verify_node_start(
            effective_policy,
            execution_bindings,
            compiled_artifact_index,
            "execute-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertIn("workflow revision mismatch", verifier_result["message"])

    def test_verifier_rejects_effective_policy_artifact_revision_mismatch(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = canonical_sha256_hex(effective_policy)
                artifact["artifact_revision_id"] = "workflow-rev-mismatch-effective-policy"

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "effective policy artifact revision mismatch"
        )

    def test_verifier_rejects_effective_policy_artifact_revision_missing(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = canonical_sha256_hex(effective_policy)
                artifact["artifact_revision_id"] = ""

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "effective policy artifact revision missing"
        )

    def test_verifier_rejects_execution_bindings_artifact_revision_mismatch(self) -> None:
        fixture_input = (
            ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
        )
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = canonical_sha256_hex(effective_policy)
            if artifact["artifact_name"] == "ExecutionBindings":
                artifact["artifact_revision_id"] = (
                    "workflow-rev-mismatch-execution-bindings"
                )

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "execute-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "execution bindings artifact revision mismatch"
        )

    def test_verifier_rejects_execution_bindings_artifact_revision_missing(self) -> None:
        fixture_input = (
            ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
        )
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = canonical_sha256_hex(effective_policy)
            if artifact["artifact_name"] == "ExecutionBindings":
                artifact["artifact_revision_id"] = ""

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "execute-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "execution bindings artifact revision missing"
        )

    def test_verifier_rejects_effective_policy_wrong_filename_artifact_path(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["artifact_path"] = (
                    "fixtures/valid/simple-workflow/input/WrongEffectivePolicy.json"
                )

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "effective policy artifact path mismatch"
        )

    def test_verifier_rejects_effective_policy_backslash_artifact_path(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["artifact_path"] = (
                    "fixtures\\valid\\simple-workflow\\input\\EffectivePolicy.json"
                )

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "effective policy artifact path mismatch"
        )

    def test_verifier_rejects_effective_policy_absolute_posix_artifact_path(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["artifact_path"] = "/tmp/EffectivePolicy.json"

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "effective policy artifact path mismatch"
        )

    def test_verifier_rejects_execution_bindings_windows_artifact_path(self) -> None:
        fixture_input = (
            ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
        )
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "ExecutionBindings":
                artifact["artifact_path"] = (
                    "C:/Users/u230212/workflow-harness/ExecutionBindings.json"
                )

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "execute-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "execution bindings artifact path mismatch"
        )

    def test_verifier_rejects_effective_policy_traversal_artifact_path(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["artifact_path"] = "../EffectivePolicy.json"

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "effective policy artifact path mismatch"
        )

    def test_verifier_rejects_effective_policy_digest_mismatch(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = "digest-mismatch-effective-policy"

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertIn("effective policy content digest mismatch", verifier_result["message"])

    def test_verifier_rejects_effective_policy_digest_missing(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = ""

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "effective policy content digest missing"
        )

    def test_verifier_rejects_execution_bindings_digest_mismatch(self) -> None:
        fixture_input = (
            ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
        )
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = canonical_sha256_hex(effective_policy)
            if artifact["artifact_name"] == "ExecutionBindings":
                artifact["content_digest"] = "digest-mismatch-execution-bindings"

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "execute-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertIn(
            "execution bindings content digest mismatch", verifier_result["message"]
        )

    def test_verifier_rejects_execution_bindings_digest_missing(self) -> None:
        fixture_input = (
            ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
        )
        compile_result = compile_static_artifacts(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        effective_policy = dict(compile_result["artifacts"]["EffectivePolicy.json"])
        effective_policy["review_required"] = False
        compiled_artifact_index = dict(
            compile_result["artifacts"]["CompiledArtifactIndex.json"]
        )
        compiled_artifact_index["artifacts"] = [
            dict(artifact) for artifact in compiled_artifact_index["artifacts"]
        ]
        for artifact in compiled_artifact_index["artifacts"]:
            if artifact["artifact_name"] == "EffectivePolicy":
                artifact["content_digest"] = canonical_sha256_hex(effective_policy)
            if artifact["artifact_name"] == "ExecutionBindings":
                artifact["content_digest"] = ""

        verifier_result = verify_node_start(
            effective_policy,
            compile_result["artifacts"].get("ExecutionBindings.json"),
            compiled_artifact_index,
            "execute-1",
        )

        self.assertFalse(verifier_result["ok"])
        self.assertEqual(
            verifier_result["message"], "execution bindings content digest missing"
        )


if __name__ == "__main__":
    unittest.main()
