from __future__ import annotations

from pathlib import Path
from typing import Any


EXPECTED_RUN_ARTIFACTS = [
    "CompilationReport.json",
    "CompiledArtifactIndex.json",
    "EffectivePolicy.json",
    "ExecutionBindings.json",
    "AuditLog.jsonl",
    "ExecutionManifest.json",
    "ExecutionResult.json",
]


def inspect_run_directory(run_dir: str | Path) -> dict[str, Any]:
    run_path = Path(run_dir)
    artifacts = {
        artifact_name: {"exists": (run_path / artifact_name).exists()}
        for artifact_name in EXPECTED_RUN_ARTIFACTS
    }
    return {
        "run_dir": str(run_path),
        "artifacts": artifacts,
        "complete_safe_noop_run": all(
            artifact["exists"] for artifact in artifacts.values()
        ),
    }
