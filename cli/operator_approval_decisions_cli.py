from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Sequence


ALLOWED_DECISIONS = frozenset({"approved"})


class OperatorApprovalDecisionsCliError(Exception):
    def __init__(self, error_code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class _JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise OperatorApprovalDecisionsCliError("INVALID_ARGUMENTS", message)


def build_parser() -> argparse.ArgumentParser:
    parser = _JsonArgumentParser(
        description=(
            "Write a current-run/request-scoped operator ApprovalDecisions.json "
            "artifact from candidate/ApprovalRequests.json."
        )
    )
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--reviewer")
    parser.add_argument("--reason")
    return parser


def _normalized_nonempty_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def _utc_now_text() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))


def _base_response() -> dict[str, bool]:
    return {
        "current_run_scope_only": True,
        "not_reusable": True,
        "not_authority": True,
        "not_execution": True,
    }


def _error(error_code: str, message: str) -> int:
    payload: dict[str, Any] = {
        "ok": False,
        "error_code": error_code,
        "message": message,
    }
    payload.update(_base_response())
    _emit_json(payload)
    return 1


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validated_request(raw_request: Any) -> dict[str, str]:
    if not isinstance(raw_request, dict):
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_REQUESTS",
            "candidate/ApprovalRequests.json is malformed",
        )

    request_id = _normalized_nonempty_string(raw_request.get("request_id"))
    node_id = _normalized_nonempty_string(raw_request.get("node_id"))
    approval_subject_hash = _normalized_nonempty_string(
        raw_request.get("approval_subject_hash")
    )
    if request_id is None or node_id is None or approval_subject_hash is None:
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_REQUESTS",
            "candidate/ApprovalRequests.json is malformed",
        )

    request_entry = {
        "request_id": request_id,
        "node_id": node_id,
        "approval_subject_hash": approval_subject_hash,
    }
    reason = _normalized_nonempty_string(raw_request.get("reason"))
    if reason is not None:
        request_entry["reason"] = reason
    return request_entry


def _load_approval_requests(
    approval_requests_path: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    if not approval_requests_path.exists():
        raise OperatorApprovalDecisionsCliError(
            "MISSING_APPROVAL_REQUESTS",
            "candidate/ApprovalRequests.json is missing",
        )

    try:
        payload = _load_json(approval_requests_path)
    except (OSError, ValueError) as exc:
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_REQUESTS",
            "candidate/ApprovalRequests.json is malformed",
        ) from exc

    if not isinstance(payload, dict):
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_REQUESTS",
            "candidate/ApprovalRequests.json is malformed",
        )

    workflow_revision_id = _normalized_nonempty_string(
        payload.get("workflow_revision_id")
    )
    artifact_lifecycle_state = _normalized_nonempty_string(
        payload.get("artifact_lifecycle_state")
    )
    raw_requests = payload.get("requests")
    if (
        workflow_revision_id is None
        or artifact_lifecycle_state is None
        or not isinstance(raw_requests, list)
    ):
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_REQUESTS",
            "candidate/ApprovalRequests.json is malformed",
        )

    schema_version = payload.get("schema_version")
    if "schema_version" in payload and not isinstance(schema_version, str):
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_REQUESTS",
            "candidate/ApprovalRequests.json is malformed",
        )

    requests_by_id: dict[str, dict[str, str]] = {}
    for raw_request in raw_requests:
        request_entry = _validated_request(raw_request)
        request_id = request_entry["request_id"]
        if request_id in requests_by_id:
            raise OperatorApprovalDecisionsCliError(
                "MALFORMED_APPROVAL_REQUESTS",
                "candidate/ApprovalRequests.json is malformed",
            )
        requests_by_id[request_id] = request_entry

    return (
        {
            "schema_version": schema_version,
            "workflow_revision_id": workflow_revision_id,
            "artifact_lifecycle_state": artifact_lifecycle_state,
        },
        requests_by_id,
    )


def _validated_existing_decision(raw_decision: Any) -> dict[str, Any]:
    if not isinstance(raw_decision, dict):
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_DECISIONS",
            "ApprovalDecisions.json is malformed",
        )

    request_id = _normalized_nonempty_string(raw_decision.get("request_id"))
    decision = _normalized_nonempty_string(raw_decision.get("decision"))
    if request_id is None or decision is None:
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_DECISIONS",
            "ApprovalDecisions.json is malformed",
        )

    validated = dict(raw_decision)
    validated["request_id"] = request_id
    validated["decision"] = decision

    for field_name in (
        "approved_by",
        "approved_at",
        "node_id",
        "approval_subject_hash",
        "reason",
    ):
        if field_name in raw_decision and not isinstance(raw_decision[field_name], str):
            raise OperatorApprovalDecisionsCliError(
                "MALFORMED_APPROVAL_DECISIONS",
                "ApprovalDecisions.json is malformed",
            )

    return validated


def _load_or_initialize_approval_decisions(
    approval_decisions_path: Path,
    *,
    schema_version: str | None,
    workflow_revision_id: str,
) -> dict[str, Any]:
    if not approval_decisions_path.exists():
        payload: dict[str, Any] = {
            "workflow_revision_id": workflow_revision_id,
            "artifact_lifecycle_state": "completed",
            "decisions": [],
        }
        if schema_version is not None:
            payload["schema_version"] = schema_version
        else:
            payload["schema_version"] = "m1"
        return payload

    try:
        payload = _load_json(approval_decisions_path)
    except (OSError, ValueError) as exc:
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_DECISIONS",
            "ApprovalDecisions.json is malformed",
        ) from exc

    if not isinstance(payload, dict):
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_DECISIONS",
            "ApprovalDecisions.json is malformed",
        )

    existing_workflow_revision_id = _normalized_nonempty_string(
        payload.get("workflow_revision_id")
    )
    artifact_lifecycle_state = _normalized_nonempty_string(
        payload.get("artifact_lifecycle_state")
    )
    raw_decisions = payload.get("decisions")
    if (
        existing_workflow_revision_id is None
        or existing_workflow_revision_id != workflow_revision_id
        or artifact_lifecycle_state is None
        or not isinstance(raw_decisions, list)
    ):
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_DECISIONS",
            "ApprovalDecisions.json is malformed",
        )

    if "schema_version" in payload and not isinstance(payload.get("schema_version"), str):
        raise OperatorApprovalDecisionsCliError(
            "MALFORMED_APPROVAL_DECISIONS",
            "ApprovalDecisions.json is malformed",
        )

    existing_payload = dict(payload)
    existing_payload["decisions"] = [
        _validated_existing_decision(raw_decision) for raw_decision in raw_decisions
    ]
    return existing_payload


def _build_decision_entry(
    *,
    request_entry: dict[str, str],
    decision: str,
    reviewer: str | None,
    reason: str | None,
) -> dict[str, str]:
    decision_entry = {
        "request_id": request_entry["request_id"],
        "node_id": request_entry["node_id"],
        "approval_subject_hash": request_entry["approval_subject_hash"],
        "decision": decision,
        "approved_at": _utc_now_text(),
    }
    if reviewer is not None:
        decision_entry["approved_by"] = reviewer
    if reason is not None:
        decision_entry["reason"] = reason
    return decision_entry


def add_operator_approval_decision(
    *,
    run_dir: str | Path,
    request_id: str,
    decision: str,
    reviewer: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    run_path = Path(run_dir).resolve()
    if not run_path.exists() or not run_path.is_dir():
        raise OperatorApprovalDecisionsCliError(
            "RUN_DIR_NOT_FOUND",
            "run_dir does not exist",
        )

    normalized_request_id = _normalized_nonempty_string(request_id)
    if normalized_request_id is None:
        raise OperatorApprovalDecisionsCliError(
            "INVALID_ARGUMENTS",
            "request_id must be a non-empty string",
        )

    normalized_decision = _normalized_nonempty_string(decision)
    if normalized_decision is None or normalized_decision.lower() not in ALLOWED_DECISIONS:
        raise OperatorApprovalDecisionsCliError(
            "INVALID_DECISION",
            'decision must be "approved"',
        )
    normalized_decision = normalized_decision.lower()

    normalized_reviewer = _normalized_nonempty_string(reviewer)
    normalized_reason = _normalized_nonempty_string(reason)

    approval_requests_path = run_path / "candidate" / "ApprovalRequests.json"
    request_metadata, requests_by_id = _load_approval_requests(approval_requests_path)
    request_entry = requests_by_id.get(normalized_request_id)
    if request_entry is None:
        raise OperatorApprovalDecisionsCliError(
            "UNKNOWN_REQUEST_ID",
            f"No approval request with request_id {normalized_request_id} was found.",
        )

    approval_decisions_path = run_path / "ApprovalDecisions.json"
    approval_decisions = _load_or_initialize_approval_decisions(
        approval_decisions_path,
        schema_version=request_metadata["schema_version"],
        workflow_revision_id=request_metadata["workflow_revision_id"],
    )

    existing_decisions = approval_decisions["decisions"]
    if any(
        isinstance(existing_decision, dict)
        and existing_decision.get("request_id") == normalized_request_id
        for existing_decision in existing_decisions
    ):
        raise OperatorApprovalDecisionsCliError(
            "DUPLICATE_DECISION",
            f"ApprovalDecisions.json already contains request_id {normalized_request_id}.",
        )

    approval_decisions["decisions"] = [
        *existing_decisions,
        _build_decision_entry(
            request_entry=request_entry,
            decision=normalized_decision,
            reviewer=normalized_reviewer,
            reason=normalized_reason,
        ),
    ]

    try:
        approval_decisions_path.write_text(
            json.dumps(approval_decisions, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        raise OperatorApprovalDecisionsCliError(
            "WRITE_FAILED",
            "failed to write ApprovalDecisions.json",
        ) from exc

    result: dict[str, Any] = {
        "ok": True,
        "run_dir": str(run_path),
        "approval_decisions_path": str(approval_decisions_path.resolve()),
        "request_id": normalized_request_id,
        "decision": normalized_decision,
    }
    result.update(_base_response())
    return result


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        result = add_operator_approval_decision(
            run_dir=args.run_dir,
            request_id=args.request_id,
            decision=args.decision,
            reviewer=args.reviewer,
            reason=args.reason,
        )
    except OperatorApprovalDecisionsCliError as exc:
        return _error(exc.error_code, exc.message)

    _emit_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
