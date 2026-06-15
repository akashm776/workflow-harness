from __future__ import annotations

import json
from pathlib import Path
from tests.test_temp_utils import temporary_test_directory
import unittest

from compiler.static_validation import (
    validate_static_inputs,
    validate_workflow_spec_schema,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = ("simple-workflow", "approval-required-workflow")
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"


def _write_temp_workflow_spec(tmp_dir: Path, workflow_spec: object) -> Path:
    path = tmp_dir / "WorkflowSpec.json"
    path.write_text(json.dumps(workflow_spec, allow_nan=True), encoding="utf-8")
    return path


def _valid_workflow_spec() -> dict:
    return json.loads(
        (SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json").read_text(encoding="utf-8")
    )


class WorkflowSpecSchemaValidatorTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            workflow_spec_path = (
                ROOT / "fixtures" / "valid" / fixture_name / "input" / "WorkflowSpec.json"
            )
            with self.subTest(fixture=fixture_name):
                result = validate_workflow_spec_schema(workflow_spec_path)
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def _validate_modified(self, modify) -> dict:
        with temporary_test_directory('static-validation-workflow-spec-schema-tests') as tmp:
            workflow_spec = _valid_workflow_spec()
            modify(workflow_spec)
            path = _write_temp_workflow_spec(Path(tmp), workflow_spec)
            return validate_workflow_spec_schema(path)

    def test_missing_workflow_revision_id_fails(self) -> None:
        def modify(workflow_spec: dict) -> None:
            del workflow_spec["workflow_revision_id"]

        result = self._validate_modified(modify)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostic"]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )
        self.assertIn("$.workflow_revision_id", result["diagnostic"]["message"])

    def test_non_string_workflow_revision_id_fails(self) -> None:
        def modify(workflow_spec: dict) -> None:
            workflow_spec["workflow_revision_id"] = 7

        result = self._validate_modified(modify)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostic"]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )
        self.assertIn("$.workflow_revision_id", result["diagnostic"]["message"])

    def test_nodes_not_list_fails(self) -> None:
        def modify(workflow_spec: dict) -> None:
            workflow_spec["nodes"] = {"node_id": "retrieve-1"}

        result = self._validate_modified(modify)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostic"]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )
        self.assertIn("$.nodes", result["diagnostic"]["message"])

    def test_node_id_not_string_fails(self) -> None:
        def modify(workflow_spec: dict) -> None:
            workflow_spec["nodes"][0]["node_id"] = 123

        result = self._validate_modified(modify)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostic"]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )
        self.assertIn("$.nodes[0].node_id", result["diagnostic"]["message"])

    def test_diagnostic_includes_artifact_and_json_path(self) -> None:
        def modify(workflow_spec: dict) -> None:
            workflow_spec["edges"][0]["to_node_id"] = None

        result = self._validate_modified(modify)

        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertEqual(diagnostic["component"], "static_schema_validator")
        self.assertIn("WorkflowSpec.json", diagnostic["message"])
        self.assertIn("$.edges[0].to_node_id", diagnostic["message"])


class WorkflowSpecSchemaOrderingTests(unittest.TestCase):
    """Schema validation runs after authority-value validation, before graph."""

    def _validate_inputs_with_workflow_spec(
        self, workflow_spec: object, *, stop_on_first_error: bool = True
    ) -> dict:
        with temporary_test_directory('static-validation-workflow-spec-schema-tests') as tmp:
            path = _write_temp_workflow_spec(Path(tmp), workflow_spec)
            return validate_static_inputs(
                path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                SIMPLE_FIXTURE_INPUT / "RequestedAuth.json",
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json",
                stop_on_first_error=stop_on_first_error,
            )

    def test_authority_value_validation_wins_over_schema(self) -> None:
        # NaN in workflow_revision_id is both a disallowed authority value and a
        # non-string schema violation. Authority-value validation runs first.
        workflow_spec = _valid_workflow_spec()
        workflow_spec["workflow_revision_id"] = float("nan")

        result = self._validate_inputs_with_workflow_spec(workflow_spec)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "DISALLOWED_AUTHORITY_VALUE"
        )

    def test_schema_validation_wins_over_graph_validators(self) -> None:
        # nodes as a non-list is a schema violation. Schema validation must run
        # before graph validators, which would otherwise misbehave on it.
        workflow_spec = _valid_workflow_spec()
        workflow_spec["nodes"] = "not-a-list"

        result = self._validate_inputs_with_workflow_spec(workflow_spec)

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )
        self.assertIn("$.nodes", result["diagnostics"][0]["message"])

    def test_aggregate_mode_schema_failure_gates_graph_validators(self) -> None:
        # stop_on_first_error=False must still gate graph validators behind the
        # schema phase: a non-list nodes returns only the schema diagnostic and
        # never lets graph validators interpret the malformed shape (no crash).
        workflow_spec = _valid_workflow_spec()
        workflow_spec["nodes"] = "not-a-list"

        result = self._validate_inputs_with_workflow_spec(
            workflow_spec, stop_on_first_error=False
        )

        self.assertFalse(result["ok"])
        self.assertEqual(len(result["diagnostics"]), 1)
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "INVALID_ARTIFACT_SCHEMA"
        )

    def test_aggregate_mode_authority_failure_gates_schema_and_graph(self) -> None:
        # stop_on_first_error=False must gate both schema and graph phases behind
        # the authority-value phase: a NaN revision id returns only the
        # authority-value diagnostic, not a schema or graph diagnostic.
        workflow_spec = _valid_workflow_spec()
        workflow_spec["workflow_revision_id"] = float("nan")

        result = self._validate_inputs_with_workflow_spec(
            workflow_spec, stop_on_first_error=False
        )

        self.assertFalse(result["ok"])
        self.assertEqual(len(result["diagnostics"]), 1)
        self.assertEqual(
            result["diagnostics"][0]["error_code"], "DISALLOWED_AUTHORITY_VALUE"
        )


if __name__ == "__main__":
    unittest.main()
