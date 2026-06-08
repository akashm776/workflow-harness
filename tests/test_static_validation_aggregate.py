from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from compiler.static_validation import validate_static_inputs


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)


class StaticValidationAggregateTests(unittest.TestCase):
    def test_valid_fixtures_pass_aggregate_static_validation(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            result = validate_static_inputs(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "NodeTypeRegistry.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "ApprovalRequests.json",
            )

            with self.subTest(fixture=fixture_name):
                self.assertTrue(result["ok"])
                self.assertEqual(result["diagnostics"], [])

    def test_stop_on_first_error_returns_only_first_diagnostic(self) -> None:
        success = {"ok": True, "diagnostic": None}
        invalid_endpoint = {
            "ok": False,
            "diagnostic": {
                "error_code": "INVALID_EDGE_ENDPOINT",
                "component": "graph_validator",
                "artifact": "WorkflowSpec.json",
                "message": "invalid edge endpoint in workflow graph: to:ghost-1",
            },
        }
        illegal_cycle = {
            "ok": False,
            "diagnostic": {
                "error_code": "ILLEGAL_GRAPH_CYCLE",
                "component": "graph_validator",
                "artifact": "WorkflowSpec.json",
                "message": "cycle detected in workflow graph: a, b",
            },
        }

        with patch(
            "compiler.static_validation.validate_authority_values", return_value=success
        ), patch(
            "compiler.static_validation.validate_workflow_spec_schema", return_value=success
        ), patch(
            "compiler.static_validation.validate_node_type_registry_schema",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_requested_auth_schema",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_approval_requests_schema",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_execution_bindings",
            return_value=success,
        ), patch("compiler.static_validation.validate_unknown_node_types", return_value=success), patch(
            "compiler.static_validation.validate_invalid_edge_endpoints", return_value=invalid_endpoint
        ), patch(
            "compiler.static_validation.validate_illegal_graph_cycle", return_value=illegal_cycle
        ) as cycle_mock, patch(
            "compiler.static_validation.validate_disconnected_graph", return_value=success
        ) as disconnected_mock, patch(
            "compiler.static_validation.validate_invalid_fan_out", return_value=success
        ) as fanout_mock, patch(
            "compiler.static_validation.validate_missing_required_scope", return_value=success
        ) as scope_mock, patch(
            "compiler.static_validation.validate_ambiguous_approval_subjects", return_value=success
        ) as approval_mock:
            result = validate_static_inputs(
                "workflow.json",
                "registry.json",
                "requested.json",
                "approval.json",
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostics"],
            [invalid_endpoint["diagnostic"]],
        )
        cycle_mock.assert_not_called()
        disconnected_mock.assert_not_called()
        fanout_mock.assert_not_called()
        scope_mock.assert_not_called()
        approval_mock.assert_not_called()

    def test_aggregate_order_prefers_unknown_node_type_before_graph_checks(self) -> None:
        workflow_spec = {
            "nodes": [
                {"node_id": "unknown-1", "node_type": "mystery"},
                {"node_id": "retrieve-1", "node_type": "retrieve"},
                {"node_id": "synthesize-1", "node_type": "synthesize"},
                {"node_id": "synthesize-2", "node_type": "synthesize"},
                {"node_id": "isolated-1", "node_type": "retrieve"},
            ],
            "edges": [
                {"from_node_id": "retrieve-1", "to_node_id": "ghost-1"},
                {"from_node_id": "retrieve-1", "to_node_id": "synthesize-1"},
                {"from_node_id": "retrieve-1", "to_node_id": "synthesize-2"},
                {"from_node_id": "synthesize-1", "to_node_id": "retrieve-1"},
            ],
        }
        node_type_registry = {
            "node_types": [
                {"node_type": "retrieve", "max_outgoing_edges": 1},
                {"node_type": "synthesize", "max_outgoing_edges": 1},
            ]
        }
        requested_auth = {
            "requested_connectors": [
                {"connector_name": "fixture-catalog", "scope": "read:fixtures"}
            ]
        }
        approval_requests = {
            "requests": [
                {
                    "request_id": "approval-request-001",
                    "node_id": "retrieve-1",
                    "approval_subject_hash": "approval-subject-001",
                }
            ]
        }

        def fake_load_json(path: str | Path) -> dict:
            name = Path(path).name
            if name == "workflow.json":
                return workflow_spec
            if name == "registry.json":
                return node_type_registry
            if name == "requested.json":
                return requested_auth
            if name == "approval.json":
                return approval_requests
            raise AssertionError(f"unexpected path: {path}")

        with patch("compiler.static_validation._load_json", side_effect=fake_load_json), patch(
            "compiler.static_validation.validate_workflow_spec_schema",
            return_value={"ok": True, "diagnostic": None},
        ), patch(
            "compiler.static_validation.validate_node_type_registry_schema",
            return_value={"ok": True, "diagnostic": None},
        ), patch(
            "compiler.static_validation.validate_requested_auth_schema",
            return_value={"ok": True, "diagnostic": None},
        ), patch(
            "compiler.static_validation.validate_approval_requests_schema",
            return_value={"ok": True, "diagnostic": None},
        ), patch(
            "compiler.static_validation.validate_unsupported_execution_bindings",
            return_value={"ok": True, "diagnostic": None},
        ):
            result = validate_static_inputs(
                "workflow.json",
                "registry.json",
                "requested.json",
                "approval.json",
            )

        self.assertFalse(result["ok"])
        self.assertEqual(len(result["diagnostics"]), 1)
        self.assertEqual(result["diagnostics"][0]["error_code"], "UNKNOWN_NODE_TYPE")

    def test_stop_on_first_error_false_returns_multiple_diagnostics_in_order(self) -> None:
        unknown_node_type = {
            "ok": False,
            "diagnostic": {
                "error_code": "UNKNOWN_NODE_TYPE",
                "component": "graph_validator",
                "artifact": "WorkflowSpec.json",
                "message": "unknown node type: mystery",
            },
        }
        invalid_endpoint = {
            "ok": False,
            "diagnostic": {
                "error_code": "INVALID_EDGE_ENDPOINT",
                "component": "graph_validator",
                "artifact": "WorkflowSpec.json",
                "message": "invalid edge endpoint in workflow graph: to:ghost-1",
            },
        }
        missing_scope = {
            "ok": False,
            "diagnostic": {
                "error_code": "MISSING_REQUIRED_SCOPE",
                "component": "scope_validator",
                "artifact": "RequestedAuth.json",
                "message": "missing required scope for connector: fixture-catalog",
            },
        }
        success = {"ok": True, "diagnostic": None}

        with patch(
            "compiler.static_validation.validate_authority_values",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_workflow_spec_schema",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_node_type_registry_schema",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_requested_auth_schema",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_approval_requests_schema",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_execution_bindings",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unknown_node_types",
            return_value=unknown_node_type,
        ), patch(
            "compiler.static_validation.validate_invalid_edge_endpoints",
            return_value=invalid_endpoint,
        ), patch(
            "compiler.static_validation.validate_illegal_graph_cycle",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_disconnected_graph",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_invalid_fan_out",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_missing_required_scope",
            return_value=missing_scope,
        ), patch(
            "compiler.static_validation.validate_ambiguous_approval_subjects",
            return_value=success,
        ):
            result = validate_static_inputs(
                "workflow.json",
                "registry.json",
                "requested.json",
                "approval.json",
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            result["diagnostics"],
            [
                unknown_node_type["diagnostic"],
                invalid_endpoint["diagnostic"],
                missing_scope["diagnostic"],
            ],
        )


if __name__ == "__main__":
    unittest.main()
