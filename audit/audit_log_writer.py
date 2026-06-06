from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from compiler.canonical_json import canonical_json_text


def append_audit_events(
    audit_log_path: str | Path,
    events: Sequence[Mapping[str, Any]],
    *,
    allow_create: bool = True,
) -> dict[str, Any]:
    log_path = Path(audit_log_path)

    if not log_path.exists():
        if not allow_create:
            return {
                "ok": False,
                "message": f"audit log file does not exist: {log_path}",
            }
        log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8", newline="\n") as audit_log:
        for event in events:
            audit_log.write(canonical_json_text(dict(event)))
            audit_log.write("\n")

    return {
        "ok": True,
        "audit_log_path": str(log_path),
        "events_appended": len(events),
    }
