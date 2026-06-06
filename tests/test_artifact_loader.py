from __future__ import annotations

from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from compiler.artifact_writer import write_compiled_artifacts
from compiler.compile_run import compile_static_artifacts
from runtime.artifact_loader import load_runtime_bundle
from runtime.runtime_verifier import verify_node_start


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"


class ArtifactLoaderTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"artifact-loader-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _write_approved_bundle(self) -> Path:
        compile_result = compile_static_artifacts(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
        )
        output_dir = self._make_output_dir()
        write_compiled_artifacts(compile_result, output_dir)
        return output_dir

    def test_valid_written_approved_bundle_loads_successfully(self) -> None:
        bundle_dir = self._write_approved_bundle()

        loaded_bundle = load_runtime_bundle(bundle_dir)

        self.assertTrue(loaded_bundle["ok"])
        self.assertIn("effective_policy", loaded_bundle)
        self.assertIn("execution_bindings", loaded_bundle)
        self.assertIn("compiled_artifact_index", loaded_bundle)
        self.assertNotIn("CompilationReport.json", loaded_bundle)

    def test_missing_effective_policy_fails(self) -> None:
        bundle_dir = self._write_approved_bundle()
        (bundle_dir / "EffectivePolicy.json").unlink()

        loaded_bundle = load_runtime_bundle(bundle_dir)

        self.assertEqual(
            loaded_bundle,
            {
                "ok": False,
                "message": "missing required runtime artifact: EffectivePolicy.json",
            },
        )

    def test_missing_execution_bindings_fails(self) -> None:
        bundle_dir = self._write_approved_bundle()
        (bundle_dir / "ExecutionBindings.json").unlink()

        loaded_bundle = load_runtime_bundle(bundle_dir)

        self.assertEqual(
            loaded_bundle,
            {
                "ok": False,
                "message": "missing required runtime artifact: ExecutionBindings.json",
            },
        )

    def test_missing_compiled_artifact_index_fails(self) -> None:
        bundle_dir = self._write_approved_bundle()
        (bundle_dir / "CompiledArtifactIndex.json").unlink()

        loaded_bundle = load_runtime_bundle(bundle_dir)

        self.assertEqual(
            loaded_bundle,
            {
                "ok": False,
                "message": "missing required runtime artifact: CompiledArtifactIndex.json",
            },
        )

    def test_loaded_bundle_can_be_passed_directly_into_runtime_verifier(self) -> None:
        bundle_dir = self._write_approved_bundle()

        loaded_bundle = load_runtime_bundle(bundle_dir)

        self.assertTrue(loaded_bundle["ok"])
        verifier_result = verify_node_start(
            loaded_bundle["effective_policy"],
            loaded_bundle["execution_bindings"],
            loaded_bundle["compiled_artifact_index"],
            "retrieve-1",
        )

        self.assertEqual(verifier_result, {"ok": True, "message": "node may start"})


if __name__ == "__main__":
    unittest.main()
