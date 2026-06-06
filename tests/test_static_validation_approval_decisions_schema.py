from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from compiler.compile_run import compile_static_artifacts
from compiler.static_validation import (
    validate_approval_decisions_schema,
    validate_static_inputs,
)


ROOT = Path(__file__).resolve().parent.parent
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
VALID_DECISIONS_FIXTURES = (
    SIMPLE_FIXTURE_INPUT / "ApprovalDecisions.json",
    SIMPLE_FIXTURE_INPUT / "ApprovalDecisions-empty.json",
    ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
    / "ApprovalDecisions.json",
)
CONFLICTING_FIXTURE = (
    ROOT / "fixtures" / "invalid" / "conflicting-approval-decisions" / "input"
)


def _valid_decisions() -> dict:
    return json.loads(
        (SIMPLE_FIXTURE_INPUT / "ApprovalDecisions.json").read_text(encoding="utf-8")
    )


def _write_temp_decisions(tmp_dir: Path, decisions: object) -> Path:
    path = tmp_dir / "ApprovalDecisions.json"
    path.write_text(json.dumps(decisions, allow_nan=True), encoding="utf-8")
    return path


class ApprovalDecisionsSchemaValidatorTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_path in VALID_DECISIONS_FIXTURES:
            with self.subTest(fixture=fixture_path.name):
                result = validate_approval_decisions_schema(fixture_path)
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def _validate_modified(self, modify) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = _valid_decisions()
            modify(decisions)
            path = _write_temp_decisions(Path(tmp), decisions)
            return validate_approval_decisions_schema(path)

    def _assert_schema_failure(self, result: dict, *, path_fragment: str) -> None:
        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "INVALID_ARTIFACT_SCHEMA")
        self.assertEqual(diagnostic["component"], "static_schema_validator")
        self.assertEqual(diagnostic["artifact"], "ApprovalDecisions.json")
        self.assertIn(path_fragment, diagnostic["message"])

    def test_decisions_missing_fails(self) -> None:
        def modify(decisions: dict) -> None:
            del decisions["decisions"]

        self._assert_schema_failure(
            self._validate_modified(modify), path_fragment="$.decisions"
        )

    def test_decisions_not_list_fails(self) -> None:
        def modify(decisions: dict) -> None:
            decisions["decisions"] = {"request_id": "x"}

        self._assert_schema_failure(
            self._validate_modified(modify), path_fragment="$.decisions"
        )

    def test_decision_entry_not_object_fails(self) -> None:
        def modify(decisions: dict) -> None:
            decisions["decisions"] = ["not-an-object"]

        self._assert_schema_failure(
            self._validate_modified(modify), path_fragment="$.decisions[0]"
        )

    def test_decision_not_string_fails(self) -> None:
        def modify(decisions: dict) -> None:
            decisions["decisions"][0]["decision"] = 1

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.decisions[0].decision",
        )

    def test_node_id_not_string_fails_when_present(self) -> None:
        def modify(decisions: dict) -> None:
            decisions["decisions"][0]["node_id"] = 7

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.decisions[0].node_id",
        )

    def test_approval_subject_hash_not_string_fails_when_present(self) -> None:
        def modify(decisions: dict) -> None:
            decisions["decisions"][0]["approval_subject_hash"] = ["x"]

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.decisions[0].approval_subject_hash",
        )

    def test_diagnostic_includes_artifact_and_json_path(self) -> None:
        def modify(decisions: dict) -> None:
            decisions["decisions"][0]["request_id"] = None

        result = self._validate_modified(modify)
        diagnostic = result["diagnostic"]

        self.assertEqual(diagnostic["artifact"], "ApprovalDecisions.json")
        self.assertIn("ApprovalDecisions.json", diagnostic["message"])
        self.assertIn("$.decisions[0].request_id", diagnostic["message"])


class ApprovalDecisionsSchemaPhasingTests(unittest.TestCase):
    def _validate_inputs_with_decisions(
        self, decisions_path, *, stop_on_first_error: bool = True
    ) -> dict:
        return validate_static_inputs(
            SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json",
            SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
            SIMPLE_FIXTURE_INPUT / "RequestedAuth.json",
            SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json",
            approval_decisions_path=decisions_path,
            stop_on_first_error=stop_on_first_error,
        )

    def test_not_validated_when_absent(self) -> None:
        # Without approval_decisions_path the decisions schema validator does not
        # run; the valid simple fixture passes all phases.
        result = validate_static_inputs(
            SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json",
            SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
            SIMPLE_FIXTURE_INPUT / "RequestedAuth.json",
            SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json",
        )
        self.assertTrue(result["ok"])

    def test_aggregate_mode_schema_failure_gates_interpretation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = _valid_decisions()
            decisions["decisions"] = "not-a-list"
            path = _write_temp_decisions(Path(tmp), decisions)

            result = self._validate_inputs_with_decisions(
                path, stop_on_first_error=False
            )

        self.assertFalse(result["ok"])
        self.assertEqual(len(result["diagnostics"]), 1)
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )
        self.assertEqual(
            result["diagnostics"][0]["artifact"], "ApprovalDecisions.json"
        )

    def test_float_fails_in_authority_phase_before_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = _valid_decisions()
            decisions["decisions"][0]["weight"] = 1.0
            path = _write_temp_decisions(Path(tmp), decisions)

            result = self._validate_inputs_with_decisions(path)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "DISALLOWED_AUTHORITY_VALUE"
        )

    def test_conflicting_fixture_still_reaches_conflict_logic(self) -> None:
        # The conflicting-approval-decisions fixture is structurally valid, so
        # schema validation passes and compile still surfaces the existing
        # CONFLICTING_APPROVAL_DECISIONS behavior (not a schema error).
        result = compile_static_artifacts(
            CONFLICTING_FIXTURE / "WorkflowSpec.json",
            CONFLICTING_FIXTURE / "NodeTypeRegistry.json",
            CONFLICTING_FIXTURE / "RequestedAuth.json",
            CONFLICTING_FIXTURE / "ApprovalRequests.json",
            repo_root=ROOT,
        )

        self.assertFalse(result["ok"])
        diagnostics = result["artifacts"]["CompilationReport.json"]["diagnostics"]
        self.assertEqual(
            diagnostics[0]["error_code"], "CONFLICTING_APPROVAL_DECISIONS"
        )


if __name__ == "__main__":
    unittest.main()
