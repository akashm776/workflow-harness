from __future__ import annotations

import unittest

from audit.audit_event import make_audit_event


class AuditEventTests(unittest.TestCase):
    def test_make_audit_event_includes_required_fields(self) -> None:
        event = make_audit_event(
            event_type="compile_completed",
            actor="orchestrator",
            workflow_revision_id="workflow-rev-001",
            node_id="retrieve-1",
            status="compiled",
            details={"note": "test"},
        )

        self.assertEqual(event["schema_version"], "m1")
        self.assertTrue(event["event_id"].startswith("audit-event-"))
        self.assertIsInstance(event["timestamp"], str)
        self.assertEqual(event["event_type"], "compile_completed")
        self.assertEqual(event["actor"], "orchestrator")
        self.assertEqual(event["workflow_revision_id"], "workflow-rev-001")
        self.assertEqual(event["node_id"], "retrieve-1")
        self.assertEqual(event["status"], "compiled")
        self.assertEqual(event["details"], {"note": "test"})

    def test_make_audit_event_omits_node_id_when_not_provided(self) -> None:
        event = make_audit_event(
            event_type="compile_failed",
            actor="orchestrator",
            workflow_revision_id="workflow-rev-002",
            status="failed",
            details={},
        )

        self.assertNotIn("node_id", event)


if __name__ == "__main__":
    unittest.main()
