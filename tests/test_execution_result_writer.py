from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from orchestrator.compile_and_verify import (
    compile_write_load_verify,
    execute_noop_for_orchestration_result,
)
from runtime.execution_result_writer import write_execution_result


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
UNKNOWN_NODE_TYPE = ROOT / "fixtures" / "invalid" / "unknown-node-type" / "input"
EMPTY_APPROVAL_DECISIONS = SIMPLE_WORKFLOW / "ApprovalDecisions-empty.json"


class ExecutionResultWriterTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"execution-result-writer-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def test_approved_noop_execution_writes_completed_execution_result(self) -> None:
        output_dir = self._make_output_dir()
        orchestration_result = compile_write_load_verify(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )
        noop_result = execute_noop_for_orchestration_result(orchestration_result)
        self.assertIsNotNone(noop_result)

        write_result = write_execution_result(
            noop_result["execution_result"],
            output_dir,
        )

        self.assertEqual(
            write_result,
            {
                "ok": True,
                "execution_result_path": str(output_dir / "ExecutionResult.json"),
                "execution_result_written": True,
            },
        )
        reloaded_result = json.loads(
            (output_dir / "ExecutionResult.json").read_text(encoding="utf-8")
        )
        self.assertEqual(reloaded_result["execution_status"], "completed")

    def test_blocked_noop_execution_writes_blocked_execution_result(self) -> None:
        output_dir = self._make_output_dir()
        orchestration_result = compile_write_load_verify(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
            approval_decisions_path=EMPTY_APPROVAL_DECISIONS,
        )
        noop_result = execute_noop_for_orchestration_result(orchestration_result)
        self.assertIsNotNone(noop_result)

        write_result = write_execution_result(
            noop_result["execution_result"],
            output_dir,
        )

        self.assertTrue(write_result["execution_result_written"])
        reloaded_result = json.loads(
            (output_dir / "ExecutionResult.json").read_text(encoding="utf-8")
        )
        self.assertEqual(reloaded_result["execution_status"], "blocked")

    def test_failed_compile_path_writes_nothing_when_no_execution_result_exists(
        self,
    ) -> None:
        output_dir = self._make_output_dir()
        orchestration_result = compile_write_load_verify(
            UNKNOWN_NODE_TYPE / "WorkflowSpec.json",
            UNKNOWN_NODE_TYPE / "NodeTypeRegistry.json",
            UNKNOWN_NODE_TYPE / "RequestedAuth.json",
            UNKNOWN_NODE_TYPE / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )

        noop_result = execute_noop_for_orchestration_result(orchestration_result)

        self.assertIsNone(noop_result)
        self.assertFalse((output_dir / "ExecutionResult.json").exists())

    def test_overwrite_is_refused_by_default(self) -> None:
        output_dir = self._make_output_dir()
        orchestration_result = compile_write_load_verify(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )
        noop_result = execute_noop_for_orchestration_result(orchestration_result)
        self.assertIsNotNone(noop_result)

        write_execution_result(noop_result["execution_result"], output_dir)

        with self.assertRaises(FileExistsError):
            write_execution_result(noop_result["execution_result"], output_dir)

    def test_reloaded_result_matches_original_dict(self) -> None:
        output_dir = self._make_output_dir()
        orchestration_result = compile_write_load_verify(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=output_dir,
            node_id="retrieve-1",
        )
        noop_result = execute_noop_for_orchestration_result(orchestration_result)
        self.assertIsNotNone(noop_result)
        original_execution_result = deepcopy(noop_result["execution_result"])

        write_execution_result(noop_result["execution_result"], output_dir)

        reloaded_result = json.loads(
            (output_dir / "ExecutionResult.json").read_text(encoding="utf-8")
        )
        self.assertEqual(reloaded_result, original_execution_result)
        self.assertEqual(noop_result["execution_result"], original_execution_result)


if __name__ == "__main__":
    unittest.main()
