"""Canonical JSON helpers for deterministic hashing in M1."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_json_text(value: Any) -> str:
    """Render canonical JSON text with sorted object keys.

    Arrays remain order-sensitive by default. This function does not reorder them.
    """

    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Return canonical JSON as UTF-8 bytes."""

    return canonical_json_text(value).encode("utf-8")


def canonical_sha256_hex(value: Any) -> str:
    """Hash canonical JSON with SHA-256."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
