from __future__ import annotations

import json
from pathlib import Path
from tests.test_temp_utils import temporary_test_directory
import unittest

from compiler.static_validation import (
    validate_requested_auth_schema,
    validate_static_inputs,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = ("simple-workflow", "approval-required-workflow")
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"


def _valid_requested_auth() -> dict:
    return json.loads(
        (SIMPLE_FIXTURE_INPUT / "RequestedAuth.json").read_text(encoding="utf-8")
    )


def _write_temp_requested_auth(tmp_dir: Path, requested_auth: object) -> Path:
    path = tmp_dir / "RequestedAuth.json"
    path.write_text(json.dumps(requested_auth, allow_nan=True), encoding="utf-8")
    return path


class RequestedAuthSchemaValidatorTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            requested_auth_path = (
                ROOT / "fixtures" / "valid" / fixture_name / "input"
                / "RequestedAuth.json"
            )
            with self.subTest(fixture=fixture_name):
                result = validate_requested_auth_schema(requested_auth_path)
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def _validate_modified(self, modify) -> dict:
        with temporary_test_directory('static-validation-requested-auth-schema-tests') as tmp:
            requested_auth = _valid_requested_auth()
            modify(requested_auth)
            path = _write_temp_requested_auth(Path(tmp), requested_auth)
            return validate_requested_auth_schema(path)

    def _assert_schema_failure(self, result: dict, *, path_fragment: str) -> None:
        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "INVALID_ARTIFACT_SCHEMA")
        self.assertEqual(diagnostic["component"], "static_schema_validator")
        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn(path_fragment, diagnostic["message"])

    def test_requested_connectors_missing_fails(self) -> None:
        def modify(requested_auth: dict) -> None:
            del requested_auth["requested_connectors"]

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.requested_connectors",
        )

    def test_requested_connectors_not_list_fails(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_connectors"] = {"connector_name": "x"}

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.requested_connectors",
        )

    def test_connector_entry_not_object_fails(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_connectors"] = ["not-an-object"]

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.requested_connectors[0]",
        )

    def test_connector_name_not_string_fails(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_connectors"][0]["connector_name"] = 5

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.requested_connectors[0].connector_name",
        )

    def test_scope_not_string_fails(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_connectors"][0]["scope"] = ["read"]

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.requested_connectors[0].scope",
        )

    def test_requested_tools_not_list_fails_if_present(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_tools"] = {"tool_name": "x"}

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.requested_tools",
        )

    def test_requested_tool_entry_not_object_fails(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_tools"] = ["not-an-object"]

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.requested_tools[0]",
        )

    def test_requested_tools_absent_passes(self) -> None:
        def modify(requested_auth: dict) -> None:
            del requested_auth["requested_tools"]

        result = self._validate_modified(modify)
        self.assertTrue(result["ok"])

    def test_diagnostic_includes_artifact_and_json_path(self) -> None:
        def modify(requested_auth: dict) -> None:
            requested_auth["requested_tools"][0]["tool_name"] = None

        result = self._validate_modified(modify)
        diagnostic = result["diagnostic"]

        self.assertEqual(diagnostic["artifact"], "RequestedAuth.json")
        self.assertIn("RequestedAuth.json", diagnostic["message"])
        self.assertIn("$.requested_tools[0].tool_name", diagnostic["message"])


class RequestedAuthSchemaPhasingTests(unittest.TestCase):
    def _validate_inputs_with_requested_auth(
        self, requested_auth: object, *, stop_on_first_error: bool = True
    ) -> dict:
        with temporary_test_directory('static-validation-requested-auth-schema-tests') as tmp:
            path = _write_temp_requested_auth(Path(tmp), requested_auth)
            return validate_static_inputs(
                SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json",
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                path,
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json",
                stop_on_first_error=stop_on_first_error,
            )

    def test_aggregate_mode_schema_failure_gates_interpretation(self) -> None:
        # stop_on_first_error=False must still gate interpretation validators
        # behind the schema phase: a non-list requested_connectors returns only
        # the schema diagnostic.
        requested_auth = _valid_requested_auth()
        requested_auth["requested_connectors"] = "not-a-list"

        result = self._validate_inputs_with_requested_auth(
            requested_auth, stop_on_first_error=False
        )

        self.assertFalse(result["ok"])
        self.assertEqual(len(result["diagnostics"]), 1)
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )
        self.assertEqual(
            result["diagnostics"][0]["artifact"], "RequestedAuth.json"
        )

    def test_float_fails_in_authority_phase_before_schema(self) -> None:
        # A float in RequestedAuth is rejected by the authority-value phase before
        # schema validation runs.
        requested_auth = _valid_requested_auth()
        requested_auth["requested_connectors"][0]["limit"] = 1.0

        result = self._validate_inputs_with_requested_auth(requested_auth)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "DISALLOWED_AUTHORITY_VALUE"
        )


if __name__ == "__main__":
    unittest.main()
