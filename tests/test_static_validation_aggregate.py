from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from compiler.static_validation import validate_static_inputs


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)
SIMPLE_FIXTURE_INPUT = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


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
            "compiler.static_validation.validate_unsupported_secret_fields",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_capability_envelope_fields",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_safeguard_authority_claims",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_authority_artifacts",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_approval_bindings",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_execution_bindings",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_runtime_reporting_claims",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_audit_evidence_authority_claims",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_approval_scope_claims",
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
            "compiler.static_validation.validate_unsupported_secret_fields",
            return_value={"ok": True, "diagnostic": None},
        ), patch(
            "compiler.static_validation.validate_unsupported_capability_envelope_fields",
            return_value={"ok": True, "diagnostic": None},
        ), patch(
            "compiler.static_validation.validate_unsupported_safeguard_authority_claims",
            return_value={"ok": True, "diagnostic": None},
        ), patch(
            "compiler.static_validation.validate_unsupported_authority_artifacts",
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
            "compiler.static_validation.validate_unsupported_secret_fields",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_capability_envelope_fields",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_safeguard_authority_claims",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_authority_artifacts",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_approval_bindings",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_execution_bindings",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_runtime_reporting_claims",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_audit_evidence_authority_claims",
            return_value=success,
        ), patch(
            "compiler.static_validation.validate_unsupported_approval_scope_claims",
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

    def test_aggregate_static_validation_preserves_current_interpretation_order(
        self,
    ) -> None:
        success = {"ok": True, "diagnostic": None}

        def failure(
            error_code: str,
            component: str,
            artifact: str,
            message: str,
        ) -> dict[str, object]:
            return {
                "ok": False,
                "diagnostic": {
                    "error_code": error_code,
                    "component": component,
                    "artifact": artifact,
                    "message": message,
                },
            }

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
            "compiler.static_validation.validate_unsupported_secret_fields",
            side_effect=[
                failure(
                    "UNSUPPORTED_SECRET_FIELD",
                    "secret_field_validator",
                    "WorkflowSpec.json",
                    "secret workflow",
                ),
                failure(
                    "UNSUPPORTED_SECRET_FIELD",
                    "secret_field_validator",
                    "RequestedAuth.json",
                    "secret requested",
                ),
                failure(
                    "UNSUPPORTED_SECRET_FIELD",
                    "secret_field_validator",
                    "ApprovalRequests.json",
                    "secret approval",
                ),
            ],
        ), patch(
            "compiler.static_validation.validate_unsupported_capability_envelope_fields",
            side_effect=[
                failure(
                    "UNSUPPORTED_CAPABILITY_ENVELOPE",
                    "capability_envelope_validator",
                    "WorkflowSpec.json",
                    "capability workflow",
                ),
                failure(
                    "UNSUPPORTED_CAPABILITY_ENVELOPE",
                    "capability_envelope_validator",
                    "RequestedAuth.json",
                    "capability requested",
                ),
                failure(
                    "UNSUPPORTED_CAPABILITY_ENVELOPE",
                    "capability_envelope_validator",
                    "ApprovalRequests.json",
                    "capability approval",
                ),
            ],
        ), patch(
            "compiler.static_validation.validate_unsupported_safeguard_authority_claims",
            side_effect=[
                failure(
                    "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
                    "safeguard_authority_claim_validator",
                    "WorkflowSpec.json",
                    "safeguard workflow",
                ),
                failure(
                    "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
                    "safeguard_authority_claim_validator",
                    "RequestedAuth.json",
                    "safeguard requested",
                ),
                failure(
                    "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
                    "safeguard_authority_claim_validator",
                    "ApprovalRequests.json",
                    "safeguard approval",
                ),
            ],
        ), patch(
            "compiler.static_validation.validate_unsupported_authority_artifacts",
            side_effect=[
                failure(
                    "UNSUPPORTED_AUTHORITY_ARTIFACT",
                    "authority_artifact_ownership_validator",
                    "WorkflowSpec.json",
                    "authority workflow",
                ),
                failure(
                    "UNSUPPORTED_AUTHORITY_ARTIFACT",
                    "authority_artifact_ownership_validator",
                    "RequestedAuth.json",
                    "authority requested",
                ),
                failure(
                    "UNSUPPORTED_AUTHORITY_ARTIFACT",
                    "authority_artifact_ownership_validator",
                    "ApprovalRequests.json",
                    "authority approval",
                ),
            ],
        ), patch(
            "compiler.static_validation.validate_unsupported_approval_bindings",
            side_effect=[
                failure(
                    "UNSUPPORTED_APPROVAL_BINDING",
                    "approval_binding_validator",
                    "WorkflowSpec.json",
                    "approval-binding workflow",
                ),
                failure(
                    "UNSUPPORTED_APPROVAL_BINDING",
                    "approval_binding_validator",
                    "RequestedAuth.json",
                    "approval-binding requested",
                ),
                failure(
                    "UNSUPPORTED_APPROVAL_BINDING",
                    "approval_binding_validator",
                    "ApprovalRequests.json",
                    "approval-binding approval",
                ),
            ],
        ), patch(
            "compiler.static_validation.validate_unsupported_execution_bindings",
            return_value=failure(
                "UNSUPPORTED_EXECUTION_BINDING",
                "execution_binding_validator",
                "WorkflowSpec.json",
                "execution binding",
            ),
        ), patch(
            "compiler.static_validation.validate_unsupported_runtime_reporting_claims",
            side_effect=[
                failure(
                    "UNSUPPORTED_RUNTIME_REPORTING_CLAIM",
                    "runtime_reporting_boundary_validator",
                    "WorkflowSpec.json",
                    "runtime-reporting workflow",
                ),
                failure(
                    "UNSUPPORTED_RUNTIME_REPORTING_CLAIM",
                    "runtime_reporting_boundary_validator",
                    "RequestedAuth.json",
                    "runtime-reporting requested",
                ),
                failure(
                    "UNSUPPORTED_RUNTIME_REPORTING_CLAIM",
                    "runtime_reporting_boundary_validator",
                    "ApprovalRequests.json",
                    "runtime-reporting approval",
                ),
            ],
        ), patch(
            "compiler.static_validation.validate_unsupported_audit_evidence_authority_claims",
            side_effect=[
                failure(
                    "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
                    "audit_evidence_authority_validator",
                    "WorkflowSpec.json",
                    "audit-evidence workflow",
                ),
                failure(
                    "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
                    "audit_evidence_authority_validator",
                    "RequestedAuth.json",
                    "audit-evidence requested",
                ),
                failure(
                    "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
                    "audit_evidence_authority_validator",
                    "ApprovalRequests.json",
                    "audit-evidence approval",
                ),
            ],
        ), patch(
            "compiler.static_validation.validate_unsupported_approval_scope_claims",
            side_effect=[
                failure(
                    "UNSUPPORTED_APPROVAL_SCOPE_CLAIM",
                    "approval_scope_validator",
                    "WorkflowSpec.json",
                    "approval-scope workflow",
                ),
                failure(
                    "UNSUPPORTED_APPROVAL_SCOPE_CLAIM",
                    "approval_scope_validator",
                    "RequestedAuth.json",
                    "approval-scope requested",
                ),
                failure(
                    "UNSUPPORTED_APPROVAL_SCOPE_CLAIM",
                    "approval_scope_validator",
                    "ApprovalRequests.json",
                    "approval-scope approval",
                ),
            ],
        ), patch(
            "compiler.static_validation.validate_unknown_node_types",
            return_value=failure(
                "UNKNOWN_NODE_TYPE",
                "graph_validator",
                "WorkflowSpec.json",
                "unknown node type",
            ),
        ), patch(
            "compiler.static_validation.validate_invalid_edge_endpoints",
            return_value=failure(
                "INVALID_EDGE_ENDPOINT",
                "graph_validator",
                "WorkflowSpec.json",
                "invalid endpoint",
            ),
        ), patch(
            "compiler.static_validation.validate_illegal_graph_cycle",
            return_value=failure(
                "ILLEGAL_GRAPH_CYCLE",
                "graph_validator",
                "WorkflowSpec.json",
                "illegal cycle",
            ),
        ), patch(
            "compiler.static_validation.validate_disconnected_graph",
            return_value=failure(
                "DISCONNECTED_GRAPH",
                "graph_validator",
                "WorkflowSpec.json",
                "disconnected graph",
            ),
        ), patch(
            "compiler.static_validation.validate_invalid_fan_out",
            return_value=failure(
                "INVALID_FAN_OUT",
                "graph_validator",
                "WorkflowSpec.json",
                "invalid fan out",
            ),
        ), patch(
            "compiler.static_validation.validate_missing_required_scope",
            return_value=failure(
                "MISSING_REQUIRED_SCOPE",
                "scope_validator",
                "RequestedAuth.json",
                "missing scope",
            ),
        ), patch(
            "compiler.static_validation.validate_ambiguous_approval_subjects",
            return_value=failure(
                "AMBIGUOUS_APPROVAL_SUBJECT",
                "approval_validator",
                "ApprovalRequests.json",
                "ambiguous approval",
            ),
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
            [diagnostic["message"] for diagnostic in result["diagnostics"]],
            [
                "secret workflow",
                "secret requested",
                "secret approval",
                "capability workflow",
                "capability requested",
                "capability approval",
                "safeguard workflow",
                "safeguard requested",
                "safeguard approval",
                "authority workflow",
                "authority requested",
                "authority approval",
                "approval-binding workflow",
                "approval-binding requested",
                "approval-binding approval",
                "execution binding",
                "runtime-reporting workflow",
                "runtime-reporting requested",
                "runtime-reporting approval",
                "audit-evidence workflow",
                "audit-evidence requested",
                "audit-evidence approval",
                "approval-scope workflow",
                "approval-scope requested",
                "approval-scope approval",
                "unknown node type",
                "invalid endpoint",
                "illegal cycle",
                "disconnected graph",
                "invalid fan out",
                "missing scope",
                "ambiguous approval",
            ],
        )

    def test_requested_auth_secret_and_capability_keep_documented_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["credentials"] = {"mode": "forbidden"}
            requested_auth["approved_capabilities"] = ["future-only"]

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            [diagnostic["error_code"] for diagnostic in result["diagnostics"]],
            [
                "UNSUPPORTED_SECRET_FIELD",
                "UNSUPPORTED_CAPABILITY_ENVELOPE",
            ],
        )
        self.assertEqual(
            [diagnostic["component"] for diagnostic in result["diagnostics"]],
            [
                "secret_field_validator",
                "capability_envelope_validator",
            ],
        )

    def test_requested_auth_capability_and_safeguard_claims_keep_documented_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["approved_capabilities"] = ["future-only"]
            requested_auth["unblock_execution"] = True

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            [diagnostic["error_code"] for diagnostic in result["diagnostics"]],
            [
                "UNSUPPORTED_CAPABILITY_ENVELOPE",
                "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
            ],
        )
        self.assertEqual(
            [diagnostic["component"] for diagnostic in result["diagnostics"]],
            [
                "capability_envelope_validator",
                "safeguard_authority_claim_validator",
            ],
        )

    def test_workflow_safeguard_claim_and_execution_binding_keep_documented_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            workflow_spec["nodes"][0]["authorized_by_safeguard"] = True
            workflow_spec["nodes"][0]["tool_binding"] = {"tool_name": "future-tool"}

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            [diagnostic["error_code"] for diagnostic in result["diagnostics"]],
            [
                "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
                "UNSUPPORTED_EXECUTION_BINDING",
            ],
        )
        self.assertEqual(
            [diagnostic["component"] for diagnostic in result["diagnostics"]],
            [
                "safeguard_authority_claim_validator",
                "execution_binding_validator",
            ],
        )

    def test_requested_auth_safeguard_and_authority_artifact_keep_documented_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            requested_auth["grant_capabilities"] = True
            requested_auth["execution_manifest"] = {"display_only": True}

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            [diagnostic["error_code"] for diagnostic in result["diagnostics"]],
            [
                "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
                "UNSUPPORTED_AUTHORITY_ARTIFACT",
            ],
        )
        self.assertEqual(
            [diagnostic["component"] for diagnostic in result["diagnostics"]],
            [
                "safeguard_authority_claim_validator",
                "authority_artifact_ownership_validator",
            ],
        )

    def test_workflow_authority_artifact_and_execution_binding_keep_documented_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            workflow_spec["nodes"][0]["execution_manifest"] = {"display_only": True}
            workflow_spec["nodes"][0]["tool_binding"] = {"tool_name": "future-tool"}

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            [diagnostic["error_code"] for diagnostic in result["diagnostics"]],
            [
                "UNSUPPORTED_AUTHORITY_ARTIFACT",
                "UNSUPPORTED_EXECUTION_BINDING",
            ],
        )
        self.assertEqual(
            [diagnostic["component"] for diagnostic in result["diagnostics"]],
            [
                "authority_artifact_ownership_validator",
                "execution_binding_validator",
            ],
        )

    def test_workflow_authority_artifact_approval_binding_and_execution_binding_keep_documented_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            # authority-artifact, approval-binding, and execution-binding keys on
            # the same node must surface in the documented Phase 3 order.
            workflow_spec["nodes"][0]["execution_manifest"] = {"display_only": True}
            workflow_spec["nodes"][0]["reusable_approval"] = {"display_only": True}
            workflow_spec["nodes"][0]["tool_binding"] = {"tool_name": "future-tool"}

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            [diagnostic["error_code"] for diagnostic in result["diagnostics"]],
            [
                "UNSUPPORTED_AUTHORITY_ARTIFACT",
                "UNSUPPORTED_APPROVAL_BINDING",
                "UNSUPPORTED_EXECUTION_BINDING",
            ],
        )
        self.assertEqual(
            [diagnostic["component"] for diagnostic in result["diagnostics"]],
            [
                "authority_artifact_ownership_validator",
                "approval_binding_validator",
                "execution_binding_validator",
            ],
        )

    def test_workflow_execution_binding_and_runtime_reporting_keep_documented_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            # execution-binding and runtime-reporting keys on the same node must
            # surface in the documented Phase 3 order.
            workflow_spec["nodes"][0]["tool_binding"] = {"tool_name": "future-tool"}
            workflow_spec["nodes"][0]["broker_request"] = {"display_only": True}

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            [diagnostic["error_code"] for diagnostic in result["diagnostics"]],
            [
                "UNSUPPORTED_EXECUTION_BINDING",
                "UNSUPPORTED_RUNTIME_REPORTING_CLAIM",
            ],
        )
        self.assertEqual(
            [diagnostic["component"] for diagnostic in result["diagnostics"]],
            [
                "execution_binding_validator",
                "runtime_reporting_boundary_validator",
            ],
        )

    def test_workflow_runtime_reporting_and_audit_evidence_keep_documented_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            # runtime-reporting and audit-evidence keys on the same node must
            # surface in the documented Phase 3 order.
            workflow_spec["nodes"][0]["broker_request"] = {"display_only": True}
            workflow_spec["nodes"][0]["evidence_approval"] = {"display_only": True}

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            [diagnostic["error_code"] for diagnostic in result["diagnostics"]],
            [
                "UNSUPPORTED_RUNTIME_REPORTING_CLAIM",
                "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
            ],
        )
        self.assertEqual(
            [diagnostic["component"] for diagnostic in result["diagnostics"]],
            [
                "runtime_reporting_boundary_validator",
                "audit_evidence_authority_validator",
            ],
        )

    def test_workflow_audit_evidence_and_approval_scope_keep_documented_order(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow_spec = _load_json(SIMPLE_FIXTURE_INPUT / "WorkflowSpec.json")
            requested_auth = _load_json(SIMPLE_FIXTURE_INPUT / "RequestedAuth.json")
            approval_requests = _load_json(
                SIMPLE_FIXTURE_INPUT / "ApprovalRequests.json"
            )
            # audit-evidence and approval-scope keys on the same node must surface
            # in the documented Phase 3 order.
            workflow_spec["nodes"][0]["evidence_approval"] = {"display_only": True}
            workflow_spec["nodes"][0]["cross_run_approval"] = {"display_only": True}

            workflow_spec_path = _write_json(
                Path(tmp) / "WorkflowSpec.json", workflow_spec
            )
            requested_auth_path = _write_json(
                Path(tmp) / "RequestedAuth.json", requested_auth
            )
            approval_requests_path = _write_json(
                Path(tmp) / "ApprovalRequests.json", approval_requests
            )

            result = validate_static_inputs(
                workflow_spec_path,
                SIMPLE_FIXTURE_INPUT / "NodeTypeRegistry.json",
                requested_auth_path,
                approval_requests_path,
                stop_on_first_error=False,
            )

        self.assertFalse(result["ok"])
        self.assertEqual(
            [diagnostic["error_code"] for diagnostic in result["diagnostics"]],
            [
                "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
                "UNSUPPORTED_APPROVAL_SCOPE_CLAIM",
            ],
        )
        self.assertEqual(
            [diagnostic["component"] for diagnostic in result["diagnostics"]],
            [
                "audit_evidence_authority_validator",
                "approval_scope_validator",
            ],
        )


if __name__ == "__main__":
    unittest.main()
