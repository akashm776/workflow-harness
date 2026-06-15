from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from tests.test_temp_utils import temporary_test_directory
import unittest

from cli import run_status_cli, workflow_demo_cli


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_NODE_TYPE_REGISTRY = (
    ROOT / "fixtures" / "valid" / "simple-workflow" / "input" / "NodeTypeRegistry.json"
)


class SafeInnovationDemoSmokeTest(unittest.TestCase):
    def test_two_command_safe_innovation_demo(self) -> None:
        with temporary_test_directory('safe-innovation-demo-tests') as tmp:
            run_dir = Path(tmp) / "innovation-demo"

            # Command 1: run the demo with an innovation goal.
            demo_stdout = io.StringIO()
            with contextlib.redirect_stdout(demo_stdout):
                demo_code = workflow_demo_cli.main(
                    [
                        "--goal", "generate innovation ideas from program data",
                        "--node-type-registry", str(SIMPLE_NODE_TYPE_REGISTRY),
                        "--repo-root", ".",
                        "--run-dir", str(run_dir),
                    ]
                )
            demo_summary = json.loads(demo_stdout.getvalue())

            self.assertEqual(demo_code, 0)
            self.assertEqual(demo_summary["planner_template"], "innovation")
            self.assertEqual(demo_summary["compilation_status"], "compiled")

            # Command 2: inspect the produced run with the read-only summary.
            status_stdout = io.StringIO()
            with contextlib.redirect_stdout(status_stdout):
                status_code = run_status_cli.main(
                    ["--run-dir", str(run_dir), "--summary"]
                )
            rendered = status_stdout.getvalue()

            self.assertEqual(status_code, 0)
            self.assertIn("Safe No-Op Run Summary", rendered)
            self.assertIn("compilation_status: compiled", rendered)
            self.assertIn("execution_status: blocked", rendered)

            # No real execution: no side effects, no produced evidence.
            execution_result = json.loads(
                (run_dir / "ExecutionResult.json").read_text(encoding="utf-8")
            )
            self.assertEqual(execution_result["side_effects"], [])
            self.assertEqual(execution_result["produced_evidence"], [])


if __name__ == "__main__":
    unittest.main()
