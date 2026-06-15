from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import shutil
import unittest
import uuid
from unittest import mock

from cli import operator_approval_decisions_cli
from tests.test_temp_utils import writable_test_root


TEST_RUN_ROOT = writable_test_root("operator-approval-decisions-cli-tests")


class OperatorApprovalDecisionsCliTests(unittest.TestCase):
    def _new_run_dir(self) -> Path:
        run_dir = TEST_RUN_ROOT / uuid.uuid4().hex
        if run_dir.exists():
            shutil.rmtree(run_dir, ignore_errors=True)
        run_dir.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(run_dir, ignore_errors=True))
        return run_dir

    def _write_json(self, path: Path, payload: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def _write_approval_requests(self, run_dir: Path) -> None:
        self._write_json(
            run_dir / "candidate" / "ApprovalRequests.json",
            {
                "schema_version": "m1",
                "workflow_revision_id": "workflow-rev-001",
                "artifact_lifecycle_state": "approval_pending",
                "requests": [
                    {
                        "request_id": "req-1",
                        "node_id": "retrieve-1",
                        "approval_subject_hash": "approval-subject-001",
                        "reason": "Approve safe no-op demo request.",
                    },
                    {
                        "request_id": "req-2",
                        "node_id": "retrieve-2",
                        "approval_subject_hash": "approval-subject-002",
                        "reason": "Approve second safe no-op demo request.",
                    },
                ],
            },
        )

    def _run_cli(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            return_code = operator_approval_decisions_cli.main(argv)
        return return_code, json.loads(stdout.getvalue())

    def test_creates_approval_decisions_for_known_request_id(self) -> None:
        run_dir = self._new_run_dir()
        self._write_approval_requests(run_dir)

        with mock.patch(
            "cli.operator_approval_decisions_cli._utc_now_text",
            return_value="2026-06-15T12:00:00Z",
        ):
            return_code, result = self._run_cli(
                [
                    "--run-dir",
                    str(run_dir),
                    "--request-id",
                    "req-1",
                    "--decision",
                    "approved",
                    "--reviewer",
                    "operator",
                    "--reason",
                    "Approved current request for safe no-op demo only.",
                ]
            )

        approval_decisions_path = run_dir / "ApprovalDecisions.json"
        written = json.loads(approval_decisions_path.read_text(encoding="utf-8"))
        self.assertEqual(return_code, 0)
        self.assertTrue(result["ok"])
        self.assertEqual(result["run_dir"], str(run_dir.resolve()))
        self.assertEqual(
            result["approval_decisions_path"],
            str(approval_decisions_path.resolve()),
        )
        self.assertEqual(result["request_id"], "req-1")
        self.assertEqual(result["decision"], "approved")
        self.assertIs(result["current_run_scope_only"], True)
        self.assertIs(result["not_reusable"], True)
        self.assertIs(result["not_authority"], True)
        self.assertIs(result["not_execution"], True)
        self.assertEqual(
            written,
            {
                "schema_version": "m1",
                "workflow_revision_id": "workflow-rev-001",
                "artifact_lifecycle_state": "completed",
                "decisions": [
                    {
                        "request_id": "req-1",
                        "node_id": "retrieve-1",
                        "approval_subject_hash": "approval-subject-001",
                        "decision": "approved",
                        "approved_at": "2026-06-15T12:00:00Z",
                        "approved_by": "operator",
                        "reason": "Approved current request for safe no-op demo only.",
                    }
                ],
            },
        )
        self.assertTrue(approval_decisions_path.read_text(encoding="utf-8").endswith("\n"))

    def test_unknown_request_id_fails_and_writes_nothing(self) -> None:
        run_dir = self._new_run_dir()
        self._write_approval_requests(run_dir)

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--request-id",
                "req-missing",
                "--decision",
                "approved",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "UNKNOWN_REQUEST_ID")
        self.assertIs(result["current_run_scope_only"], True)
        self.assertIs(result["not_reusable"], True)
        self.assertIs(result["not_authority"], True)
        self.assertIs(result["not_execution"], True)
        self.assertFalse((run_dir / "ApprovalDecisions.json").exists())

    def test_missing_approval_requests_fails_and_writes_nothing(self) -> None:
        run_dir = self._new_run_dir()
        (run_dir / "candidate").mkdir(parents=True)

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--request-id",
                "req-1",
                "--decision",
                "approved",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["error_code"], "MISSING_APPROVAL_REQUESTS")
        self.assertFalse((run_dir / "ApprovalDecisions.json").exists())

    def test_malformed_approval_requests_fails_and_writes_nothing(self) -> None:
        run_dir = self._new_run_dir()
        approval_requests_path = run_dir / "candidate" / "ApprovalRequests.json"
        approval_requests_path.parent.mkdir(parents=True)
        approval_requests_path.write_text("{ not valid json", encoding="utf-8")

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--request-id",
                "req-1",
                "--decision",
                "approved",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["error_code"], "MALFORMED_APPROVAL_REQUESTS")
        self.assertFalse((run_dir / "ApprovalDecisions.json").exists())

    def test_malformed_existing_approval_decisions_fails_without_overwrite(self) -> None:
        run_dir = self._new_run_dir()
        self._write_approval_requests(run_dir)
        approval_decisions_path = run_dir / "ApprovalDecisions.json"
        approval_decisions_path.write_text("{ not valid json", encoding="utf-8")
        before = approval_decisions_path.read_text(encoding="utf-8")

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--request-id",
                "req-1",
                "--decision",
                "approved",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["error_code"], "MALFORMED_APPROVAL_DECISIONS")
        self.assertEqual(approval_decisions_path.read_text(encoding="utf-8"), before)

    def test_duplicate_decision_for_same_request_id_fails_without_overwrite(self) -> None:
        run_dir = self._new_run_dir()
        self._write_approval_requests(run_dir)
        approval_decisions_path = run_dir / "ApprovalDecisions.json"
        self._write_json(
            approval_decisions_path,
            {
                "schema_version": "m1",
                "workflow_revision_id": "workflow-rev-001",
                "artifact_lifecycle_state": "completed",
                "decisions": [
                    {
                        "request_id": "req-1",
                        "decision": "approved",
                        "approved_by": "operator",
                        "approved_at": "2026-06-15T11:00:00Z",
                    }
                ],
            },
        )
        before = approval_decisions_path.read_text(encoding="utf-8")

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--request-id",
                "req-1",
                "--decision",
                "approved",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["error_code"], "DUPLICATE_DECISION")
        self.assertEqual(approval_decisions_path.read_text(encoding="utf-8"), before)

    def test_preserves_existing_valid_decisions_for_other_request_ids(self) -> None:
        run_dir = self._new_run_dir()
        self._write_approval_requests(run_dir)
        approval_decisions_path = run_dir / "ApprovalDecisions.json"
        self._write_json(
            approval_decisions_path,
            {
                "schema_version": "m1",
                "workflow_revision_id": "workflow-rev-001",
                "artifact_lifecycle_state": "completed",
                "decisions": [
                    {
                        "request_id": "req-2",
                        "decision": "approved",
                        "approved_by": "existing-operator",
                        "approved_at": "2026-06-15T11:00:00Z",
                    }
                ],
            },
        )

        with mock.patch(
            "cli.operator_approval_decisions_cli._utc_now_text",
            return_value="2026-06-15T12:00:00Z",
        ):
            return_code, result = self._run_cli(
                [
                    "--run-dir",
                    str(run_dir),
                    "--request-id",
                    "req-1",
                    "--decision",
                    "approved",
                    "--reviewer",
                    "operator",
                ]
            )

        written = json.loads(approval_decisions_path.read_text(encoding="utf-8"))
        self.assertEqual(return_code, 0)
        self.assertTrue(result["ok"])
        self.assertEqual(
            written["decisions"],
            [
                {
                    "request_id": "req-2",
                    "decision": "approved",
                    "approved_by": "existing-operator",
                    "approved_at": "2026-06-15T11:00:00Z",
                },
                {
                    "request_id": "req-1",
                    "node_id": "retrieve-1",
                    "approval_subject_hash": "approval-subject-001",
                    "decision": "approved",
                    "approved_at": "2026-06-15T12:00:00Z",
                    "approved_by": "operator",
                },
            ],
        )

    def test_invalid_decision_value_fails(self) -> None:
        run_dir = self._new_run_dir()
        self._write_approval_requests(run_dir)

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--request-id",
                "req-1",
                "--decision",
                "rejected",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["error_code"], "INVALID_DECISION")
        self.assertFalse((run_dir / "ApprovalDecisions.json").exists())

    def test_cli_writes_no_files_except_approval_decisions_json(self) -> None:
        run_dir = self._new_run_dir()
        self._write_approval_requests(run_dir)
        before = sorted(
            str(path.relative_to(run_dir))
            for path in run_dir.rglob("*")
        )

        with mock.patch(
            "cli.operator_approval_decisions_cli._utc_now_text",
            return_value="2026-06-15T12:00:00Z",
        ):
            return_code, result = self._run_cli(
                [
                    "--run-dir",
                    str(run_dir),
                    "--request-id",
                    "req-1",
                    "--decision",
                    "approved",
                ]
            )

        after = sorted(
            str(path.relative_to(run_dir))
            for path in run_dir.rglob("*")
        )
        self.assertEqual(return_code, 0)
        self.assertTrue(result["ok"])
        self.assertEqual(
            after,
            sorted([*before, "ApprovalDecisions.json"]),
        )


if __name__ == "__main__":
    unittest.main()
