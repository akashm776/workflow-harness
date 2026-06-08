from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from examples import safe_innovation_demo


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_NODE_TYPE_REGISTRY = (
    ROOT / "fixtures" / "valid" / "simple-workflow" / "input" / "NodeTypeRegistry.json"
)


class SafeInnovationDemoExampleTests(unittest.TestCase):
    def _run(
        self,
        run_root: Path,
        *,
        planner_template: str | None = None,
        approve: bool = False,
        allow_overwrite: bool = False,
    ):
        argv = [
            "--run-root", str(run_root),
            "--node-type-registry", str(SIMPLE_NODE_TYPE_REGISTRY),
        ]
        if planner_template is not None:
            argv.extend(["--planner-template", planner_template])
        if approve:
            argv.append("--demo-approve-current-request")
        if allow_overwrite:
            argv.append("--allow-overwrite")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            return_code = safe_innovation_demo.main(argv)
        return return_code, json.loads(stdout.getvalue())

    def test_no_approval_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp)
            return_code, output = self._run(run_root)

            blocked_run_dir = run_root / "innovation-demo"
            approved_run_dir = run_root / "innovation-approved"

            self.assertEqual(return_code, 0)
            self.assertTrue(blocked_run_dir.exists())
            self.assertFalse((blocked_run_dir / "ApprovalDecisions.json").exists())
            self.assertFalse(approved_run_dir.exists())
            self.assertFalse(output["approval_generated"])
            self.assertIn("approval was not generated", output["message"].lower())
            self.assertEqual(
                output["blocked_run"]["summary"]["execution_status"], "blocked"
            )
            self.assertEqual(output["planner_template"], "innovation")

    def test_approval_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp)
            return_code, output = self._run(run_root, approve=True)

            blocked_run_dir = run_root / "innovation-demo"
            approved_run_dir = run_root / "innovation-approved"
            decisions_path = blocked_run_dir / "ApprovalDecisions.json"

            self.assertEqual(return_code, 0)
            self.assertTrue(decisions_path.exists())

            # Decision matches the generated request_id.
            approval_requests = json.loads(
                (blocked_run_dir / "candidate" / "ApprovalRequests.json").read_text(
                    encoding="utf-8"
                )
            )
            request_id = approval_requests["requests"][0]["request_id"]
            decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
            self.assertEqual(decisions["decisions"][0]["request_id"], request_id)
            self.assertEqual(decisions["decisions"][0]["decision"], "approved")
            self.assertEqual(
                decisions["decisions"][0]["approved_by"], "safe-innovation-demo-local"
            )
            self.assertEqual(output["request_id"], request_id)

            # Approved run is a completed safe no-op.
            execution_result = json.loads(
                (approved_run_dir / "ExecutionResult.json").read_text(encoding="utf-8")
            )
            self.assertEqual(execution_result["execution_status"], "completed")
            self.assertEqual(execution_result["side_effects"], [])
            self.assertEqual(execution_result["produced_evidence"], [])
            self.assertEqual(
                output["approved_run"]["summary"]["execution_status"], "completed"
            )

            # Demo-local notice.
            notice = output["demo_approval_notice"].lower()
            self.assertIn("demo-local", notice)
            self.assertIn("current run", notice)
            self.assertIn("not a general auto-approval", notice)

    def test_rerun_without_allow_overwrite_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp)
            self._run(run_root)

            workflow_spec_path = (
                run_root / "innovation-demo" / "candidate" / "WorkflowSpec.json"
            )
            before = workflow_spec_path.read_text(encoding="utf-8")

            with self.assertRaises(FileExistsError):
                self._run(run_root)

            self.assertEqual(workflow_spec_path.read_text(encoding="utf-8"), before)

    def test_explicit_innovation_review_template_path_works(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp)
            return_code, output = self._run(
                run_root, planner_template="innovation_review"
            )

            self.assertEqual(return_code, 0)
            self.assertEqual(output["planner_template"], "innovation_review")
            self.assertEqual(
                output["blocked_run"]["summary"]["execution_status"], "blocked"
            )

    def test_default_planner_template_remains_innovation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_root = Path(tmp)
            _, output = self._run(run_root)
            self.assertEqual(output["planner_template"], "innovation")


if __name__ == "__main__":
    unittest.main()
