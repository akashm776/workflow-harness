from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from compiler.canonical_json import canonical_json_text


def _validate_artifact_name(artifact_name: str) -> None:
    if not artifact_name.strip():
        raise ValueError("artifact names must be non-empty strings")
    if Path(artifact_name).name != artifact_name:
        raise ValueError("artifact names must be exact filenames")


def _bundle_compiled_artifact_index(
    compiled_artifact_index: Mapping[str, Any],
) -> dict[str, Any]:
    bundle_index = deepcopy(dict(compiled_artifact_index))
    bundle_artifacts: list[dict[str, Any]] = []

    for artifact_entry in bundle_index.get("artifacts", []):
        rebased_entry = deepcopy(dict(artifact_entry))
        artifact_name = rebased_entry.get("artifact_name")
        if artifact_name == "CompilationReport":
            rebased_entry["artifact_path"] = "CompilationReport.json"
        elif artifact_name == "EffectivePolicy":
            rebased_entry["artifact_path"] = "EffectivePolicy.json"
        elif artifact_name == "ExecutionBindings":
            rebased_entry["artifact_path"] = "ExecutionBindings.json"
        bundle_artifacts.append(rebased_entry)

    bundle_index["artifacts"] = bundle_artifacts
    return bundle_index


def _bundle_artifacts(compile_result: Mapping[str, Any]) -> dict[str, Any]:
    artifacts = compile_result.get("artifacts")
    if not isinstance(artifacts, Mapping):
        raise ValueError("compile_result must contain an artifacts mapping")

    bundled = deepcopy(dict(artifacts))
    compiled_artifact_index = bundled.get("CompiledArtifactIndex.json")
    if isinstance(compiled_artifact_index, Mapping):
        bundled["CompiledArtifactIndex.json"] = _bundle_compiled_artifact_index(
            compiled_artifact_index
        )
    return bundled


def write_compiled_artifacts(
    compile_result: Mapping[str, Any],
    output_dir: str | Path,
    *,
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    bundled_artifacts = _bundle_artifacts(compile_result)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    target_paths: list[Path] = []
    for artifact_name in bundled_artifacts:
        if not isinstance(artifact_name, str):
            raise ValueError("artifact names must be non-empty strings")
        _validate_artifact_name(artifact_name)
        target_paths.append(output_path / artifact_name)

    if not allow_overwrite:
        for target_path in target_paths:
            if target_path.exists():
                raise FileExistsError(
                    f"refusing to overwrite existing artifact: {target_path.name}"
                )

    for artifact_name, artifact_value in bundled_artifacts.items():
        (output_path / artifact_name).write_text(
            canonical_json_text(artifact_value),
            encoding="utf-8",
        )

    return {
        "ok": True,
        "output_dir": str(output_path),
        "written_artifacts": sorted(bundled_artifacts.keys()),
    }
