from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from compiler.canonical_json import canonical_json_text


def write_execution_result(
    execution_result: Mapping[str, Any],
    output_dir: str | Path,
    *,
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    result_path = output_path / "ExecutionResult.json"
    if result_path.exists() and not allow_overwrite:
        raise FileExistsError(
            "refusing to overwrite existing artifact: ExecutionResult.json"
        )

    result_path.write_text(
        canonical_json_text(dict(execution_result)),
        encoding="utf-8",
    )
    return {
        "ok": True,
        "execution_result_path": str(result_path),
        "execution_result_written": True,
    }
