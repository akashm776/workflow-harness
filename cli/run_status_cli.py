from __future__ import annotations

import argparse
from typing import Sequence

from compiler.canonical_json import canonical_json_text
from runtime.run_status import inspect_run_directory
from runtime.run_status_render import render_run_status_text
from tui.run_status_view import render_run_status_view


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect a persisted safe no-op run.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--view", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = inspect_run_directory(args.run_dir)
    if args.view:
        print(render_run_status_view(result))
    elif args.text:
        print(render_run_status_text(result))
    else:
        print(canonical_json_text(result))
    return 0 if result["complete_safe_noop_run"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
