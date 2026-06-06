"""Reject floats and non-finite numbers in authority-bearing artifacts.

Authority-bearing artifacts feed canonical hashing, content digests,
``approval_subject_hash``, and runtime verification. Floats and non-finite
numeric values (``NaN``, ``Infinity``, ``-Infinity``) are not safe to carry in
those artifacts: float formatting is not normalized by the canonical JSON
contract (see ``docs/CANONICAL_JSON_V1.md``) and non-finite values are not valid
strict JSON. This module is validation only. It does not change serialization or
hashing behavior.

Rules:

- ``int`` values are allowed.
- ``bool`` values are allowed and are not treated as ints.
- ``float`` values are rejected, including integral floats such as ``1.0``.
- ``NaN``, ``Infinity``, and ``-Infinity`` are rejected.
"""

from __future__ import annotations

import math
from typing import Any


class DisallowedAuthorityValueError(ValueError):
    """Raised when an authority-bearing artifact contains a disallowed value."""

    def __init__(self, artifact_name: str, findings: list[dict[str, Any]]) -> None:
        self.artifact_name = artifact_name
        self.findings = findings
        detail = "; ".join(
            f"{finding['path']} ({finding['reason']})" for finding in findings
        )
        super().__init__(
            f"disallowed authority value in {artifact_name}: {detail}"
        )


def _classify_float(value: float) -> str:
    if math.isnan(value):
        return "non-finite-nan"
    if math.isinf(value):
        return "non-finite-infinity" if value > 0 else "non-finite-negative-infinity"
    return "float"


def _walk(value: Any, path: str, findings: list[dict[str, Any]]) -> None:
    # bool is a subclass of int; handle it first so it is allowed and never
    # treated as an int or mistaken for a numeric to reject.
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        findings.append(
            {
                "path": path,
                "reason": _classify_float(value),
                "value_repr": repr(value),
            }
        )
        return
    if isinstance(value, dict):
        for key in value:
            _walk(value[key], f"{path}.{key}", findings)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _walk(item, f"{path}[{index}]", findings)
        return
    # str, None, and any other leaf are allowed.


def find_disallowed_authority_values(value: Any) -> list[dict[str, Any]]:
    """Return a list of disallowed-value findings within ``value``.

    Each finding is a dict with a ``path`` (e.g. ``$.requested_tools[0].scope``),
    a ``reason`` (``float`` or a ``non-finite-*`` classification), and a
    ``value_repr``. An empty list means no disallowed values were found.
    """

    findings: list[dict[str, Any]] = []
    _walk(value, "$", findings)
    return findings


def assert_no_disallowed_authority_values(
    value: Any, *, artifact_name: str
) -> None:
    """Raise ``DisallowedAuthorityValueError`` if ``value`` has disallowed values."""

    findings = find_disallowed_authority_values(value)
    if findings:
        raise DisallowedAuthorityValueError(artifact_name, findings)
