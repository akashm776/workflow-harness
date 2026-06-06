"""Pure schema-shape validator for a future ``SideEffectCatalog.json``.

This validates the *shape* of a governed side-effect catalog artifact only. It is
standalone and inspection-only:

- It grants no authority and enforces nothing.
- It is deliberately **not** wired into ``validate_static_inputs`` or any compile
  path; ``SideEffectCatalog.json`` is not a control-plane input.
- It performs no I/O beyond reading the JSON file it is given.
- It does not implement a sandbox/broker, tools, connectors, authority
  subsumption, or approval carryover.

It returns the same diagnostic convention used by the existing schema validators
in ``compiler/static_validation.py``:

- success: ``{"ok": True, "diagnostic": None}``
- failure: ``{"ok": False, "diagnostic": {...}}`` with ``error_code``
  ``"INVALID_ARTIFACT_SCHEMA"``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_ARTIFACT = "SideEffectCatalog.json"

# Closed set of side-effect classes, matching docs/SIDE_EFFECT_CATALOG_DESIGN.md.
ALLOWED_SIDE_EFFECT_CLASSES = (
    "read-only",
    "local write",
    "external write",
    "network call",
    "export",
    "deletion / destructive action",
)


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _diagnostic(message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "diagnostic": {
            "error_code": "INVALID_ARTIFACT_SCHEMA",
            "component": "static_schema_validator",
            "artifact": _ARTIFACT,
            "message": message,
        },
    }


def _field_must_be(path: str, type_name: str) -> dict[str, Any]:
    return _diagnostic(f"{_ARTIFACT} field {path} must be {type_name}")


def validate_side_effect_catalog_schema(catalog_path: str | Path) -> dict[str, Any]:
    catalog = _load_json(catalog_path)

    if not isinstance(catalog, dict):
        return _diagnostic(f"{_ARTIFACT} root $ must be an object")

    if not isinstance(catalog.get("catalog_version"), str):
        return _field_must_be("$.catalog_version", "a string")

    entries = catalog.get("entries")
    if not isinstance(entries, list):
        return _field_must_be("$.entries", "a list")

    for index, entry in enumerate(entries):
        path = f"$.entries[{index}]"
        if not isinstance(entry, dict):
            return _field_must_be(path, "an object")

        has_tool = "tool_name" in entry
        has_connector = "connector_name" in entry
        if has_tool == has_connector:
            return _diagnostic(
                f"{_ARTIFACT} field {path} must have exactly one of "
                "tool_name or connector_name"
            )
        if has_tool and not isinstance(entry["tool_name"], str):
            return _field_must_be(f"{path}.tool_name", "a string")
        if has_connector and not isinstance(entry["connector_name"], str):
            return _field_must_be(f"{path}.connector_name", "a string")

        if not isinstance(entry.get("version"), str):
            return _field_must_be(f"{path}.version", "a string")

        side_effect_class = entry.get("side_effect_class")
        if not isinstance(side_effect_class, str):
            return _field_must_be(f"{path}.side_effect_class", "a string")
        if side_effect_class not in ALLOWED_SIDE_EFFECT_CLASSES:
            return _diagnostic(
                f"{_ARTIFACT} field {path}.side_effect_class must be one of: "
                + ", ".join(ALLOWED_SIDE_EFFECT_CLASSES)
            )

        if not isinstance(entry.get("allowed_scopes"), list):
            return _field_must_be(f"{path}.allowed_scopes", "a list")
        if not isinstance(entry.get("authority_dimensions"), list):
            return _field_must_be(f"{path}.authority_dimensions", "a list")

        if not isinstance(entry.get("sandbox_requirements"), dict):
            return _field_must_be(f"{path}.sandbox_requirements", "an object")
        if not isinstance(entry.get("audit_requirements"), dict):
            return _field_must_be(f"{path}.audit_requirements", "an object")
        if not isinstance(entry.get("review_or_approval_requirements"), dict):
            return _field_must_be(
                f"{path}.review_or_approval_requirements", "an object"
            )

    return {"ok": True, "diagnostic": None}
