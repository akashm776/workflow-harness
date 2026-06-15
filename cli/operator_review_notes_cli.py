from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence


class OperatorReviewNotesCliError(Exception):
    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.message = message


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Write local operator-authored display-only review notes for "
            "candidate workflow nodes."
        )
    )
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--note-type")
    parser.add_argument("--requested-action")
    parser.add_argument("--reviewer")
    return parser


def _normalized_nonempty_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def _error(reason_code: str, message: str) -> int:
    _emit_json(
        {
            "status": "error",
            "reason_code": reason_code,
            "message": message,
        }
    )
    return 1


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_candidate_workflow_info(
    workflow_path: Path,
) -> tuple[dict[str, Any], set[str]]:
    if not workflow_path.exists():
        raise OperatorReviewNotesCliError(
            "MISSING_CANDIDATE_WORKFLOW",
            "candidate/WorkflowSpec.json is missing",
        )

    try:
        workflow = _load_json(workflow_path)
    except (OSError, ValueError) as exc:
        raise OperatorReviewNotesCliError(
            "MALFORMED_CANDIDATE_WORKFLOW",
            "candidate/WorkflowSpec.json is malformed",
        ) from exc

    if not isinstance(workflow, dict):
        raise OperatorReviewNotesCliError(
            "MALFORMED_CANDIDATE_WORKFLOW",
            "candidate/WorkflowSpec.json is malformed",
        )

    raw_nodes = workflow.get("nodes")
    if not isinstance(raw_nodes, list):
        raise OperatorReviewNotesCliError(
            "MALFORMED_CANDIDATE_WORKFLOW",
            "candidate/WorkflowSpec.json is malformed",
        )

    known_node_ids = {
        node_id
        for raw_node in raw_nodes
        if isinstance(raw_node, dict)
        for node_id in [_normalized_nonempty_string(raw_node.get("node_id"))]
        if node_id is not None
    }
    if not known_node_ids:
        raise OperatorReviewNotesCliError(
            "MALFORMED_CANDIDATE_WORKFLOW",
            "candidate/WorkflowSpec.json is malformed",
        )

    return workflow, known_node_ids


def _validated_existing_note(raw_note: Any) -> dict[str, str]:
    if not isinstance(raw_note, dict):
        raise OperatorReviewNotesCliError(
            "MALFORMED_OPERATOR_REVIEW_NOTES",
            "candidate/OperatorReviewNotes.json is malformed",
        )

    node_id = _normalized_nonempty_string(raw_note.get("node_id"))
    note = _normalized_nonempty_string(raw_note.get("note"))
    if node_id is None or note is None:
        raise OperatorReviewNotesCliError(
            "MALFORMED_OPERATOR_REVIEW_NOTES",
            "candidate/OperatorReviewNotes.json is malformed",
        )

    note_entry: dict[str, str] = {"node_id": node_id}
    note_type = _normalized_nonempty_string(raw_note.get("note_type"))
    if note_type is not None:
        note_entry["note_type"] = note_type
    note_entry["note"] = note

    requested_action = _normalized_nonempty_string(raw_note.get("requested_action"))
    if requested_action is not None:
        note_entry["requested_action"] = requested_action

    reviewer = _normalized_nonempty_string(raw_note.get("reviewer"))
    if reviewer is not None:
        note_entry["reviewer"] = reviewer

    return note_entry


def _load_existing_notes(notes_path: Path) -> list[dict[str, str]]:
    if not notes_path.exists():
        return []

    try:
        payload = _load_json(notes_path)
    except (OSError, ValueError) as exc:
        raise OperatorReviewNotesCliError(
            "MALFORMED_OPERATOR_REVIEW_NOTES",
            "candidate/OperatorReviewNotes.json is malformed",
        ) from exc

    if not isinstance(payload, dict):
        raise OperatorReviewNotesCliError(
            "MALFORMED_OPERATOR_REVIEW_NOTES",
            "candidate/OperatorReviewNotes.json is malformed",
        )

    raw_notes = payload.get("notes")
    if not isinstance(raw_notes, list):
        raise OperatorReviewNotesCliError(
            "MALFORMED_OPERATOR_REVIEW_NOTES",
            "candidate/OperatorReviewNotes.json is malformed",
        )

    return [_validated_existing_note(raw_note) for raw_note in raw_notes]


def _build_note(
    *,
    node_id: str,
    note: str,
    note_type: str | None,
    requested_action: str | None,
    reviewer: str | None,
) -> dict[str, str]:
    note_entry: dict[str, str] = {"node_id": node_id}
    if note_type is not None:
        note_entry["note_type"] = note_type
    note_entry["note"] = note
    if requested_action is not None:
        note_entry["requested_action"] = requested_action
    if reviewer is not None:
        note_entry["reviewer"] = reviewer
    return note_entry


def _notes_payload(
    workflow: dict[str, Any],
    notes: list[dict[str, str]],
) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    workflow_id = _normalized_nonempty_string(workflow.get("workflow_id"))
    if workflow_id is not None:
        payload["workflow_id"] = workflow_id

    workflow_revision_id = _normalized_nonempty_string(
        workflow.get("workflow_revision_id")
    )
    if workflow_revision_id is not None:
        payload["workflow_revision_id"] = workflow_revision_id

    payload["notes"] = notes
    return payload


def add_operator_review_note(
    *,
    run_dir: str | Path,
    node_id: str,
    note: str,
    note_type: str | None = None,
    requested_action: str | None = None,
    reviewer: str | None = None,
) -> dict[str, Any]:
    run_path = Path(run_dir).resolve()
    if not run_path.exists() or not run_path.is_dir():
        raise OperatorReviewNotesCliError(
            "RUN_DIR_NOT_FOUND",
            "run_dir does not exist",
        )

    normalized_node_id = _normalized_nonempty_string(node_id)
    if normalized_node_id is None:
        raise OperatorReviewNotesCliError(
            "EMPTY_NODE_ID",
            "node_id must be a non-empty string",
        )

    normalized_note = _normalized_nonempty_string(note)
    if normalized_note is None:
        raise OperatorReviewNotesCliError(
            "EMPTY_NOTE",
            "note must be a non-empty string",
        )

    workflow_path = run_path / "candidate" / "WorkflowSpec.json"
    workflow, known_node_ids = _extract_candidate_workflow_info(workflow_path)

    if normalized_node_id not in known_node_ids:
        raise OperatorReviewNotesCliError(
            "UNKNOWN_NODE_ID",
            "node_id is not present in candidate workflow",
        )

    notes_path = run_path / "candidate" / "OperatorReviewNotes.json"
    notes = _load_existing_notes(notes_path)
    notes.append(
        _build_note(
            node_id=normalized_node_id,
            note=normalized_note,
            note_type=_normalized_nonempty_string(note_type),
            requested_action=_normalized_nonempty_string(requested_action),
            reviewer=_normalized_nonempty_string(reviewer),
        )
    )

    payload = _notes_payload(workflow, notes)
    notes_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return {
        "status": "operator_review_note_added",
        "run_dir": str(run_path),
        "notes_path": str(notes_path.resolve()),
        "node_id": normalized_node_id,
        "note_count": len(notes),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        result = add_operator_review_note(
            run_dir=args.run_dir,
            node_id=args.node_id,
            note=args.note,
            note_type=args.note_type,
            requested_action=args.requested_action,
            reviewer=args.reviewer,
        )
    except OperatorReviewNotesCliError as exc:
        return _error(exc.reason_code, exc.message)

    _emit_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
