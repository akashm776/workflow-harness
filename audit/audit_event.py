from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def make_audit_event(
    *,
    event_type: str,
    actor: str,
    workflow_revision_id: str,
    node_id: str | None = None,
    status: str,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "schema_version": "m1",
        "event_id": f"audit-event-{uuid4().hex}",
        "timestamp": _utc_timestamp(),
        "event_type": event_type,
        "actor": actor,
        "workflow_revision_id": workflow_revision_id,
        "status": status,
        "details": dict(details or {}),
    }
    if node_id is not None:
        event["node_id"] = node_id
    return event
