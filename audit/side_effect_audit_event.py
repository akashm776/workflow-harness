"""Pure builders for side-effect audit events.

These helpers construct audit-event dictionaries for future side-effect attempts.
They are **build-only and non-authoritative**: they execute nothing, contact
nothing, authorize nothing, write no files, and mutate no external state. They
only assemble data structures that an audit log could later record.

Each helper delegates to ``audit.audit_event.make_audit_event`` so it reuses the
existing audit envelope (`schema_version`, `event_id`, `timestamp`, `event_type`,
`actor`, `workflow_revision_id`, `status`, `details`, optional `node_id`).
Side-effect-specific fields live inside ``details``. Optional values are omitted
when ``None``, mirroring how the envelope omits ``node_id`` when not provided.

This module does not implement a sandbox/broker, does not enforce a side-effect
catalog, does not perform authority subsumption, and does not carry approvals
forward. The compiler remains the sole authority boundary.
"""

from __future__ import annotations

from typing import Any, Sequence

from audit.audit_event import make_audit_event


def _build_details(
    *,
    side_effect_class: str,
    tool_name: str | None,
    connector_name: str | None,
    scope: Any | None,
    checked_authority_ref: str | None,
    correlation_id: str | None,
    artifact_references: Sequence[Any] | None,
    node_revision_id: str | None,
    reason_code: str | None,
) -> dict[str, Any]:
    # Deterministic field ordering; optional values omitted when None.
    details: dict[str, Any] = {"side_effect_class": side_effect_class}
    if tool_name is not None:
        details["tool_name"] = tool_name
    if connector_name is not None:
        details["connector_name"] = connector_name
    if scope is not None:
        details["scope"] = scope
    if checked_authority_ref is not None:
        details["checked_authority_ref"] = checked_authority_ref
    if correlation_id is not None:
        details["correlation_id"] = correlation_id
    if artifact_references is not None:
        details["artifact_references"] = list(artifact_references)
    if node_revision_id is not None:
        details["node_revision_id"] = node_revision_id
    if reason_code is not None:
        details["reason_code"] = reason_code
    return details


def _make_side_effect_event(
    *,
    event_type: str,
    status: str,
    actor: str,
    workflow_revision_id: str,
    node_id: str,
    side_effect_class: str,
    tool_name: str | None = None,
    connector_name: str | None = None,
    scope: Any | None = None,
    checked_authority_ref: str | None = None,
    correlation_id: str | None = None,
    artifact_references: Sequence[Any] | None = None,
    node_revision_id: str | None = None,
    reason_code: str | None = None,
) -> dict[str, Any]:
    details = _build_details(
        side_effect_class=side_effect_class,
        tool_name=tool_name,
        connector_name=connector_name,
        scope=scope,
        checked_authority_ref=checked_authority_ref,
        correlation_id=correlation_id,
        artifact_references=artifact_references,
        node_revision_id=node_revision_id,
        reason_code=reason_code,
    )
    return make_audit_event(
        event_type=event_type,
        actor=actor,
        workflow_revision_id=workflow_revision_id,
        node_id=node_id,
        status=status,
        details=details,
    )


def side_effect_proposed(
    *,
    actor: str,
    workflow_revision_id: str,
    node_id: str,
    side_effect_class: str,
    tool_name: str | None = None,
    connector_name: str | None = None,
    scope: Any | None = None,
    checked_authority_ref: str | None = None,
    correlation_id: str | None = None,
    artifact_references: Sequence[Any] | None = None,
    node_revision_id: str | None = None,
) -> dict[str, Any]:
    """Build a non-authoritative `side_effect_proposed` audit event."""

    return _make_side_effect_event(
        event_type="side_effect_proposed",
        status="proposed",
        actor=actor,
        workflow_revision_id=workflow_revision_id,
        node_id=node_id,
        side_effect_class=side_effect_class,
        tool_name=tool_name,
        connector_name=connector_name,
        scope=scope,
        checked_authority_ref=checked_authority_ref,
        correlation_id=correlation_id,
        artifact_references=artifact_references,
        node_revision_id=node_revision_id,
    )


def side_effect_permitted(
    *,
    actor: str,
    workflow_revision_id: str,
    node_id: str,
    side_effect_class: str,
    tool_name: str | None = None,
    connector_name: str | None = None,
    scope: Any | None = None,
    checked_authority_ref: str | None = None,
    correlation_id: str | None = None,
    artifact_references: Sequence[Any] | None = None,
    node_revision_id: str | None = None,
) -> dict[str, Any]:
    """Build a non-authoritative `side_effect_permitted` audit event.

    Building this event does not authorize anything; it records that a side
    effect was permitted by an authority decision made elsewhere.
    """

    return _make_side_effect_event(
        event_type="side_effect_permitted",
        status="permitted",
        actor=actor,
        workflow_revision_id=workflow_revision_id,
        node_id=node_id,
        side_effect_class=side_effect_class,
        tool_name=tool_name,
        connector_name=connector_name,
        scope=scope,
        checked_authority_ref=checked_authority_ref,
        correlation_id=correlation_id,
        artifact_references=artifact_references,
        node_revision_id=node_revision_id,
    )


def side_effect_denied(
    *,
    actor: str,
    workflow_revision_id: str,
    node_id: str,
    side_effect_class: str,
    reason_code: str,
    tool_name: str | None = None,
    connector_name: str | None = None,
    scope: Any | None = None,
    checked_authority_ref: str | None = None,
    correlation_id: str | None = None,
    artifact_references: Sequence[Any] | None = None,
    node_revision_id: str | None = None,
) -> dict[str, Any]:
    """Build a non-authoritative `side_effect_denied` audit event.

    ``reason_code`` is required so denials are always explainable.
    """

    return _make_side_effect_event(
        event_type="side_effect_denied",
        status="denied",
        actor=actor,
        workflow_revision_id=workflow_revision_id,
        node_id=node_id,
        side_effect_class=side_effect_class,
        tool_name=tool_name,
        connector_name=connector_name,
        scope=scope,
        checked_authority_ref=checked_authority_ref,
        correlation_id=correlation_id,
        artifact_references=artifact_references,
        node_revision_id=node_revision_id,
        reason_code=reason_code,
    )


def side_effect_failed(
    *,
    actor: str,
    workflow_revision_id: str,
    node_id: str,
    side_effect_class: str,
    reason_code: str,
    tool_name: str | None = None,
    connector_name: str | None = None,
    scope: Any | None = None,
    checked_authority_ref: str | None = None,
    correlation_id: str | None = None,
    artifact_references: Sequence[Any] | None = None,
    node_revision_id: str | None = None,
) -> dict[str, Any]:
    """Build a non-authoritative `side_effect_failed` audit event.

    ``reason_code`` is required so failures are always explainable.
    """

    return _make_side_effect_event(
        event_type="side_effect_failed",
        status="failed",
        actor=actor,
        workflow_revision_id=workflow_revision_id,
        node_id=node_id,
        side_effect_class=side_effect_class,
        tool_name=tool_name,
        connector_name=connector_name,
        scope=scope,
        checked_authority_ref=checked_authority_ref,
        correlation_id=correlation_id,
        artifact_references=artifact_references,
        node_revision_id=node_revision_id,
        reason_code=reason_code,
    )
