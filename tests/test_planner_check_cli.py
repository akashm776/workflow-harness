from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from cli import planner_check_cli


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_NODE_TYPE_REGISTRY = (
    ROOT / "fixtures" / "valid" / "simple-workflow" / "input" / "NodeTypeRegistry.json"
)
CANDIDATE_FILES = ("ApprovalRequests.json", "RequestedAuth.json", "WorkflowSpec.json")
FORBIDDEN_ARTIFACTS = (
    "CompilationReport.json",
    "CompiledArtifactIndex.json",
    "EffectivePolicy.json",
    "ExecutionBindings.json",
    "AuditLog.jsonl",
    "ExecutionManifest.json",
    "ExecutionResult.json",
)


class PlannerCheckCliTests(unittest.TestCase):
    def _run(
        self, goal: str, *, summary_only: bool = False, dry_run: bool = False
    ):
        """Run the CLI in an isolated repo root; return (rc, parsed_stdout, dirs)."""
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        repo_root = tmp
        candidate_dir = repo_root / "candidate"
        registry_path = repo_root / "NodeTypeRegistry.json"
        shutil.copy(SIMPLE_NODE_TYPE_REGISTRY, registry_path)

        argv = [
            "--goal", goal,
            "--node-type-registry", str(registry_path),
            "--repo-root", str(repo_root),
            "--candidate-dir", str(candidate_dir),
        ]
        if summary_only:
            argv.append("--summary-only")
        if dry_run:
            argv.append("--dry-run")

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            return_code = planner_check_cli.main(argv)
        return (
            return_code,
            json.loads(stdout.getvalue()),
            {"repo_root": repo_root, "candidate_dir": candidate_dir},
        )

    def test_writes_only_candidate_input_files(self) -> None:
        _, _, dirs = self._run("collect and synthesize evidence")
        written = sorted(p.name for p in dirs["candidate_dir"].iterdir())
        self.assertEqual(written, list(CANDIDATE_FILES))

    def test_candidate_dir_contains_exactly_three_inputs(self) -> None:
        _, _, dirs = self._run("exact set")
        names = {p.name for p in dirs["candidate_dir"].iterdir()}
        self.assertEqual(names, set(CANDIDATE_FILES))

    def test_no_forbidden_artifacts_written_anywhere(self) -> None:
        _, _, dirs = self._run("no artifacts")
        produced = {
            p.name for p in dirs["repo_root"].rglob("*") if p.is_file()
        }
        for forbidden in FORBIDDEN_ARTIFACTS:
            self.assertNotIn(forbidden, produced)

    def test_no_compilation_report(self) -> None:
        _, _, dirs = self._run("g")
        self.assertFalse((dirs["candidate_dir"] / "CompilationReport.json").exists())

    def test_no_compiled_artifact_index(self) -> None:
        _, _, dirs = self._run("g")
        self.assertFalse(
            (dirs["candidate_dir"] / "CompiledArtifactIndex.json").exists()
        )

    def test_no_audit_log(self) -> None:
        _, _, dirs = self._run("g")
        self.assertFalse((dirs["candidate_dir"] / "AuditLog.jsonl").exists())

    def test_no_execution_manifest(self) -> None:
        _, _, dirs = self._run("g")
        self.assertFalse((dirs["candidate_dir"] / "ExecutionManifest.json").exists())

    def test_no_execution_result(self) -> None:
        _, _, dirs = self._run("g")
        self.assertFalse((dirs["candidate_dir"] / "ExecutionResult.json").exists())

    def test_exits_zero_when_candidate_compiles(self) -> None:
        return_code, output, _ = self._run("compile me")
        self.assertEqual(return_code, 0)
        self.assertTrue(output["compile_summary"]["ok"])
        self.assertEqual(
            output["compile_summary"]["compilation_status"], "compiled"
        )

    def test_default_output_shape(self) -> None:
        _, output, _ = self._run("shape")
        self.assertEqual(set(output.keys()), {"planner_result", "compile_summary"})
        planner_result = output["planner_result"]
        self.assertEqual(
            set(planner_result.keys()),
            {"planner_version", "candidate_dir", "written"},
        )
        self.assertEqual(
            sorted(planner_result["written"]), list(CANDIDATE_FILES)
        )

    def test_summary_only_prints_compact_shape(self) -> None:
        _, output, _ = self._run("compact", summary_only=True)
        self.assertEqual(
            set(output.keys()),
            {"ok", "compilation_status", "diagnostics", "candidate_dir"},
        )
        self.assertIsInstance(output["diagnostics"], list)

    def test_output_is_deterministic_for_same_goal(self) -> None:
        # Same goal + same candidate dir path -> identical default output.
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        candidate_dir = tmp / "candidate"
        registry_path = tmp / "NodeTypeRegistry.json"
        shutil.copy(SIMPLE_NODE_TYPE_REGISTRY, registry_path)
        argv = [
            "--goal", "stable goal",
            "--node-type-registry", str(registry_path),
            "--repo-root", str(tmp),
            "--candidate-dir", str(candidate_dir),
        ]

        outputs = []
        for _ in range(2):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                planner_check_cli.main(argv)
            outputs.append(stdout.getvalue())

        self.assertEqual(outputs[0], outputs[1])

    def test_goal_text_not_written_inside_candidate_artifacts(self) -> None:
        goal = "SENTINEL-GOAL-DO-NOT-LEAK"
        _, _, dirs = self._run(goal)
        for file_name in CANDIDATE_FILES:
            content = (dirs["candidate_dir"] / file_name).read_text(encoding="utf-8")
            self.assertNotIn(goal, content)

    # --- --dry-run ---

    def test_dry_run_exits_zero_for_valid_candidate(self) -> None:
        return_code, output, _ = self._run("dry compile", dry_run=True)
        self.assertEqual(return_code, 0)
        self.assertTrue(output["compile_summary"]["ok"])
        self.assertEqual(output["dry_run"], True)

    def test_dry_run_does_not_create_candidate_dir(self) -> None:
        _, _, dirs = self._run("no candidate dir", dry_run=True)
        self.assertFalse(dirs["candidate_dir"].exists())

    def test_dry_run_writes_no_candidate_files_to_requested_dir(self) -> None:
        _, _, dirs = self._run("no files", dry_run=True)
        # candidate-dir must not exist; if it did, it must hold no candidate files.
        if dirs["candidate_dir"].exists():
            names = {p.name for p in dirs["candidate_dir"].iterdir()}
            self.assertEqual(names & set(CANDIDATE_FILES), set())

    def test_dry_run_writes_no_compiled_or_runtime_artifacts(self) -> None:
        _, _, dirs = self._run("no artifacts dry", dry_run=True)
        produced = {p.name for p in dirs["repo_root"].rglob("*") if p.is_file()}
        for forbidden in FORBIDDEN_ARTIFACTS:
            self.assertNotIn(forbidden, produced)
        # Only the static registry input should remain in the repo root.
        self.assertEqual(
            {p.name for p in dirs["repo_root"].iterdir()}, {"NodeTypeRegistry.json"}
        )

    def test_dry_run_summary_only_prints_compact_output(self) -> None:
        _, output, _ = self._run("compact dry", summary_only=True, dry_run=True)
        self.assertEqual(
            set(output.keys()),
            {"ok", "compilation_status", "diagnostics", "candidate_dir", "dry_run"},
        )
        self.assertEqual(output["dry_run"], True)

    def test_dry_run_output_does_not_expose_temp_path(self) -> None:
        _, output, dirs = self._run("no temp leak", dry_run=True)
        # The reported candidate_dir is the requested target, not a temp path.
        self.assertEqual(
            output["planner_result"]["candidate_dir"], str(dirs["candidate_dir"])
        )

    def test_dry_run_output_is_deterministic_for_same_goal(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        candidate_dir = tmp / "candidate"
        registry_path = tmp / "NodeTypeRegistry.json"
        shutil.copy(SIMPLE_NODE_TYPE_REGISTRY, registry_path)
        argv = [
            "--goal", "stable dry goal",
            "--node-type-registry", str(registry_path),
            "--repo-root", str(tmp),
            "--candidate-dir", str(candidate_dir),
            "--dry-run",
        ]

        outputs = []
        for _ in range(2):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                planner_check_cli.main(argv)
            outputs.append(stdout.getvalue())

        self.assertEqual(outputs[0], outputs[1])

    def test_default_non_dry_run_output_has_no_dry_run_key(self) -> None:
        _, output, _ = self._run("normal mode")
        self.assertNotIn("dry_run", output)


if __name__ == "__main__":
    unittest.main()
