from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from compiler.static_validation import (
    validate_static_inputs,
    validate_unsupported_execution_bindings,
)


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"


def _valid_workflow_spec() -> dict:
    return json.loads(
        (SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json").read_text(encoding="utf-8")
    )


def _write_temp_workflow_spec(tmp_dir: Path, workflow_spec: object) -> Path:
    path = tmp_dir / "WorkflowSpec.json"
    path.write_text(json.dumps(workflow_spec), encoding="utf-8")
    return path


class UnsupportedExecutionBindingValidationTests(unittest.TestCase):
    def test_valid_fixtures_pass(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            result = validate_unsupported_execution_bindings(
                fixture_input / "WorkflowSpec.json"
            )

            with self.subTest(fixture=fixture_name):
                self.assertTrue(result["ok"])
                self.assertIsNone(result["diagnostic"])

    def _validate_modified(self, modify) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _valid_workflow_spec()
            modify(workflow_spec)
            path = _write_temp_workflow_spec(Path(tmp), workflow_spec)
            return validate_unsupported_execution_bindings(path)

    def _validate_modified_via_static_inputs(self, modify) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _valid_workflow_spec()
            modify(workflow_spec)
            path = _write_temp_workflow_spec(Path(tmp), workflow_spec)
            return validate_static_inputs(
                path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                SIMPLE_FIXTURE_INPUT / "RequestedAuth.json",
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json",
            )

    def test_node_with_harness_style_tool_binding_is_rejected(self) -> None:
        def modify(workflow_spec: dict) -> None:
            workflow_spec["nodes"][0]["tool_binding"] = {
                "tool_name": "future-tool"
            }

        result = self._validate_modified(modify)

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_EXECUTION_BINDING")
        self.assertEqual(diagnostic["component"], "execution_binding_validator")
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("tool_binding", diagnostic["message"])
        self.assertIn("$.nodes[0].tool_binding", diagnostic["message"])

    def test_node_with_mcp_execution_intent_is_rejected(self) -> None:
        def modify(workflow_spec: dict) -> None:
            workflow_spec["nodes"][0]["task"]["mcp_server"] = "catalog"
            workflow_spec["nodes"][0]["task"]["mcp_tool"] = "tools/call"

        result = self._validate_modified(modify)

        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_EXECUTION_BINDING")
        self.assertIn("mcp_server", diagnostic["message"])
        self.assertIn("mcp_tool", diagnostic["message"])
        self.assertIn("$.nodes[0].task.mcp_server", diagnostic["message"])
        self.assertIn("$.nodes[0].task.mcp_tool", diagnostic["message"])

    def test_aggregate_static_validation_surfaces_unsupported_execution_binding(self) -> None:
        def modify(workflow_spec: dict) -> None:
            workflow_spec["nodes"][0]["task"]["mcp_binding"] = {
                "mcp_server": "catalog",
                "mcp_tool": "tools/call",
            }

        result = self._validate_modified_via_static_inputs(modify)

        self.assertFalse(result["ok"])
        self.assertEqual(len(result["diagnostics"]), 1)
        diagnostic = result["diagnostics"][0]
        self.assertEqual(diagnostic["error_code"], "UNSUPPORTED_EXECUTION_BINDING")
        self.assertEqual(diagnostic["component"], "execution_binding_validator")
        self.assertEqual(diagnostic["artifact"], "WorkflowSpec.json")
        self.assertIn("mcp_binding", diagnostic["message"])


if __name__ == "__main__":
    unittest.main()
