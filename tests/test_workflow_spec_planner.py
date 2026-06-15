from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import shutil
from tests.test_temp_utils import temporary_test_directory
import unittest

from cli import safe_run_cli
from compiler.canonical_json import canonical_json_text
from compiler.authority_value_validator import find_disallowed_authority_values
from compiler.static_validation import (
    validate_approval_requests_schema,
    validate_requested_auth_schema,
    validate_workflow_spec_schema,
)
from planner.workflow_spec_planner import (
    CANDIDATE_ARTIFACT_FILES,
    build_stub_planner_candidate,
    write_planner_candidate,
)


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_NODE_TYPE_REGISTRY = (
    ROOT / "fixtures" / "valid" / "simple-workflow" / "input" / "NodeTypeRegistry.json"
)
RUNTIME_ARTIFACT_NAMES = (
    "ExecutionManifest.json",
    "ExecutionResult.json",
    "AuditLog.jsonl",
    "CompilationReport.json",
    "CompiledArtifactIndex.json",
    "EffectivePolicy.json",
    "ExecutionBindings.json",
)


class WorkflowSpecPlannerTests(unittest.TestCase):
    def test_candidate_is_deterministic_for_same_goal(self) -> None:
        left = build_stub_planner_candidate("collect and synthesize evidence")
        right = build_stub_planner_candidate("collect and synthesize evidence")

        self.assertEqual(canonical_json_text(left), canonical_json_text(right))

    def test_candidate_includes_three_input_artifacts(self) -> None:
        candidate = build_stub_planner_candidate("any goal")
        artifacts = candidate["artifacts"]

        self.assertIn("WorkflowSpec.json", artifacts)
        self.assertIn("RequestedAuth.json", artifacts)
        self.assertIn("ApprovalRequests.json", artifacts)

    def test_goal_is_non_authoritative_metadata_only(self) -> None:
        goal = "SENTINEL-GOAL-TEXT"
        candidate = build_stub_planner_candidate(goal)

        self.assertEqual(candidate["goal"], goal)
        # The goal text must not leak into any candidate authority-bearing artifact.
        for artifact in candidate["artifacts"].values():
            self.assertNotIn(goal, canonical_json_text(artifact))

    def test_candidate_passes_authority_value_and_schema_validation(self) -> None:
        candidate = build_stub_planner_candidate("validate me")
        with temporary_test_directory('workflow-spec-planner-tests') as tmp:
            manifest = write_planner_candidate(candidate, tmp)
            tmp_dir = Path(manifest["output_dir"])

            # Authority-value validation: no floats / non-finite anywhere.
            for file_name in CANDIDATE_ARTIFACT_FILES:
                data = json.loads((tmp_dir / file_name).read_text(encoding="utf-8"))
                self.assertEqual(find_disallowed_authority_values(data), [])

            self.assertTrue(
                validate_workflow_spec_schema(tmp_dir / "WorkflowSpec.json")["ok"]
            )
            self.assertTrue(
                validate_requested_auth_schema(tmp_dir / "RequestedAuth.json")["ok"]
            )
            self.assertTrue(
                validate_approval_requests_schema(
                    tmp_dir / "ApprovalRequests.json"
                )["ok"]
            )

    def test_write_planner_candidate_writes_only_candidate_input_files(self) -> None:
        candidate = build_stub_planner_candidate("write me")
        with temporary_test_directory('workflow-spec-planner-tests') as tmp:
            manifest = write_planner_candidate(candidate, tmp)
            written = sorted(p.name for p in Path(tmp).iterdir())

            self.assertEqual(
                written,
                ["ApprovalRequests.json", "RequestedAuth.json", "WorkflowSpec.json"],
            )
            self.assertEqual(sorted(manifest["written"]), written)
            for runtime_artifact in RUNTIME_ARTIFACT_NAMES:
                self.assertNotIn(runtime_artifact, written)

    def _run_check(self, candidate_dir: Path, output_dir: Path) -> tuple[int, dict]:
        argv = [
            "--workflow-spec", str(candidate_dir / "WorkflowSpec.json"),
            "--node-type-registry", str(candidate_dir / "NodeTypeRegistry.json"),
            "--requested-auth", str(candidate_dir / "RequestedAuth.json"),
            "--approval-requests", str(candidate_dir / "ApprovalRequests.json"),
            "--repo-root", str(candidate_dir),
            "--output-dir", str(output_dir),
            "--node-id", "retrieve-1",
            "--check",
        ]
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            return_code = safe_run_cli.main(argv)
        return return_code, json.loads(stdout.getvalue())

    def test_compile_check_succeeds_or_returns_stable_diagnostics(self) -> None:
        candidate = build_stub_planner_candidate("compile me")
        with temporary_test_directory('workflow-spec-planner-tests') as tmp:
            candidate_dir = Path(tmp) / "candidate"
            output_dir = Path(tmp) / "out"
            output_dir.mkdir()
            write_planner_candidate(candidate, candidate_dir)
            shutil.copy(SIMPLE_NODE_TYPE_REGISTRY, candidate_dir / "NodeTypeRegistry.json")

            return_code, check_result = self._run_check(candidate_dir, output_dir)
            return_code_2, check_result_2 = self._run_check(candidate_dir, output_dir)

        # Stable result across runs.
        self.assertEqual(check_result, check_result_2)
        self.assertEqual(return_code, return_code_2)
        # Either succeeds (compiled) or returns stable diagnostics.
        self.assertIn(return_code, (0, 1))
        self.assertIn("compilation_status", check_result)
        self.assertIsInstance(check_result["diagnostics"], list)
        if return_code == 0:
            self.assertEqual(check_result["compilation_status"], "compiled")

    def test_compile_check_writes_no_runtime_or_execution_artifacts(self) -> None:
        candidate = build_stub_planner_candidate("no runtime artifacts")
        with temporary_test_directory('workflow-spec-planner-tests') as tmp:
            candidate_dir = Path(tmp) / "candidate"
            output_dir = Path(tmp) / "out"
            output_dir.mkdir()
            write_planner_candidate(candidate, candidate_dir)
            shutil.copy(SIMPLE_NODE_TYPE_REGISTRY, candidate_dir / "NodeTypeRegistry.json")

            self._run_check(candidate_dir, output_dir)

            # --check writes nothing to the output dir.
            self.assertEqual(list(output_dir.iterdir()), [])
            # No execution artifacts anywhere under the candidate dir either.
            produced = {p.name for p in candidate_dir.iterdir()}
            self.assertNotIn("ExecutionManifest.json", produced)
            self.assertNotIn("ExecutionResult.json", produced)


if __name__ == "__main__":
    unittest.main()
