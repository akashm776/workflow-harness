from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch
from uuid import uuid4

from orchestrator.safe_run import safe_noop_run
from runtime.run_status import inspect_run_directory
from tui import run_status_loop as run_status_loop_module


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"


class RunStatusLoopTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-loop-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _make_missing_output_dir(self) -> Path:
        output_dir = ROOT / f"run-status-loop-test-{uuid4().hex}"
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_missing_directory_with_q_prints_view_once_and_returns_one(self) -> None:
        output_dir = self._make_missing_output_dir()
        output_lines: list[str] = []

        exit_code = run_status_loop_module.run_status_loop(
            output_dir,
            input_fn=lambda: "q",
            output_fn=output_lines.append,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(output_lines.count("Press Enter to refresh, or q to quit."), 1)
        self.assertEqual(
            sum("Safe No-Op Run Status" in line for line in output_lines),
            1,
        )

    def test_approved_run_with_q_prints_view_once_and_returns_zero(self) -> None:
        output_dir = self._make_output_dir()
        safe_noop_run(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )
        output_lines: list[str] = []

        exit_code = run_status_loop_module.run_status_loop(
            output_dir,
            input_fn=lambda: "q",
            output_fn=output_lines.append,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            sum("Safe No-Op Run Status" in line for line in output_lines),
            1,
        )
        self.assertTrue(
            any("complete_safe_noop_run: true" in line for line in output_lines)
        )

    def test_enter_then_q_refreshes_and_prints_view_twice(self) -> None:
        output_dir = self._make_missing_output_dir()
        output_lines: list[str] = []
        commands = iter(["", "q"])

        exit_code = run_status_loop_module.run_status_loop(
            output_dir,
            input_fn=lambda: next(commands),
            output_fn=output_lines.append,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(output_lines.count("Press Enter to refresh, or q to quit."), 2)
        self.assertEqual(
            sum("Safe No-Op Run Status" in line for line in output_lines),
            2,
        )

    def test_uppercase_q_quits(self) -> None:
        output_dir = self._make_missing_output_dir()
        output_lines: list[str] = []

        exit_code = run_status_loop_module.run_status_loop(
            output_dir,
            input_fn=lambda: "Q",
            output_fn=output_lines.append,
        )

        self.assertEqual(exit_code, 1)
        self.assertEqual(output_lines.count("Press Enter to refresh, or q to quit."), 1)

    def test_loop_does_not_mutate_status(self) -> None:
        output_dir = self._make_missing_output_dir()
        status = inspect_run_directory(output_dir)
        original_status = deepcopy(status)
        output_lines: list[str] = []

        with patch.object(
            run_status_loop_module,
            "inspect_run_directory",
            return_value=status,
        ) as inspect_mock:
            exit_code = run_status_loop_module.run_status_loop(
                output_dir,
                input_fn=lambda: "q",
                output_fn=output_lines.append,
            )

        self.assertEqual(exit_code, 1)
        self.assertEqual(status, original_status)
        inspect_mock.assert_called_once_with(output_dir)


if __name__ == "__main__":
    unittest.main()
