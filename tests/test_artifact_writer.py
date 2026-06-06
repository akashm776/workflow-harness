from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from compiler.artifact_writer import write_compiled_artifacts
from compiler.compile_run import compile_static_artifacts
from runtime.runtime_verifier import verify_node_start


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"


class ArtifactWriterTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"artifact-writer-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_valid_approved_compile_writes_all_four_artifacts(self) -> None:
        compile_result = compile_static_artifacts(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        output_dir = self._make_output_dir()
        manifest = write_compiled_artifacts(compile_result, output_dir)

        self.assertEqual(
            manifest,
            {
                "ok": True,
                "output_dir": str(output_dir),
                "written_artifacts": [
                    "CompilationReport.json",
                    "CompiledArtifactIndex.json",
                    "EffectivePolicy.json",
                    "ExecutionBindings.json",
                ],
            },
        )
        for artifact_name in manifest["written_artifacts"]:
            self.assertTrue((output_dir / artifact_name).exists())

    def test_failed_compile_writes_only_compilation_report_and_index(self) -> None:
        compile_result = compile_static_artifacts(
            UNKNOWN_NODE_TYPE / "WorkflowSpec.json",
            UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json",
            UNKNOWN_NODE_TYPE / "RequestedAuth.json",
            UNKNOWN_NODE_TYPE / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        output_dir = self._make_output_dir()
        manifest = write_compiled_artifacts(compile_result, output_dir)

        self.assertEqual(
            manifest["written_artifacts"],
            ["CompilationReport.json", "CompiledArtifactIndex.json"],
        )
        self.assertFalse((output_dir / "EffectivePolicy.json").exists())
        self.assertFalse((output_dir / "ExecutionBindings.json").exists())

    def test_writer_refuses_overwrite_by_default(self) -> None:
        compile_result = compile_static_artifacts(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        output_dir = self._make_output_dir()
        write_compiled_artifacts(compile_result, output_dir)

        with self.assertRaises(FileExistsError):
            write_compiled_artifacts(compile_result, output_dir)

    def test_written_index_uses_bundle_relative_artifact_paths(self) -> None:
        compile_result = compile_static_artifacts(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        output_dir = self._make_output_dir()
        write_compiled_artifacts(compile_result, output_dir)
        reloaded_index = json.loads(
            (output_dir / "CompiledArtifactIndex.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            [entry["artifact_path"] for entry in reloaded_index["artifacts"]],
            [
                "CompilationReport.json",
                "EffectivePolicy.json",
                "ExecutionBindings.json",
            ],
        )

    def test_original_compile_result_is_unchanged_after_writing(self) -> None:
        compile_result = compile_static_artifacts(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        original_snapshot = deepcopy(compile_result)

        output_dir = self._make_output_dir()
        write_compiled_artifacts(compile_result, output_dir)

        self.assertEqual(compile_result, original_snapshot)

    def test_written_json_reloads_and_matches_original_dicts_except_rebased_index(
        self,
    ) -> None:
        compile_result = compile_static_artifacts(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        output_dir = self._make_output_dir()
        write_compiled_artifacts(compile_result, output_dir)

        for artifact_name in (
            "CompilationReport.json",
            "EffectivePolicy.json",
            "ExecutionBindings.json",
        ):
            with self.subTest(artifact=artifact_name):
                reloaded = json.loads(
                    (output_dir / artifact_name).read_text(encoding="utf-8")
                )
                self.assertEqual(reloaded, compile_result["artifacts"][artifact_name])

    def test_runtime_verifier_accepts_reloaded_written_artifacts_for_approved_workflow(
        self,
    ) -> None:
        compile_result = compile_static_artifacts(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        output_dir = self._make_output_dir()
        write_compiled_artifacts(compile_result, output_dir)

        effective_policy = json.loads(
            (output_dir / "EffectivePolicy.json").read_text(encoding="utf-8")
        )
        execution_bindings = json.loads(
            (output_dir / "ExecutionBindings.json").read_text(encoding="utf-8")
        )
        compiled_artifact_index = json.loads(
            (output_dir / "CompiledArtifactIndex.json").read_text(encoding="utf-8")
        )

        verifier_result = verify_node_start(
            effective_policy,
            execution_bindings,
            compiled_artifact_index,
            "retrieve-1",
        )

        self.assertEqual(verifier_result, {"ok": True, "message": "node may start"})


if __name__ == "__main__":
    unittest.main()
