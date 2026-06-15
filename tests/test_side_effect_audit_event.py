from __future__ import annotations

import json
from pathlib import Path
from tests.test_temp_utils import temporary_test_directory
import unittest

from audit.audit_log_writer import append_audit_events
from audit.side_effect_audit_event import (
    side_effect_denied,
    side_effect_failed,
    side_effect_permitted,
    side_effect_proposed,
)


COMMON = {
    "actor": "broker",
    "workflow_revision_id": "workflow-rev-001",
    "node_id": "execute-1",
    "side_effect_class": "external write",
}


class SideEffectAuditEventTests(unittest.TestCase):
    def test_event_type_and_status_are_distinct(self) -> None:
        proposed = side_effect_proposed(**COMMON)
        permitted = side_effect_permitted(**COMMON)
        denied = side_effect_denied(reason_code="BROADER_THAN_APPROVED", **COMMON)
        failed = side_effect_failed(reason_code="SANDBOX_UNVERIFIABLE", **COMMON)

        event_types = {
            proposed["event_type"],
            permitted["event_type"],
            denied["event_type"],
            failed["event_type"],
        }
        statuses = {
            proposed["status"],
            permitted["status"],
            denied["status"],
            failed["status"],
        }

        self.assertEqual(
            event_types,
            {
                "side_effect_proposed",
                "side_effect_permitted",
                "side_effect_denied",
                "side_effect_failed",
            },
        )
        self.assertEqual(statuses, {"proposed", "permitted", "denied", "failed"})

    def test_deterministic_domain_fields_land_exactly_in_details(self) -> None:
        event = side_effect_proposed(
            actor="broker",
            workflow_revision_id="workflow-rev-001",
            node_id="execute-1",
            side_effect_class="external write",
            tool_name="ticket-creator",
            connector_name="jira",
            scope={"project_key": "ABC"},
            checked_authority_ref="EffectivePolicy.json#execute-1",
            correlation_id="corr-123",
            artifact_references=["ExecutionBindings.json"],
            node_revision_id="node-rev-7",
        )

        self.assertEqual(
            event["details"],
            {
                "side_effect_class": "external write",
                "tool_name": "ticket-creator",
                "connector_name": "jira",
                "scope": {"project_key": "ABC"},
                "checked_authority_ref": "EffectivePolicy.json#execute-1",
                "correlation_id": "corr-123",
                "artifact_references": ["ExecutionBindings.json"],
                "node_revision_id": "node-rev-7",
            },
        )
        # Envelope fields still carried by make_audit_event.
        self.assertEqual(event["event_type"], "side_effect_proposed")
        self.assertEqual(event["status"], "proposed")
        self.assertEqual(event["actor"], "broker")
        self.assertEqual(event["workflow_revision_id"], "workflow-rev-001")
        self.assertEqual(event["node_id"], "execute-1")

    def test_optional_fields_omitted_when_none(self) -> None:
        event = side_effect_proposed(**COMMON)
        self.assertEqual(event["details"], {"side_effect_class": "external write"})

    def test_denied_and_failed_include_reason_code(self) -> None:
        denied = side_effect_denied(reason_code="MISSING_SCOPE", **COMMON)
        failed = side_effect_failed(reason_code="UNEXPECTED_NETWORK_ACCESS", **COMMON)

        self.assertEqual(denied["details"]["reason_code"], "MISSING_SCOPE")
        self.assertEqual(failed["details"]["reason_code"], "UNEXPECTED_NETWORK_ACCESS")

    def test_proposed_and_permitted_do_not_include_reason_code(self) -> None:
        proposed = side_effect_proposed(**COMMON)
        permitted = side_effect_permitted(**COMMON)

        self.assertNotIn("reason_code", proposed["details"])
        self.assertNotIn("reason_code", permitted["details"])

    def test_helpers_do_not_write_files(self) -> None:
        with temporary_test_directory('side-effect-audit-event-tests') as tmp:
            tmp_path = Path(tmp)
            side_effect_proposed(**COMMON)
            side_effect_permitted(**COMMON)
            side_effect_denied(reason_code="AMBIGUOUS_AUTHORITY", **COMMON)
            side_effect_failed(reason_code="SANDBOX_UNVERIFIABLE", **COMMON)

            self.assertEqual(list(tmp_path.iterdir()), [])

    def test_events_round_trip_through_append_audit_events(self) -> None:
        events = [
            side_effect_proposed(**COMMON),
            side_effect_permitted(**COMMON),
            side_effect_denied(reason_code="UNDECLARED_TOOL", **COMMON),
            side_effect_failed(reason_code="SANDBOX_UNVERIFIABLE", **COMMON),
        ]
        with temporary_test_directory('side-effect-audit-event-tests') as tmp:
            audit_log_path = Path(tmp) / "AuditLog.jsonl"
            result = append_audit_events(audit_log_path, events)

            self.assertTrue(result["ok"])
            self.assertEqual(result["events_appended"], 4)
            reloaded = [
                json.loads(line)
                for line in audit_log_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(reloaded, events)


if __name__ == "__main__":
    unittest.main()
