from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import unittest

from cli import workflow_strategy_preview_cli
from tests.test_temp_utils import temporary_test_directory


class WorkflowStrategyPreviewCliTests(unittest.TestCase):
    def _run_cli(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            return_code = workflow_strategy_preview_cli.main(argv)
        return return_code, json.loads(stdout.getvalue())

    def test_cli_prints_json_success_and_returns_zero(self) -> None:
        return_code, result = self._run_cli(
            [
                "--goal",
                "Find AI innovation opportunities from program docs and repo context",
            ]
        )

        self.assertEqual(return_code, 0)
        self.assertTrue(result["ok"])
        preview = result["preview"]
        self.assertEqual(
            preview["strategy_type"], "workflow_orchestration_preview"
        )
        self.assertEqual(
            preview["selected_pattern_family"], "fan_out_and_synthesize"
        )
        self.assertIs(preview["display_only"], True)
        self.assertIs(preview["no_model_calls"], True)
        self.assertIs(preview["no_tool_calls"], True)
        self.assertEqual(
            preview["selection_mode"], "deterministic_baseline_preview"
        )
        self.assertIs(preview["future_selector_ready"], True)
        self.assertNotIn("candidate_pattern_rankings", preview)

    def test_cli_prints_json_failure_for_empty_goal_and_returns_one(self) -> None:
        return_code, result = self._run_cli(["--goal", "   "])

        self.assertEqual(return_code, 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "EMPTY_GOAL")
        self.assertEqual(result["message"], "goal must be a non-empty string")
        self.assertIs(result["display_only"], True)
        self.assertIs(result["not_execution"], True)
        self.assertIs(result["no_model_calls"], True)
        self.assertIs(result["no_tool_calls"], True)

    def test_cli_missing_goal_fails_closed(self) -> None:
        return_code, result = self._run_cli([])

        self.assertEqual(return_code, 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "EMPTY_GOAL")

    def test_cli_writes_no_files(self) -> None:
        with temporary_test_directory("workflow-strategy-preview-cli-tests") as tmp:
            tmp_path = Path(tmp)
            before = sorted(
                str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*")
            )

            return_code, result = self._run_cli(
                [
                    "--goal",
                    "Compare alternatives and rank candidate approaches",
                ]
            )

            after = sorted(
                str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*")
            )

        self.assertEqual(return_code, 0)
        self.assertTrue(result["ok"])
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
