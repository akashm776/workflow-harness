from __future__ import annotations

import json
from pathlib import Path
import shutil
import unittest
from uuid import uuid4

from audit.audit_log_writer import append_audit_events
from orchestrator.compile_and_verify import (
    build_orchestration_audit_events,
    compile_write_load_verify,
)


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_WORKFLOW = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"


class AuditLogWriterTests(unittest.TestCase):
    def _make_output_dir(self) -> Path:
        output_dir = ROOT / f"audit-log-writer-test-{uuid4().hex}"
        output_dir.mkdir(parents=True, exist_ok=False)
        self.addCleanup(lambda: shutil.rmtree(output_dir, ignore_errors=True))
        return output_dir

    def _make_orchestration_events(self) -> list[dict]:
        bundle_dir = self._make_output_dir() / "bundle"
        result = compile_write_load_verify(
            SIMPLE_WORKFLOW / "WorkflowSpec.json",
            SIMPLE_WORKFLOW / "NodeTypeRegistry.json",
            SIMPLE_WORKFLOW / "RequestedAuth.json",
            SIMPLE_WORKFLOW / "ApprovalRequests.json",
            repo_root=ROOT,
            output_dir=bundle_dir,
            node_id="retrieve-1",
        )
        return build_orchestration_audit_events(result)

    def test_writes_three_orchestration_audit_events_to_jsonl(self) -> None:
        events = self._make_orchestration_events()
        output_dir = self._make_output_dir()
        audit_log_path = output_dir / "AuditLog.jsonl"

        result = append_audit_events(audit_log_path, events)

        self.assertEqual(
            result,
            {
                "ok": True,
                "audit_log_path": str(audit_log_path),
                "events_appended": 3,
            },
        )
        self.assertTrue(audit_log_path.exists())
        lines = audit_log_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 3)

    def test_appending_twice_preserves_previous_lines_and_adds_new_lines(self) -> None:
        first_events = self._make_orchestration_events()
        second_events = self._make_orchestration_events()
        output_dir = self._make_output_dir()
        audit_log_path = output_dir / "AuditLog.jsonl"

        append_audit_events(audit_log_path, first_events)
        append_audit_events(audit_log_path, second_events)

        parsed_lines = [
            json.loads(line)
            for line in audit_log_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(parsed_lines, [*first_events, *second_events])

    def test_allow_create_false_fails_if_file_is_missing(self) -> None:
        output_dir = self._make_output_dir()
        audit_log_path = output_dir / "missing" / "AuditLog.jsonl"
        events = self._make_orchestration_events()

        result = append_audit_events(audit_log_path, events, allow_create=False)

        self.assertEqual(
            result,
            {
                "ok": False,
                "message": f"audit log file does not exist: {audit_log_path}",
            },
        )
        self.assertFalse(audit_log_path.exists())

    def test_reloaded_jsonl_lines_match_original_event_dicts(self) -> None:
        events = self._make_orchestration_events()
        output_dir = self._make_output_dir()
        audit_log_path = output_dir / "AuditLog.jsonl"

        append_audit_events(audit_log_path, events)

        reloaded_events = [
            json.loads(line)
            for line in audit_log_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(reloaded_events, events)


if __name__ == "__main__":
    unittest.main()
