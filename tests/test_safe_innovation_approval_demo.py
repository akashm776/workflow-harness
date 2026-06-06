from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from cli import run_status_cli, safe_run_cli, workflow_demo_cli


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_NODE_TYPE_REGISTRY = (
    ROOT / "fixtures" / "valid" / "simple-workflow" / "input" / "NodeTypeRegistry.json"
)


class SafeInnovationApprovalDemoSmokeTest(unittest.TestCase):
    def test_blocked_then_explicit_approval_then_completed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            blocked_run_dir = Path(tmp) / "innovation-demo"
            approved_run_dir = Path(tmp) / "innovation-approved"

            # 1. Run the innovation demo unapproved -> blocked.
            demo_stdout = io.StringIO()
            with contextlib.redirect_stdout(demo_stdout):
                demo_code = workflow_demo_cli.main(
                    [
                        "--goal", "generate innovation ideas from program data",
                        "--node-type-registry", str(SIMPLE_NODE_TYPE_REGISTRY),
                        "--repo-root", ".",
                        "--run-dir", str(blocked_run_dir),
                    ]
                )
            demo_summary = json.loads(demo_stdout.getvalue())

            self.assertEqual(demo_code, 0)
            self.assertEqual(demo_summary["planner_template"], "innovation")
            self.assertEqual(demo_summary["compilation_status"], "compiled")
            self.assertEqual(demo_summary["execution_status"], "blocked")

            # 2. Inspect the generated approval request.
            approval_requests = json.loads(
                (blocked_run_dir / "candidate" / "ApprovalRequests.json").read_text(
                    encoding="utf-8"
                )
            )
            requests = approval_requests["requests"]
            self.assertEqual(len(requests), 1)
            request_id = requests[0]["request_id"]
            workflow_revision_id = approval_requests["workflow_revision_id"]

            # 3. Write an explicit approval decision for this run's request only.
            approval_decisions_path = blocked_run_dir / "ApprovalDecisions.json"
            approval_decisions_path.write_text(
                json.dumps(
                    {
                        "schema_version": "m1",
                        "workflow_revision_id": workflow_revision_id,
                        "artifact_lifecycle_state": "completed",
                        "decisions": [
                            {
                                "request_id": request_id,
                                "decision": "approved",
                                "approved_by": "smoke-test-operator",
                                "approved_at": "2026-06-06T00:00:00Z",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            # 4. Rerun the safe no-op path with the explicit approval decision.
            safe_run_stdout = io.StringIO()
            with contextlib.redirect_stdout(safe_run_stdout):
                safe_run_code = safe_run_cli.main(
                    [
                        "--workflow-spec",
                        str(blocked_run_dir / "candidate" / "WorkflowSpec.json"),
                        "--node-type-registry",
                        str(blocked_run_dir / "NodeTypeRegistry.json"),
                        "--requested-auth",
                        str(blocked_run_dir / "candidate" / "RequestedAuth.json"),
                        "--approval-requests",
                        str(blocked_run_dir / "candidate" / "ApprovalRequests.json"),
                        "--approval-decisions",
                        str(approval_decisions_path),
                        "--repo-root",
                        str(blocked_run_dir),
                        "--output-dir",
                        str(approved_run_dir),
                        "--node-id",
                        "retrieve-1",
                    ]
                )

            self.assertEqual(safe_run_code, 0)

            # 5. The approved run is a completed safe no-op (no side effects).
            execution_result = json.loads(
                (approved_run_dir / "ExecutionResult.json").read_text(encoding="utf-8")
            )
            self.assertEqual(execution_result["execution_status"], "completed")
            self.assertEqual(execution_result["side_effects"], [])
            self.assertEqual(execution_result["produced_evidence"], [])

            # 6. The summary reflects compiled + completed.
            status_stdout = io.StringIO()
            with contextlib.redirect_stdout(status_stdout):
                status_code = run_status_cli.main(
                    ["--run-dir", str(approved_run_dir), "--summary"]
                )
            rendered = status_stdout.getvalue()

            self.assertEqual(status_code, 0)
            self.assertIn("Safe No-Op Run Summary", rendered)
            self.assertIn("compilation_status: compiled", rendered)
            self.assertIn("execution_status: completed", rendered)


if __name__ == "__main__":
    unittest.main()
