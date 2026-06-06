from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from compiler.static_validation import (
    validate_approval_requests_schema,
    validate_static_inputs,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = ("simple-workflow", "approval-required-workflow")
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
AMBIGUOUS_APPROVAL_REQUESTS = (
    ROOT / "fixtures" / "invalid" / "ambiguous-approval-subject" / "input"
    / "ApprovalRequests.json"
)


def _valid_approval_requests() -> dict:
    return json.loads(
        (SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json").read_text(encoding="utf-8")
    )


def _write_temp_approval_requests(tmp_dir: Path, approval_requests: object) -> Path:
    path = tmp_dir / "ApprovalRequests.json"
    path.write_text(json.dumps(approval_requests, allow_nan=True), encoding="utf-8")
    return path


class ApprovalRequestsSchemaValidatorTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            approval_requests_path = (
                ROOT / "fixtures" / "valid" / fixture_name / "input"
                / "ApprovalRequests.json"
            )
            with self.subTest(fixture=fixture_name):
                result = validate_approval_requests_schema(approval_requests_path)
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def _validate_modified(self, modify) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            approval_requests = _valid_approval_requests()
            modify(approval_requests)
            path = _write_temp_approval_requests(Path(tmp), approval_requests)
            return validate_approval_requests_schema(path)

    def _assert_schema_failure(self, result: dict, *, path_fragment: str) -> None:
        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "INVALID_ARTIFACT_SCHEMA")
        self.assertEqual(diagnostic["component"], "static_schema_validator")
        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn(path_fragment, diagnostic["message"])

    def test_requests_missing_fails(self) -> None:
        def modify(approval_requests: dict) -> None:
            del approval_requests["requests"]

        self._assert_schema_failure(
            self._validate_modified(modify), path_fragment="$.requests"
        )

    def test_requests_not_list_fails(self) -> None:
        def modify(approval_requests: dict) -> None:
            approval_requests["requests"] = {"request_id": "x"}

        self._assert_schema_failure(
            self._validate_modified(modify), path_fragment="$.requests"
        )

    def test_request_entry_not_object_fails(self) -> None:
        def modify(approval_requests: dict) -> None:
            approval_requests["requests"] = ["not-an-object"]

        self._assert_schema_failure(
            self._validate_modified(modify), path_fragment="$.requests[0]"
        )

    def test_request_id_not_string_fails(self) -> None:
        def modify(approval_requests: dict) -> None:
            approval_requests["requests"][0]["request_id"] = 1

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.requests[0].request_id",
        )

    def test_node_id_not_string_fails(self) -> None:
        def modify(approval_requests: dict) -> None:
            approval_requests["requests"][0]["node_id"] = None

        self._assert_schema_failure(
            self._validate_modified(modify), path_fragment="$.requests[0].node_id"
        )

    def test_approval_subject_hash_not_string_fails(self) -> None:
        def modify(approval_requests: dict) -> None:
            approval_requests["requests"][0]["approval_subject_hash"] = ["x"]

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.requests[0].approval_subject_hash",
        )

    def test_diagnostic_includes_artifact_and_json_path(self) -> None:
        def modify(approval_requests: dict) -> None:
            approval_requests["requests"][0]["node_id"] = 42

        result = self._validate_modified(modify)
        diagnostic = result["diagnostic"]

        self.assertEqual(diagnostic["artifact"], "ApprovalRequests.json")
        self.assertIn("ApprovalRequests.json", diagnostic["message"])
        self.assertIn("$.requests[0].node_id", diagnostic["message"])


class ApprovalRequestsSchemaPhasingTests(unittest.TestCase):
    def _validate_inputs_with_approval_requests(
        self, approval_requests_path, *, stop_on_first_error: bool = True
    ) -> dict:
        return validate_static_inputs(
            SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json",
            SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
            SIMPLE_FIXTURE_INPUT / "RequestedAuth.json",
            approval_requests_path,
            stop_on_first_error=stop_on_first_error,
        )

    def test_aggregate_mode_schema_failure_gates_interpretation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approval_requests = _valid_approval_requests()
            approval_requests["requests"] = "not-a-list"
            path = _write_temp_approval_requests(Path(tmp), approval_requests)

            result = self._validate_inputs_with_approval_requests(
                path, stop_on_first_error=False
            )

        self.assertFalse(result["ok"])
        self.assertEqual(len(result["diagnostics"]), 1)
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )
        self.assertEqual(
            result["diagnostics"][0]["artifact"], "ApprovalRequests.json"
        )

    def test_float_fails_in_authority_phase_before_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approval_requests = _valid_approval_requests()
            approval_requests["requests"][0]["weight"] = 1.0
            path = _write_temp_approval_requests(Path(tmp), approval_requests)

            result = self._validate_inputs_with_approval_requests(path)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "DISALLOWED_AUTHORITY_VALUE"
        )

    def test_ambiguous_fixture_still_reaches_interpretation_phase(self) -> None:
        # The ambiguous-approval-subject fixture is well-formed at the schema
        # layer, so schema validation passes and the interpretation phase returns
        # AMBIGUOUS_APPROVAL_SUBJECT.
        result = self._validate_inputs_with_approval_requests(
            AMBIGUOUS_APPROVAL_REQUESTS
        )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "AMBIGUOUS_APPROVAL_SUBJECT"
        )


if __name__ == "__main__":
    unittest.main()
