from __future__ import annotations

from pathlib import Path
from typing import Callable

from runtime.run_status import inspect_run_directory
from tui.run_status_view import render_run_status_view


def run_status_loop(
    run_dir: str | Path,
    *,
    input_fn: Callable[[], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    while True:
        status = inspect_run_directory(run_dir)
        output_fn(render_run_status_view(status))
        output_fn("Press Enter to refresh, or q to quit.")
        command = input_fn()
        if command.lower() == "q":
            return 0 if status.get("complete_safe_noop_run") is True else 1
