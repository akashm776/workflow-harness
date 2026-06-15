from __future__ import annotations

import argparse
import json
from typing import Any, Sequence

from planner.workflow_strategy_preview import (
    WorkflowStrategyPreviewError,
    preview_workflow_strategy,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview a deterministic workflow proposal strategy for a goal."
    )
    parser.add_argument("--goal")
    return parser


def _base_response() -> dict[str, bool]:
    return {
        "display_only": True,
        "not_execution": True,
        "no_model_calls": True,
        "no_tool_calls": True,
    }


def _emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def _error(error_code: str, message: str) -> int:
    payload: dict[str, Any] = {
        "ok": False,
        "error_code": error_code,
        "message": message,
    }
    payload.update(_base_response())
    _emit_json(payload)
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        preview = preview_workflow_strategy(args.goal)
    except WorkflowStrategyPreviewError as exc:
        return _error(exc.error_code, exc.message)

    _emit_json({"ok": True, "preview": preview})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
