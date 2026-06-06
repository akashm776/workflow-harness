from __future__ import annotations

from typing import Any, Mapping


class ConflictingApprovalDecisionsError(ValueError):
    """Raised when matching approval decisions conflict for one approval subject."""


def _normalized_approval_state(decision_entry: Mapping[str, Any]) -> str | None:
    for field_name in ("decision", "status"):
        value = decision_entry.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return None


def resolve_review_required(
    *,
    node_id: str,
    approval_subject_hash: str,
    approval_decisions: Mapping[str, Any],
) -> bool:
    matching_decisions = [
        decision_entry
        for decision_entry in approval_decisions.get("decisions", [])
        if isinstance(decision_entry, Mapping)
        and decision_entry.get("node_id") == node_id
        and decision_entry.get("approval_subject_hash") == approval_subject_hash
    ]

    if not matching_decisions:
        return True

    if len(matching_decisions) > 1:
        decision_states = {
            _normalized_approval_state(decision_entry)
            for decision_entry in matching_decisions
        }
        if len(decision_states) > 1:
            raise ConflictingApprovalDecisionsError(
                "multiple conflicting approval decisions for node_id and approval_subject_hash"
            )
        return True

    return _normalized_approval_state(matching_decisions[0]) != "approved"
