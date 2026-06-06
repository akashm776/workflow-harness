from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from compiler.static_validation import (
    validate_node_type_registry_schema,
    validate_static_inputs,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = ("simple-workflow", "approval-required-workflow")
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"


def _valid_registry() -> dict:
    return json.loads(
        (SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json").read_text(encoding="utf-8")
    )


def _write_temp_registry(tmp_dir: Path, registry: object) -> Path:
    path = tmp_dir / "NodeTypeRegistry.json"
    path.write_text(json.dumps(registry, allow_nan=True), encoding="utf-8")
    return path


class NodeTypeRegistrySchemaValidatorTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            registry_path = (
                ROOT / "fixtures" / "valid" / fixture_name / "input"
                / "NodeTypeRegistry.json"
            )
            with self.subTest(fixture=fixture_name):
                result = validate_node_type_registry_schema(registry_path)
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def _validate_modified(self, modify) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            registry = _valid_registry()
            modify(registry)
            path = _write_temp_registry(Path(tmp), registry)
            return validate_node_type_registry_schema(path)

    def _assert_schema_failure(self, result: dict, *, path_fragment: str) -> None:
        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "INVALID_ARTIFACT_SCHEMA")
        self.assertEqual(diagnostic["component"], "static_schema_validator")
        self.assertEqual(diagnostic["artifact"], "NodeTypeRegistry.json")
        self.assertIn(path_fragment, diagnostic["message"])

    def test_node_types_missing_fails(self) -> None:
        def modify(registry: dict) -> None:
            del registry["node_types"]

        self._assert_schema_failure(
            self._validate_modified(modify), path_fragment="$.node_types"
        )

    def test_node_types_not_list_fails(self) -> None:
        def modify(registry: dict) -> None:
            registry["node_types"] = {"node_type": "retrieve"}

        self._assert_schema_failure(
            self._validate_modified(modify), path_fragment="$.node_types"
        )

    def test_node_type_not_string_fails(self) -> None:
        def modify(registry: dict) -> None:
            registry["node_types"][0]["node_type"] = 5

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.node_types[0].node_type",
        )

    def test_max_outgoing_edges_bool_fails(self) -> None:
        def modify(registry: dict) -> None:
            registry["node_types"][0]["max_outgoing_edges"] = True

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.node_types[0].max_outgoing_edges",
        )

    def test_required_scopes_not_list_fails(self) -> None:
        def modify(registry: dict) -> None:
            registry["node_types"][0]["required_scopes"] = "jira.read"

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.node_types[0].required_scopes",
        )

    def test_required_scopes_item_not_string_fails(self) -> None:
        def modify(registry: dict) -> None:
            registry["node_types"][0]["required_scopes"] = ["jira.read", 7]

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.node_types[0].required_scopes[1]",
        )

    def test_side_effect_class_not_string_fails(self) -> None:
        def modify(registry: dict) -> None:
            registry["node_types"][0]["side_effect_class"] = 1

        self._assert_schema_failure(
            self._validate_modified(modify),
            path_fragment="$.node_types[0].side_effect_class",
        )

    def test_diagnostic_includes_artifact_and_json_path(self) -> None:
        def modify(registry: dict) -> None:
            registry["node_types"][0]["node_type"] = None

        result = self._validate_modified(modify)
        diagnostic = result["diagnostic"]

        self.assertEqual(diagnostic["artifact"], "NodeTypeRegistry.json")
        self.assertIn("NodeTypeRegistry.json", diagnostic["message"])
        self.assertIn("$.node_types[0].node_type", diagnostic["message"])


class NodeTypeRegistrySchemaPhasingTests(unittest.TestCase):
    def _validate_inputs_with_registry(
        self, registry: object, *, stop_on_first_error: bool = True
    ) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_temp_registry(Path(tmp), registry)
            return validate_static_inputs(
                SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json",
                path,
                SIMPLE_FIXTURE_INPUT / "RequestedAuth.json",
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json",
                stop_on_first_error=stop_on_first_error,
            )

    def test_max_outgoing_edges_float_fails_in_authority_phase(self) -> None:
        # A float (even an integral one) is rejected by the authority-value phase
        # before schema validation sees it.
        registry = _valid_registry()
        registry["node_types"][0]["max_outgoing_edges"] = 1.0

        result = self._validate_inputs_with_registry(registry)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "DISALLOWED_AUTHORITY_VALUE"
        )

    def test_aggregate_mode_schema_failure_gates_interpretation(self) -> None:
        # stop_on_first_error=False must still gate interpretation validators
        # behind the schema phase: a non-list node_types returns only the schema
        # diagnostic.
        registry = _valid_registry()
        registry["node_types"] = "not-a-list"

        result = self._validate_inputs_with_registry(
            registry, stop_on_first_error=False
        )

        self.assertFalse(result["ok"])
        self.assertEqual(len(result["diagnostics"]), 1)
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )
        self.assertEqual(
            result["diagnostics"][0]["artifact"], "NodeTypeRegistry.json"
        )


if __name__ == "__main__":
    unittest.main()
