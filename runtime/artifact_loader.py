from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_runtime_bundle(bundle_dir: str | Path) -> dict[str, Any]:
    bundle_path = Path(bundle_dir)
    required_artifacts = (
        "EffectivePolicy.json",
        "ExecutionBindings.json",
        "CompiledArtifactIndex.json",
    )

    loaded_artifacts: dict[str, dict[str, Any]] = {}
    for artifact_name in required_artifacts:
        artifact_path = bundle_path / artifact_name
        if not artifact_path.exists():
            return {
                "ok": False,
                "message": f"missing required runtime artifact: {artifact_name}",
            }
        loaded_artifacts[artifact_name] = _load_json_file(artifact_path)

    return {
        "ok": True,
        "effective_policy": loaded_artifacts["EffectivePolicy.json"],
        "execution_bindings": loaded_artifacts["ExecutionBindings.json"],
        "compiled_artifact_index": loaded_artifacts["CompiledArtifactIndex.json"],
    }
