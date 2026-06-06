"""Pure data-shape builders for the future sandbox/broker interface.

These helpers build (and lightly shape-validate) the request, decision, and
result dictionaries described in ``docs/SANDBOX_BROKER_INTERFACE_DESIGN.md``.
They are **build-only**:

- They execute nothing, authorize nothing, verify no sandbox, call no tools or
  connectors, and write no files.
- They are not a broker and not a sandbox; they only assemble data shapes.
- They are not imported by runtime or compiler behavior. The compiler remains
  the sole authority boundary.

The light shape invariants (exactly one of tool/connector; required
``reason_code`` for denied decisions and failure/denied results) are pure
data-shape validation. They may raise ``ValueError`` with stable messages. They
are not runtime authority enforcement.
"""

from __future__ import annotations

from typing import Any, Sequence


SCHEMA_VERSION = "m1"

DECISION_VALUES = ("permitted", "denied")
RESULT_STATUS_VALUES = ("success", "failure", "denied")
_RESULT_STATUS_REQUIRING_REASON = ("failure", "denied")


def build_broker_request(
    *,
    request_id: str,
    workflow_revision_id: str,
    node_id: str,
    node_revision_id: str,
    compiled_artifact_refs: Sequence[Any],
    execution_binding_ref: str,
    side_effect_class: str,
    tool_or_connector_version: str,
    scope: Any,
    audit_correlation_id: str,
    tool_name: str | None = None,
    connector_name: str | None = None,
) -> dict[str, Any]:
    """Build a broker request shape.

    Requires exactly one of ``tool_name`` or ``connector_name``.
    """

    has_tool = tool_name is not None
    has_connector = connector_name is not None
    if has_tool == has_connector:
        raise ValueError(
            "broker request requires exactly one of tool_name or connector_name"
        )

    request: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "workflow_revision_id": workflow_revision_id,
        "node_id": node_id,
        "node_revision_id": node_revision_id,
        "compiled_artifact_refs": list(compiled_artifact_refs),
        "execution_binding_ref": execution_binding_ref,
        "side_effect_class": side_effect_class,
    }
    if has_tool:
        request["tool_name"] = tool_name
    else:
        request["connector_name"] = connector_name
    request["tool_or_connector_version"] = tool_or_connector_version
    request["scope"] = scope
    request["audit_correlation_id"] = audit_correlation_id
    return request


def build_broker_decision(
    *,
    request_id: str,
    decision: str,
    checked_authority_ref: str,
    sandbox_attestation_ref: str,
    side_effect_class: str,
    audit_correlation_id: str,
    reason_code: str | None = None,
) -> dict[str, Any]:
    """Build a broker decision shape.

    ``decision`` must be one of ``"permitted"`` / ``"denied"``. A ``"denied"``
    decision requires ``reason_code``; ``reason_code`` is omitted otherwise.
    """

    if decision not in DECISION_VALUES:
        raise ValueError(
            "broker decision must be one of: " + ", ".join(DECISION_VALUES)
        )
    if decision == "denied" and reason_code is None:
        raise ValueError("broker decision 'denied' requires reason_code")

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "decision": decision,
        "checked_authority_ref": checked_authority_ref,
        "sandbox_attestation_ref": sandbox_attestation_ref,
        "side_effect_class": side_effect_class,
        "audit_correlation_id": audit_correlation_id,
    }
    if reason_code is not None:
        result["reason_code"] = reason_code
    return result


def build_broker_result(
    *,
    request_id: str,
    status: str,
    output_refs: Sequence[Any],
    observed_side_effects: Sequence[Any],
    audit_correlation_id: str,
    reason_code: str | None = None,
) -> dict[str, Any]:
    """Build a broker result shape.

    ``status`` must be one of ``"success"`` / ``"failure"`` / ``"denied"``. A
    ``"failure"`` or ``"denied"`` status requires ``reason_code``; ``reason_code``
    is omitted otherwise.
    """

    if status not in RESULT_STATUS_VALUES:
        raise ValueError(
            "broker result status must be one of: "
            + ", ".join(RESULT_STATUS_VALUES)
        )
    if status in _RESULT_STATUS_REQUIRING_REASON and reason_code is None:
        raise ValueError(
            f"broker result status '{status}' requires reason_code"
        )

    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "status": status,
        "output_refs": list(output_refs),
        "observed_side_effects": list(observed_side_effects),
        "audit_correlation_id": audit_correlation_id,
    }
    if reason_code is not None:
        result["reason_code"] = reason_code
    return result
