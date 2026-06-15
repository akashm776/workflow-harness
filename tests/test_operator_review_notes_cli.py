from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import shutil
import unittest
import uuid

from cli import operator_review_notes_cli
from runtime.run_status_summary import summarize_run_directory
from tests.test_temp_utils import writable_test_root
from tui.run_status_summary_view import render_run_status_summary_view


TEST_RUN_ROOT = writable_test_root("operator-review-notes-cli-tests")


class OperatorReviewNotesCliTests(unittest.TestCase):
    def _new_run_dir(self) -> Path:
        run_dir = TEST_RUN_ROOT / uuid.uuid4().hex
        if run_dir.exists():
            shutil.rmtree(run_dir, ignore_errors=True)
        run_dir.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(run_dir, ignore_errors=True))
        return run_dir

    def _write_candidate_workflow(self, run_dir: Path) -> None:
        candidate_dir = run_dir / "candidate"
        candidate_dir.mkdir(parents=True)
        (candidate_dir / "WorkflowSpec.json").write_text(
            json.dumps(
                {
                    "workflow_id": "planner-innovation-review-workflow-example",
                    "workflow_revision_id": (
                        "planner-innovation-review-workflow-rev-example"
                    ),
                    "nodes": [
                        {
                            "node_id": "retrieve-2",
                            "node_type": "retrieve",
                            "label": "Retrieve program context",
                        },
                        {
                            "node_id": "synthesize-2",
                            "node_type": "synthesize",
                            "label": "Synthesize MVP plans",
                        },
                    ],
                    "edges": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def _run_cli(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            return_code = operator_review_notes_cli.main(argv)
        return return_code, json.loads(stdout.getvalue())

    def test_success_creates_operator_review_notes_file(self) -> None:
        run_dir = self._new_run_dir()
        self._write_candidate_workflow(run_dir)

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note-type",
                "scope_too_broad",
                "--note",
                "Use Bitbucket and Confluence only; do not include SharePoint yet.",
                "--requested-action",
                "narrow_scope",
                "--reviewer",
                "operator",
            ]
        )

        notes_path = run_dir / "candidate" / "OperatorReviewNotes.json"
        written = json.loads(notes_path.read_text(encoding="utf-8"))
        self.assertEqual(return_code, 0)
        self.assertEqual(result["status"], "operator_review_note_added")
        self.assertEqual(result["run_dir"], str(run_dir.resolve()))
        self.assertEqual(result["notes_path"], str(notes_path.resolve()))
        self.assertEqual(result["node_id"], "retrieve-2")
        self.assertEqual(result["note_count"], 1)
        self.assertEqual(
            written,
            {
                "workflow_id": "planner-innovation-review-workflow-example",
                "workflow_revision_id": (
                    "planner-innovation-review-workflow-rev-example"
                ),
                "notes": [
                    {
                        "node_id": "retrieve-2",
                        "note_type": "scope_too_broad",
                        "note": (
                            "Use Bitbucket and Confluence only; do not "
                            "include SharePoint yet."
                        ),
                        "requested_action": "narrow_scope",
                        "reviewer": "operator",
                    }
                ],
            },
        )
        self.assertTrue(notes_path.read_text(encoding="utf-8").endswith("\n"))

    def test_success_appends_to_existing_valid_notes(self) -> None:
        run_dir = self._new_run_dir()
        self._write_candidate_workflow(run_dir)
        notes_path = run_dir / "candidate" / "OperatorReviewNotes.json"
        notes_path.write_text(
            json.dumps(
                {
                    "workflow_id": "stale-id",
                    "workflow_revision_id": "stale-revision",
                    "notes": [
                        {
                            "node_id": "synthesize-2",
                            "note": "Existing note.",
                            "reviewer": "operator",
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note",
                "New display-only note.",
            ]
        )

        written = json.loads(notes_path.read_text(encoding="utf-8"))
        self.assertEqual(return_code, 0)
        self.assertEqual(result["note_count"], 2)
        self.assertEqual(
            written["notes"],
            [
                {
                    "node_id": "synthesize-2",
                    "note": "Existing note.",
                    "reviewer": "operator",
                },
                {
                    "node_id": "retrieve-2",
                    "note": "New display-only note.",
                },
            ],
        )

    def test_success_preserves_workflow_identity_from_workflow_spec(self) -> None:
        run_dir = self._new_run_dir()
        self._write_candidate_workflow(run_dir)

        self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note",
                "Review scope before approval.",
            ]
        )

        notes_path = run_dir / "candidate" / "OperatorReviewNotes.json"
        written = json.loads(notes_path.read_text(encoding="utf-8"))
        self.assertEqual(
            written["workflow_id"],
            "planner-innovation-review-workflow-example",
        )
        self.assertEqual(
            written["workflow_revision_id"],
            "planner-innovation-review-workflow-rev-example",
        )

    def test_unknown_node_id_exits_one_and_does_not_write_notes(self) -> None:
        run_dir = self._new_run_dir()
        self._write_candidate_workflow(run_dir)

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "unknown-node",
                "--note",
                "This should fail.",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["reason_code"], "UNKNOWN_NODE_ID")
        self.assertFalse(
            (run_dir / "candidate" / "OperatorReviewNotes.json").exists()
        )

    def test_missing_workflow_spec_exits_one(self) -> None:
        run_dir = self._new_run_dir()
        (run_dir / "candidate").mkdir(parents=True)

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note",
                "This should fail.",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["reason_code"], "MISSING_CANDIDATE_WORKFLOW")

    def test_malformed_workflow_spec_exits_one(self) -> None:
        run_dir = self._new_run_dir()
        candidate_dir = run_dir / "candidate"
        candidate_dir.mkdir(parents=True)
        (candidate_dir / "WorkflowSpec.json").write_text(
            "{ not valid json",
            encoding="utf-8",
        )

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note",
                "This should fail.",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["reason_code"], "MALFORMED_CANDIDATE_WORKFLOW")

    def test_malformed_existing_operator_review_notes_exits_one_and_does_not_overwrite(
        self,
    ) -> None:
        run_dir = self._new_run_dir()
        self._write_candidate_workflow(run_dir)
        notes_path = run_dir / "candidate" / "OperatorReviewNotes.json"
        notes_path.write_text("{ not valid json", encoding="utf-8")
        before = notes_path.read_text(encoding="utf-8")

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note",
                "This should fail.",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["reason_code"], "MALFORMED_OPERATOR_REVIEW_NOTES")
        self.assertEqual(notes_path.read_text(encoding="utf-8"), before)

    def test_empty_node_id_exits_one(self) -> None:
        run_dir = self._new_run_dir()
        self._write_candidate_workflow(run_dir)

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "   ",
                "--note",
                "This should fail.",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["reason_code"], "EMPTY_NODE_ID")

    def test_empty_note_exits_one(self) -> None:
        run_dir = self._new_run_dir()
        self._write_candidate_workflow(run_dir)

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note",
                "   ",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["reason_code"], "EMPTY_NOTE")

    def test_missing_run_dir_exits_one(self) -> None:
        run_dir = self._new_run_dir() / "missing"

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note",
                "This should fail.",
            ]
        )

        self.assertEqual(return_code, 1)
        self.assertEqual(result["reason_code"], "RUN_DIR_NOT_FOUND")

    def test_stdout_is_valid_json_for_success_and_error(self) -> None:
        run_dir = self._new_run_dir()
        self._write_candidate_workflow(run_dir)

        success_code, success_result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note",
                "Valid note.",
            ]
        )
        error_code, error_result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "unknown-node",
                "--note",
                "Invalid note.",
            ]
        )

        self.assertEqual(success_code, 0)
        self.assertEqual(success_result["status"], "operator_review_note_added")
        self.assertEqual(error_code, 1)
        self.assertEqual(error_result["status"], "error")

    def test_created_notes_are_rendered_by_summary_and_view(self) -> None:
        run_dir = self._new_run_dir()
        self._write_candidate_workflow(run_dir)

        return_code, result = self._run_cli(
            [
                "--run-dir",
                str(run_dir),
                "--node-id",
                "retrieve-2",
                "--note-type",
                "scope_too_broad",
                "--note",
                "Use Bitbucket and Confluence only; do not include SharePoint yet.",
                "--requested-action",
                "narrow_scope",
                "--reviewer",
                "operator",
            ]
        )
        summary = summarize_run_directory(run_dir)
        rendered = render_run_status_summary_view(summary)

        self.assertEqual(return_code, 0)
        self.assertEqual(result["note_count"], 1)
        self.assertIsNotNone(summary["operator_review_notes"])
        self.assertEqual(
            summary["operator_review_notes"]["notes_by_node"]["retrieve-2"][0],
            {
                "note_type": "scope_too_broad",
                "note": (
                    "Use Bitbucket and Confluence only; do not include "
                    "SharePoint yet."
                ),
                "requested_action": "narrow_scope",
                "reviewer": "operator",
            },
        )
        self.assertIn("Operator Review Notes:", rendered)
        self.assertIn("- retrieve-2", rendered)
        self.assertIn("scope_too_broad", rendered)
        self.assertIn("requested_action: narrow_scope", rendered)
        self.assertIn("reviewer: operator", rendered)


if __name__ == "__main__":
    unittest.main()
