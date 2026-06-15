from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import uuid


def writable_test_root(name: str) -> Path:
    candidates: list[Path] = []

    explicit_root = os.environ.get("WORKFLOW_HARNESS_TEST_RUN_ROOT")
    if explicit_root:
        candidates.append(Path(explicit_root))

    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        candidates.append(Path(local_appdata) / "Temp" / "workflow-harness-test-runs")

    candidates.append(Path(os.path.expanduser("~/workflow-harness-test-runs")))

    for candidate in candidates:
        root = candidate / name
        try:
            root.mkdir(parents=True, exist_ok=True)
            probe = root / f"probe-{uuid.uuid4().hex}"
            probe.mkdir()
            shutil.rmtree(probe, ignore_errors=True)
            return root
        except OSError:
            continue

    raise RuntimeError(f"no writable test root for {name}")


@contextmanager
def temporary_test_directory(name: str) -> Iterator[str]:
    path = writable_test_root(name) / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield str(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)
