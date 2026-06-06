from __future__ import annotations

import copy
import unittest

from tui.run_status_summary_view import render_run_status_summary_view


def _sample_summary() -> dict:
    return {
        "run_dir": "/tmp/demo",
        "complete_safe_noop_run": True,
        "artifacts": {
            "CompilationReport.json": {"exists": True},
            "ExecutionResult.json": {"exists": True},
        },
        "candidate_dir_present": True,
        "compilation_status": "compiled",
        "execution_status": "blocked",
        "review_required": True,
        "blocked_by_review": True,
        "status_command": "python -m cli.run_status_cli --run-dir /tmp/demo --view",
    }


class RunStatusSummaryViewTests(unittest.TestCase):
    def test_render_includes_all_summary_fields(self) -> None:
        rendered = render_run_status_summary_view(_sample_summary())

        self.assertIn("Safe No-Op Run Summary", rendered)
        self.assertIn("run_dir: /tmp/demo", rendered)
        self.assertIn("complete_safe_noop_run: true", rendered)
        self.assertIn("compilation_status: compiled", rendered)
        self.assertIn("execution_status: blocked", rendered)
        self.assertIn("review_required: true", rendered)
        self.assertIn("blocked_by_review: true", rendered)
        self.assertIn("candidate_dir_present: true", rendered)
        self.assertIn("[x] CompilationReport.json", rendered)
        self.assertIn("[x] ExecutionResult.json", rendered)
        self.assertIn(
            "status command: python -m cli.run_status_cli --run-dir /tmp/demo --view",
            rendered,
        )

    def test_render_does_not_mutate_input(self) -> None:
        summary = _sample_summary()
        original = copy.deepcopy(summary)

        render_run_status_summary_view(summary)

        self.assertEqual(summary, original)

    def test_render_unknown_fields(self) -> None:
        summary = {
            "run_dir": "/tmp/missing",
            "complete_safe_noop_run": False,
            "artifacts": {},
            "candidate_dir_present": False,
            "compilation_status": "unknown",
            "execution_status": "unknown",
            "review_required": None,
            "blocked_by_review": False,
            "status_command": "python -m cli.run_status_cli --run-dir /tmp/missing --view",
        }

        rendered = render_run_status_summary_view(summary)

        self.assertIn("compilation_status: unknown", rendered)
        self.assertIn("execution_status: unknown", rendered)
        self.assertIn("review_required: unknown", rendered)
        self.assertIn("blocked_by_review: false", rendered)


if __name__ == "__main__":
    unittest.main()
