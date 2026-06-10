from __future__ import annotations

from collections import defaultdict, deque
import json
from pathlib import Path
from typing import Any

from compiler.authority_value_validator import find_disallowed_authority_values


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_authority_values(
    artifact_path: str | Path, artifact_name: str
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = find_disallowed_authority_values(artifact)

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    detail = "; ".join(
        f"{finding['path']} ({finding['reason']})" for finding in findings
    )
    return {
        "ok": False,
        "diagnostic": {
            "error_code": "DISALLOWED_AUTHORITY_VALUE",
            "component": "authority_value_validator",
            "artifact": artifact_name,
            "message": (
                f"disallowed authority value in {artifact_name}: {detail}"
            ),
        },
    }


def _schema_diagnostic(artifact: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "diagnostic": {
            "error_code": "INVALID_ARTIFACT_SCHEMA",
            "component": "static_schema_validator",
            "artifact": artifact,
            "message": message,
        },
    }


def validate_workflow_spec_schema(workflow_spec_path: str | Path) -> dict[str, Any]:
    artifact = "WorkflowSpec.json"
    workflow_spec = _load_json(workflow_spec_path)

    if not isinstance(workflow_spec, dict):
        return _schema_diagnostic(artifact, "WorkflowSpec.json root $ must be an object")

    for field_name in (
        "schema_version",
        "graph_revision_id",
        "workflow_revision_id",
        "policy_bundle_digest",
    ):
        if not isinstance(workflow_spec.get(field_name), str):
            return _schema_diagnostic(
                artifact, f"WorkflowSpec.json field $.{field_name} must be a string"
            )

    nodes = workflow_spec.get("nodes")
    if not isinstance(nodes, list):
        return _schema_diagnostic(
            artifact, "WorkflowSpec.json field $.nodes must be a list"
        )

    edges = workflow_spec.get("edges")
    if not isinstance(edges, list):
        return _schema_diagnostic(
            artifact, "WorkflowSpec.json field $.edges must be a list"
        )

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            return _schema_diagnostic(
                artifact, f"WorkflowSpec.json field $.nodes[{index}] must be an object"
            )
        for field_name in ("node_id", "node_type"):
            if not isinstance(node.get(field_name), str):
                return _schema_diagnostic(
                    artifact,
                    f"WorkflowSpec.json field $.nodes[{index}].{field_name} "
                    "must be a string",
                )

    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            return _schema_diagnostic(
                artifact, f"WorkflowSpec.json field $.edges[{index}] must be an object"
            )
        for field_name in ("from_node_id", "to_node_id"):
            if not isinstance(edge.get(field_name), str):
                return _schema_diagnostic(
                    artifact,
                    f"WorkflowSpec.json field $.edges[{index}].{field_name} "
                    "must be a string",
                )

    return {"ok": True, "diagnostic": None}


def validate_node_type_registry_schema(
    node_type_registry_path: str | Path,
) -> dict[str, Any]:
    artifact = "NodeTypeRegistry.json"
    node_type_registry = _load_json(node_type_registry_path)

    if not isinstance(node_type_registry, dict):
        return _schema_diagnostic(artifact, "NodeTypeRegistry.json root $ must be an object")

    if not isinstance(node_type_registry.get("schema_version"), str):
        return _schema_diagnostic(
            artifact, "NodeTypeRegistry.json field $.schema_version must be a string"
        )

    node_types = node_type_registry.get("node_types")
    if not isinstance(node_types, list):
        return _schema_diagnostic(
            artifact, "NodeTypeRegistry.json field $.node_types must be a list"
        )

    for index, entry in enumerate(node_types):
        path = f"$.node_types[{index}]"
        if not isinstance(entry, dict):
            return _schema_diagnostic(
                artifact, f"NodeTypeRegistry.json field {path} must be an object"
            )

        if not isinstance(entry.get("node_type"), str):
            return _schema_diagnostic(
                artifact,
                f"NodeTypeRegistry.json field {path}.node_type must be a string",
            )

        if "max_outgoing_edges" in entry:
            max_outgoing_edges = entry["max_outgoing_edges"]
            # bool is a subclass of int; reject it explicitly.
            if isinstance(max_outgoing_edges, bool) or not isinstance(
                max_outgoing_edges, int
            ):
                return _schema_diagnostic(
                    artifact,
                    f"NodeTypeRegistry.json field {path}.max_outgoing_edges "
                    "must be an int",
                )

        if "required_scopes" in entry:
            required_scopes = entry["required_scopes"]
            if not isinstance(required_scopes, list):
                return _schema_diagnostic(
                    artifact,
                    f"NodeTypeRegistry.json field {path}.required_scopes "
                    "must be a list",
                )
            for scope_index, scope in enumerate(required_scopes):
                if not isinstance(scope, str):
                    return _schema_diagnostic(
                        artifact,
                        f"NodeTypeRegistry.json field "
                        f"{path}.required_scopes[{scope_index}] must be a string",
                    )

        if "side_effect_class" in entry and not isinstance(
            entry["side_effect_class"], str
        ):
            return _schema_diagnostic(
                artifact,
                f"NodeTypeRegistry.json field {path}.side_effect_class "
                "must be a string",
            )

    return {"ok": True, "diagnostic": None}


def validate_requested_auth_schema(requested_auth_path: str | Path) -> dict[str, Any]:
    artifact = "RequestedAuth.json"
    requested_auth = _load_json(requested_auth_path)

    if not isinstance(requested_auth, dict):
        return _schema_diagnostic(artifact, "RequestedAuth.json root $ must be an object")

    if not isinstance(requested_auth.get("schema_version"), str):
        return _schema_diagnostic(
            artifact, "RequestedAuth.json field $.schema_version must be a string"
        )

    # Authority reference fields present in fixtures must be strings when present.
    for field_name in ("node_id", "workflow_revision_id"):
        if field_name in requested_auth and not isinstance(
            requested_auth[field_name], str
        ):
            return _schema_diagnostic(
                artifact, f"RequestedAuth.json field $.{field_name} must be a string"
            )

    requested_connectors = requested_auth.get("requested_connectors")
    if not isinstance(requested_connectors, list):
        return _schema_diagnostic(
            artifact, "RequestedAuth.json field $.requested_connectors must be a list"
        )

    for index, connector in enumerate(requested_connectors):
        path = f"$.requested_connectors[{index}]"
        if not isinstance(connector, dict):
            return _schema_diagnostic(
                artifact, f"RequestedAuth.json field {path} must be an object"
            )
        if not isinstance(connector.get("connector_name"), str):
            return _schema_diagnostic(
                artifact,
                f"RequestedAuth.json field {path}.connector_name must be a string",
            )
        # scope is optional at the schema layer; missing scope is an
        # interpretation-phase concern. When present it must be a string.
        if "scope" in connector and not isinstance(connector["scope"], str):
            return _schema_diagnostic(
                artifact, f"RequestedAuth.json field {path}.scope must be a string"
            )

    requested_tools = requested_auth.get("requested_tools")
    if requested_tools is not None:
        if not isinstance(requested_tools, list):
            return _schema_diagnostic(
                artifact, "RequestedAuth.json field $.requested_tools must be a list"
            )
        for index, tool in enumerate(requested_tools):
            path = f"$.requested_tools[{index}]"
            if not isinstance(tool, dict):
                return _schema_diagnostic(
                    artifact, f"RequestedAuth.json field {path} must be an object"
                )
            if not isinstance(tool.get("tool_name"), str):
                return _schema_diagnostic(
                    artifact,
                    f"RequestedAuth.json field {path}.tool_name must be a string",
                )

    return {"ok": True, "diagnostic": None}


def validate_approval_requests_schema(
    approval_requests_path: str | Path,
) -> dict[str, Any]:
    artifact = "ApprovalRequests.json"
    approval_requests = _load_json(approval_requests_path)

    if not isinstance(approval_requests, dict):
        return _schema_diagnostic(
            artifact, "ApprovalRequests.json root $ must be an object"
        )

    if not isinstance(approval_requests.get("schema_version"), str):
        return _schema_diagnostic(
            artifact, "ApprovalRequests.json field $.schema_version must be a string"
        )

    if "workflow_revision_id" in approval_requests and not isinstance(
        approval_requests["workflow_revision_id"], str
    ):
        return _schema_diagnostic(
            artifact,
            "ApprovalRequests.json field $.workflow_revision_id must be a string",
        )

    requests = approval_requests.get("requests")
    if not isinstance(requests, list):
        return _schema_diagnostic(
            artifact, "ApprovalRequests.json field $.requests must be a list"
        )

    for index, request in enumerate(requests):
        path = f"$.requests[{index}]"
        if not isinstance(request, dict):
            return _schema_diagnostic(
                artifact, f"ApprovalRequests.json field {path} must be an object"
            )
        for field_name in ("request_id", "node_id", "approval_subject_hash"):
            if not isinstance(request.get(field_name), str):
                return _schema_diagnostic(
                    artifact,
                    f"ApprovalRequests.json field {path}.{field_name} "
                    "must be a string",
                )
        # reason is informational; required to be a string only when present.
        if "reason" in request and not isinstance(request["reason"], str):
            return _schema_diagnostic(
                artifact, f"ApprovalRequests.json field {path}.reason must be a string"
            )

    return {"ok": True, "diagnostic": None}


def validate_approval_decisions_schema(
    approval_decisions_path: str | Path,
) -> dict[str, Any]:
    artifact = "ApprovalDecisions.json"
    approval_decisions = _load_json(approval_decisions_path)

    if not isinstance(approval_decisions, dict):
        return _schema_diagnostic(
            artifact, "ApprovalDecisions.json root $ must be an object"
        )

    if not isinstance(approval_decisions.get("schema_version"), str):
        return _schema_diagnostic(
            artifact, "ApprovalDecisions.json field $.schema_version must be a string"
        )

    if "workflow_revision_id" in approval_decisions and not isinstance(
        approval_decisions["workflow_revision_id"], str
    ):
        return _schema_diagnostic(
            artifact,
            "ApprovalDecisions.json field $.workflow_revision_id must be a string",
        )

    decisions = approval_decisions.get("decisions")
    if not isinstance(decisions, list):
        return _schema_diagnostic(
            artifact, "ApprovalDecisions.json field $.decisions must be a list"
        )

    for index, decision in enumerate(decisions):
        path = f"$.decisions[{index}]"
        if not isinstance(decision, dict):
            return _schema_diagnostic(
                artifact, f"ApprovalDecisions.json field {path} must be an object"
            )

        # Fields present in current fixtures must be strings.
        for field_name in ("request_id", "decision"):
            if not isinstance(decision.get(field_name), str):
                return _schema_diagnostic(
                    artifact,
                    f"ApprovalDecisions.json field {path}.{field_name} "
                    "must be a string",
                )

        # Optional fields must be strings only when present. node_id and
        # approval_subject_hash are not in current fixtures but are validated
        # when supplied. No enum constraint is placed on decision values, since
        # the resolver only distinguishes "approved" from anything else.
        for field_name in (
            "node_id",
            "approval_subject_hash",
            "approved_by",
            "approved_at",
            "reason",
            "comment",
        ):
            if field_name in decision and not isinstance(decision[field_name], str):
                return _schema_diagnostic(
                    artifact,
                    f"ApprovalDecisions.json field {path}.{field_name} "
                    "must be a string",
                )

    return {"ok": True, "diagnostic": None}


def validate_unknown_node_types(
    workflow_spec_path: str | Path, node_type_registry_path: str | Path
) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)
    node_type_registry = _load_json(node_type_registry_path)

    allowed_node_types = {
        node_type_entry["node_type"]
        for node_type_entry in node_type_registry.get("node_types", [])
        if "node_type" in node_type_entry
    }

    unknown_node_types = sorted(
        {
            node["node_type"]
            for node in workflow_spec.get("nodes", [])
            if node.get("node_type") not in allowed_node_types
        }
    )

    if not unknown_node_types:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNKNOWN_NODE_TYPE",
            "component": "graph_validator",
            "artifact": "WorkflowSpec.json",
            "message": f"unknown node type: {', '.join(unknown_node_types)}",
        },
    }


# This is not a final MCP schema. It is a V1 fail-closed guard that rejects
# node-level tool/connector/broker/MCP execution intent until broker-mediated
# execution is designed and implemented.
_UNSUPPORTED_EXECUTION_BINDING_KEYS = frozenset(
    {
        "tool_binding",
        "tool_access",
        "connector_binding",
        "connector_access",
        "broker_binding",
        "mcp",
        "mcp_binding",
        "mcp_server",
        "mcp_tool",
        "mcp_resource",
        "mcp_prompt",
        "mcp_transport",
        "mcp_method",
    }
)

_UNSUPPORTED_CAPABILITY_ENVELOPE_KEYS = frozenset(
    {
        "capability_envelope",
        "capability_envelopes",
        "compiled_capability_envelope",
        "compiled_capability_envelopes",
        "authority_envelope",
        "authority_envelopes",
        "runtime_capabilities",
        "approved_capabilities",
    }
)

_UNSUPPORTED_SECRET_FIELD_KEYS = frozenset(
    {
        "token",
        "tokens",
        "secret",
        "secrets",
        "password",
        "passwords",
        "api_key",
        "api_keys",
        "private_key",
        "private_keys",
        "credential",
        "credentials",
    }
)

_UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM_KEYS = frozenset(
    {
        "safeguard_approved",
        "safeguard_approval",
        "safeguard_authorized",
        "safeguard_authorization",
        "approved_by_safeguard",
        "authorized_by_safeguard",
        "execution_allowed",
        "grant_capability",
        "grant_capabilities",
        "unblock_execution",
        "approval_decision",
        "approval_override",
        "authority_override",
    }
)

_UNSUPPORTED_AUTHORITY_ARTIFACT_KEYS = frozenset(
    {
        "compiled_execution_plan",
        "compiled_execution_plans",
        "compiled_authority_manifest",
        "compiled_authority_manifests",
        "authority_manifest",
        "authority_manifests",
        "compiler_diagnostics",
        "validation_diagnostics",
        "execution_manifest",
        "execution_result",
        "runtime_result",
        "audit_log",
        "verifier_output",
        "evidence_lineage",
        "approval_decisions",
    }
)

# V1 fail-closed guard: planner-controlled artifacts must not be able to claim
# reusable approval, standing approval, approval carryover, approval tokens, or
# approval-binding authority. Approvals remain explicit, operator-owned,
# current-run/request scoped, and not reusable ambient authority. This is
# exact-key rejection only; it does not implement approval binding, approval
# carryover, authority subsumption, or any approval resolution behavior.
_UNSUPPORTED_APPROVAL_BINDING_KEYS = frozenset(
    {
        "approval_binding",
        "approval_bindings",
        "approval_token",
        "approval_tokens",
        "approval_carryover",
        "reusable_approval",
        "reusable_approvals",
        "standing_approval",
        "standing_approvals",
    }
)

# V1 fail-closed guard: planner-controlled artifacts must not declare future
# evidence/verifier/broker/sandbox reporting artifacts or authority. Those are
# documented as future reporting-only / inert-example concepts (see
# EVIDENCE_LINEAGE_VERIFIER_OUTPUT_CONTRACT.md and
# NOOP_BROKER_BOUNDARY_CONTRACT.md); they are not planner-authoritative and are
# not V1 control-plane inputs. This is exact-key rejection only.
#
# Note: ``evidence_lineage`` and ``verifier_output`` are already owned by the
# authority-artifact-ownership validator (_UNSUPPORTED_AUTHORITY_ARTIFACT_KEYS)
# and remain rejected fail-closed there; they are intentionally not duplicated
# here to keep validator ownership and diagnostic ordering unambiguous.
_UNSUPPORTED_RUNTIME_REPORTING_CLAIM_KEYS = frozenset(
    {
        "verifier_result",
        "broker_request",
        "broker_decision",
        "broker_result",
        "broker_boundary",
        "sandbox_attestation",
        "sandbox_status",
        "runtime_authority",
        "broker_authority",
        "verifier_authority",
        "evidence_authority",
    }
)

# V1 fail-closed guard: planner-controlled artifacts must not claim that audit
# logs, evidence references/records, or audit/verifier/evidence observations can
# approve, authorize, grant, satisfy, or override compiler/operator authority.
# Audit and evidence are reporting material only; they are never an approval or
# authority source in a planner-controlled proposal. This is exact-key rejection
# only.
#
# Ownership note: this validator owns only the "audit/evidence can
# approve/authorize/grant/override/satisfy authority" claim family. Adjacent
# keys are intentionally NOT duplicated here:
#   - ``evidence_authority`` is owned by the runtime-reporting-boundary validator
#     (_UNSUPPORTED_RUNTIME_REPORTING_CLAIM_KEYS).
#   - ``evidence_lineage``, ``verifier_output``, ``audit_log``, and
#     ``approval_decisions`` are owned by the authority-artifact-ownership
#     validator (_UNSUPPORTED_AUTHORITY_ARTIFACT_KEYS).
#   - ``approval_decision``, ``approval_override``, ``authority_override`` are
#     owned by the safeguard-authority-claim validator.
_UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM_KEYS = frozenset(
    {
        "audit_authority",
        "audit_approval",
        "audit_grant",
        "audit_override",
        "audit_decision",
        "audit_authorizes",
        "audit_approved_by",
        "audit_satisfies_approval",
        "audit_satisfies_authority",
        "audit_override_diagnostics",
        "evidence_approval",
        "evidence_grant",
        "evidence_override",
        "evidence_decision",
        "evidence_authorizes",
        "evidence_approved_by",
        "evidence_satisfies_approval",
        "evidence_satisfies_authority",
        "evidence_override_diagnostics",
    }
)

# V1 fail-closed guard: planner-controlled artifacts must not claim that operator
# approval is reusable, persistent, global, inherited, cross-run, cross-request,
# or otherwise valid outside the current run/request. Operator approval remains
# explicit, operator-owned, and current-run/request scoped (see
# APPROVAL_BINDING_CONTRACT.md and
# V1_SAFE_NOOP_GOVERNANCE_COCKPIT_CHECKPOINT.md). This is exact-key rejection
# only; it implements no reusable approval, approval carryover, authority
# subsumption, or real approval binding, and it changes no approval
# resolution/matching behavior.
#
# Ownership note: this validator owns only the approval scope/carryover/reuse/
# persistence/cross-run claim family. ``approval_carryover`` and
# ``reusable_approval`` (and ``standing_approval``/``standing_approvals``) are
# already owned by the approval-binding validator
# (_UNSUPPORTED_APPROVAL_BINDING_KEYS) and are intentionally not duplicated here.
_UNSUPPORTED_APPROVAL_SCOPE_CLAIM_KEYS = frozenset(
    {
        "approval_reuse",
        "persistent_approval",
        "global_approval",
        "cross_run_approval",
        "prior_run_approval",
        "inherited_approval",
        "approval_inheritance",
        "approval_subsumption",
        "approval_valid_for_future_runs",
        "approval_valid_across_requests",
        "approval_valid_across_runs",
        "approval_expires_never",
        "approval_scope_override",
        "request_scope_override",
        "run_scope_override",
    }
)

# V1 fail-closed guard: planner-controlled artifacts must not supply or redefine
# approval/run/request identity, proof, token, receipt, signature, or subject
# identifiers that could later be mistaken for operator approval binding
# authority. Operator approval identity is operator-owned and lives only in the
# operator-authored ApprovalDecisions.json; planner-controlled artifacts must not
# spoof, supply, or override it. This is exact-key rejection only; it implements
# no real approval binding, reusable approval, approval carryover, or authority
# subsumption, and it changes no approval resolution/matching behavior.
#
# Ownership note: this validator owns only planner-supplied approval
# identity/proof/token/receipt/signature/subject/run/request identifier claims.
# ``approval_token`` (and ``approval_tokens``) are already owned by the
# approval-binding validator (_UNSUPPORTED_APPROVAL_BINDING_KEYS) and are
# intentionally not duplicated here. The legitimate schema fields ``request_id``,
# ``approval_subject_hash``, and ``workflow_revision_id`` are distinct from these
# claim keys and remain accepted.
_UNSUPPORTED_APPROVAL_IDENTITY_CLAIM_KEYS = frozenset(
    {
        "approval_id",
        "approval_decision_id",
        "approval_proof",
        "approval_receipt",
        "approval_certificate",
        "approval_signature",
        "operator_signature",
        "approved_by_operator",
        "operator_approved",
        "approval_subject_override",
        "approval_subject_identity",
        "approval_subject_ref",
        "approval_subject_digest_override",
        "approval_run_id",
        "approval_request_id",
        "approval_scope_id",
        "run_approval_id",
        "request_approval_id",
    }
)


def _find_unsupported_execution_binding_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_EXECUTION_BINDING_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_execution_binding_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_execution_binding_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def _find_unsupported_capability_envelope_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_CAPABILITY_ENVELOPE_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_capability_envelope_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_capability_envelope_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def _find_unsupported_secret_field_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_SECRET_FIELD_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_secret_field_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_secret_field_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def _find_unsupported_safeguard_authority_claim_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_safeguard_authority_claim_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_safeguard_authority_claim_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def _find_unsupported_authority_artifact_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_AUTHORITY_ARTIFACT_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_authority_artifact_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_authority_artifact_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def _find_unsupported_approval_binding_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_APPROVAL_BINDING_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_approval_binding_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_approval_binding_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def _find_unsupported_runtime_reporting_claim_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_RUNTIME_REPORTING_CLAIM_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_runtime_reporting_claim_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_runtime_reporting_claim_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def _find_unsupported_audit_evidence_authority_claim_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_audit_evidence_authority_claim_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_audit_evidence_authority_claim_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def _find_unsupported_approval_scope_claim_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_APPROVAL_SCOPE_CLAIM_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_approval_scope_claim_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_approval_scope_claim_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def _find_unsupported_approval_identity_claim_paths(
    value: Any,
    *,
    path: str,
) -> list[str]:
    findings: list[str] = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in _UNSUPPORTED_APPROVAL_IDENTITY_CLAIM_KEYS:
                findings.append(child_path)
            findings.extend(
                _find_unsupported_approval_identity_claim_paths(
                    child,
                    path=child_path,
                )
            )
        return findings

    if isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(
                _find_unsupported_approval_identity_claim_paths(
                    child,
                    path=f"{path}[{index}]",
                )
            )

    return findings


def validate_unsupported_capability_envelope_fields(
    artifact_path: str | Path,
    artifact_name: str,
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = _find_unsupported_capability_envelope_paths(artifact, path="$")

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_CAPABILITY_ENVELOPE",
            "component": "capability_envelope_validator",
            "artifact": artifact_name,
            "message": (
                f"unsupported capability/authority envelope field in {artifact_name}; "
                "V1 safe no-op does not accept planner-supplied capability envelopes, "
                "approved capabilities, or authority-envelope fields: "
                + ", ".join(findings)
            ),
        },
    }


def validate_unsupported_secret_fields(
    artifact_path: str | Path,
    artifact_name: str,
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = _find_unsupported_secret_field_paths(artifact, path="$")

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_SECRET_FIELD",
            "component": "secret_field_validator",
            "artifact": artifact_name,
            "message": (
                f"unsupported secret-bearing field in {artifact_name}; "
                "V1 safe no-op does not accept planner-supplied tokens, secrets, "
                "passwords, API keys, private keys, or credentials: "
                + ", ".join(findings)
            ),
        },
    }


def validate_unsupported_safeguard_authority_claims(
    artifact_path: str | Path,
    artifact_name: str,
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = _find_unsupported_safeguard_authority_claim_paths(
        artifact,
        path="$",
    )

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
            "component": "safeguard_authority_claim_validator",
            "artifact": artifact_name,
            "message": (
                f"unsupported safeguard authority claim in {artifact_name}; "
                "V1 safe no-op does not accept safeguard approval, authorization, "
                "execution-unblock, or authority-override claims: "
                + ", ".join(findings)
            ),
        },
    }


def validate_unsupported_authority_artifacts(
    artifact_path: str | Path,
    artifact_name: str,
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = _find_unsupported_authority_artifact_paths(
        artifact,
        path="$",
    )

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_AUTHORITY_ARTIFACT",
            "component": "authority_artifact_ownership_validator",
            "artifact": artifact_name,
            "message": (
                f"unsupported compiler/runtime/operator-owned authority artifact "
                f"field in {artifact_name}; V1 safe no-op does not accept "
                "planner-supplied compiled plans, authority manifests, "
                "diagnostics, execution results, audit artifacts, evidence "
                "lineage, or approval decisions: " + ", ".join(findings)
            ),
        },
    }


def validate_unsupported_approval_bindings(
    artifact_path: str | Path,
    artifact_name: str,
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = _find_unsupported_approval_binding_paths(
        artifact,
        path="$",
    )

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_APPROVAL_BINDING",
            "component": "approval_binding_validator",
            "artifact": artifact_name,
            "message": (
                f"unsupported approval-binding field in {artifact_name}; "
                "V1 safe no-op does not accept planner-supplied approval "
                "bindings, approval tokens, approval carryover, reusable "
                "approvals, or standing approvals; approvals remain explicit, "
                "operator-owned, and current-run/request scoped: "
                + ", ".join(findings)
            ),
        },
    }


def validate_unsupported_runtime_reporting_claims(
    artifact_path: str | Path,
    artifact_name: str,
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = _find_unsupported_runtime_reporting_claim_paths(
        artifact,
        path="$",
    )

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_RUNTIME_REPORTING_CLAIM",
            "component": "runtime_reporting_boundary_validator",
            "artifact": artifact_name,
            "message": (
                f"unsupported runtime-reporting/broker claim in {artifact_name}; "
                "evidence/verifier/broker/sandbox reporting and broker artifacts "
                "are not planner-authoritative and are not V1 control-plane "
                "inputs: " + ", ".join(findings)
            ),
        },
    }


def validate_unsupported_audit_evidence_authority_claims(
    artifact_path: str | Path,
    artifact_name: str,
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = _find_unsupported_audit_evidence_authority_claim_paths(
        artifact,
        path="$",
    )

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
            "component": "audit_evidence_authority_validator",
            "artifact": artifact_name,
            "message": (
                f"unsupported audit/evidence authority claim in {artifact_name}; "
                "audit and evidence records are reporting material only and "
                "cannot approve, authorize, grant capabilities, override "
                "diagnostics, satisfy approval, or create authority in "
                "planner-controlled artifacts: " + ", ".join(findings)
            ),
        },
    }


def validate_unsupported_approval_scope_claims(
    artifact_path: str | Path,
    artifact_name: str,
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = _find_unsupported_approval_scope_claim_paths(
        artifact,
        path="$",
    )

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_APPROVAL_SCOPE_CLAIM",
            "component": "approval_scope_validator",
            "artifact": artifact_name,
            "message": (
                f"unsupported approval-scope claim in {artifact_name}; operator "
                "approval is explicit, operator-owned, and current-run/request "
                "scoped, and planner-controlled artifacts must not claim "
                "reusable, persistent, global, inherited, or cross-run/cross-"
                "request approval: " + ", ".join(findings)
            ),
        },
    }


def validate_unsupported_approval_identity_claims(
    artifact_path: str | Path,
    artifact_name: str,
) -> dict[str, Any]:
    artifact = _load_json(artifact_path)
    findings = _find_unsupported_approval_identity_claim_paths(
        artifact,
        path="$",
    )

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM",
            "component": "approval_identity_validator",
            "artifact": artifact_name,
            "message": (
                f"unsupported approval-identity claim in {artifact_name}; "
                "operator approval identity, proof, receipt, signature, and "
                "subject/run/request identifiers are operator-owned and must not "
                "be supplied, spoofed, or overridden by planner-controlled "
                "artifacts: " + ", ".join(findings)
            ),
        },
    }


def validate_unsupported_execution_bindings(
    workflow_spec_path: str | Path,
) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)

    findings: list[str] = []
    for index, node in enumerate(workflow_spec.get("nodes", [])):
        if not isinstance(node, dict):
            continue

        node_id = node.get("node_id")
        node_label = node_id if isinstance(node_id, str) else f"nodes[{index}]"
        node_findings = _find_unsupported_execution_binding_paths(
            node,
            path=f"$.nodes[{index}]",
        )
        findings.extend(
            f"{node_label}:{binding_path}" for binding_path in node_findings
        )

    if not findings:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "UNSUPPORTED_EXECUTION_BINDING",
            "component": "execution_binding_validator",
            "artifact": "WorkflowSpec.json",
            "message": (
                "unsupported execution/tool/MCP binding in WorkflowSpec.json; "
                "V1 safe no-op does not support tool, connector, broker, or "
                "MCP execution bindings: " + ", ".join(findings)
            ),
        },
    }


def validate_missing_required_scope(requested_auth_path: str | Path) -> dict[str, Any]:
    requested_auth = _load_json(requested_auth_path)

    connectors_missing_scope = sorted(
        {
            connector.get("connector_name", "<unknown>")
            for connector in requested_auth.get("requested_connectors", [])
            if not isinstance(connector.get("scope"), str) or not connector["scope"].strip()
        }
    )

    if not connectors_missing_scope:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "MISSING_REQUIRED_SCOPE",
            "component": "scope_validator",
            "artifact": "RequestedAuth.json",
            "message": (
                "missing required scope for connector: "
                + ", ".join(connectors_missing_scope)
            ),
        },
    }


def validate_illegal_graph_cycle(workflow_spec_path: str | Path) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)

    node_ids = {node.get("node_id") for node in workflow_spec.get("nodes", []) if "node_id" in node}
    adjacency: dict[str, list[str]] = defaultdict(list)
    indegree: dict[str, int] = {node_id: 0 for node_id in node_ids}

    for edge in workflow_spec.get("edges", []):
        from_node_id = edge.get("from_node_id")
        to_node_id = edge.get("to_node_id")
        if from_node_id is None or to_node_id is None:
            continue

        if from_node_id not in indegree:
            indegree[from_node_id] = 0
        if to_node_id not in indegree:
            indegree[to_node_id] = 0

        adjacency[from_node_id].append(to_node_id)
        indegree[to_node_id] += 1

    ready = deque(sorted(node_id for node_id, count in indegree.items() if count == 0))
    visited_count = 0

    while ready:
        node_id = ready.popleft()
        visited_count += 1

        for next_node_id in sorted(adjacency.get(node_id, [])):
            indegree[next_node_id] -= 1
            if indegree[next_node_id] == 0:
                ready.append(next_node_id)

    if visited_count == len(indegree):
        return {
            "ok": True,
            "diagnostic": None,
        }

    cyclic_nodes = sorted(node_id for node_id, count in indegree.items() if count > 0)
    return {
        "ok": False,
        "diagnostic": {
            "error_code": "ILLEGAL_GRAPH_CYCLE",
            "component": "graph_validator",
            "artifact": "WorkflowSpec.json",
            "message": f"cycle detected in workflow graph: {', '.join(cyclic_nodes)}",
        },
    }


def validate_disconnected_graph(workflow_spec_path: str | Path) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)

    node_ids = sorted(
        node.get("node_id")
        for node in workflow_spec.get("nodes", [])
        if "node_id" in node
    )

    if len(node_ids) <= 1:
        return {
            "ok": True,
            "diagnostic": None,
        }

    adjacency: dict[str, list[str]] = defaultdict(list)
    declared_node_ids = set(node_ids)

    for edge in workflow_spec.get("edges", []):
        from_node_id = edge.get("from_node_id")
        to_node_id = edge.get("to_node_id")
        if from_node_id not in declared_node_ids or to_node_id not in declared_node_ids:
            continue

        adjacency[from_node_id].append(to_node_id)
        adjacency[to_node_id].append(from_node_id)

    reachable: set[str] = set()
    queue = deque([node_ids[0]])

    while queue:
        node_id = queue.popleft()
        if node_id in reachable:
            continue

        reachable.add(node_id)
        for next_node_id in sorted(adjacency.get(node_id, [])):
            if next_node_id not in reachable:
                queue.append(next_node_id)

    disconnected_nodes = sorted(node_id for node_id in node_ids if node_id not in reachable)
    if not disconnected_nodes:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "DISCONNECTED_GRAPH",
            "component": "graph_validator",
            "artifact": "WorkflowSpec.json",
            "message": (
                "disconnected graph contains unreachable nodes: "
                + ", ".join(disconnected_nodes)
            ),
        },
    }


def validate_invalid_edge_endpoints(workflow_spec_path: str | Path) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)

    declared_node_ids = {
        node.get("node_id")
        for node in workflow_spec.get("nodes", [])
        if "node_id" in node
    }
    invalid_endpoints: list[str] = []

    for edge in workflow_spec.get("edges", []):
        from_node_id = edge.get("from_node_id")
        to_node_id = edge.get("to_node_id")

        if from_node_id not in declared_node_ids:
            invalid_endpoints.append(f"from:{from_node_id}")
        if to_node_id not in declared_node_ids:
            invalid_endpoints.append(f"to:{to_node_id}")

    if not invalid_endpoints:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "INVALID_EDGE_ENDPOINT",
            "component": "graph_validator",
            "artifact": "WorkflowSpec.json",
            "message": (
                "invalid edge endpoint in workflow graph: "
                + ", ".join(sorted(invalid_endpoints))
            ),
        },
    }


def validate_invalid_fan_out(
    workflow_spec_path: str | Path, node_type_registry_path: str | Path
) -> dict[str, Any]:
    workflow_spec = _load_json(workflow_spec_path)
    node_type_registry = _load_json(node_type_registry_path)

    node_id_to_type = {
        node["node_id"]: node["node_type"]
        for node in workflow_spec.get("nodes", [])
        if "node_id" in node and "node_type" in node
    }
    node_type_to_max_outgoing = {
        entry["node_type"]: entry["max_outgoing_edges"]
        for entry in node_type_registry.get("node_types", [])
        if "node_type" in entry and "max_outgoing_edges" in entry
    }
    outgoing_counts: dict[str, int] = defaultdict(int)

    for edge in workflow_spec.get("edges", []):
        from_node_id = edge.get("from_node_id")
        if from_node_id in node_id_to_type:
            outgoing_counts[from_node_id] += 1

    invalid_fan_out_nodes: list[str] = []
    for node_id, node_type in sorted(node_id_to_type.items()):
        max_outgoing_edges = node_type_to_max_outgoing.get(node_type)
        if max_outgoing_edges is None:
            continue

        outgoing_count = outgoing_counts.get(node_id, 0)
        if outgoing_count > max_outgoing_edges:
            invalid_fan_out_nodes.append(
                f"{node_id}({node_type})={outgoing_count}>{max_outgoing_edges}"
            )

    if not invalid_fan_out_nodes:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "INVALID_FAN_OUT",
            "component": "graph_validator",
            "artifact": "WorkflowSpec.json",
            "message": (
                "invalid fan-out in workflow graph: "
                + ", ".join(invalid_fan_out_nodes)
            ),
        },
    }


def validate_ambiguous_approval_subjects(approval_requests_path: str | Path) -> dict[str, Any]:
    approval_requests = _load_json(approval_requests_path)

    seen_request_ids: set[str] = set()
    seen_node_ids: set[str] = set()
    seen_approval_subject_hashes: set[str] = set()
    ambiguous_details: list[str] = []

    for request in approval_requests.get("requests", []):
        request_id = request.get("request_id")
        node_id = request.get("node_id")
        approval_subject_hash = request.get("approval_subject_hash")

        if request_id in seen_request_ids:
            ambiguous_details.append(f"duplicate request_id:{request_id}")
        elif request_id is not None:
            seen_request_ids.add(request_id)

        if node_id in seen_node_ids:
            ambiguous_details.append(f"duplicate node_id:{node_id}")
        elif node_id is not None:
            seen_node_ids.add(node_id)

        if approval_subject_hash in seen_approval_subject_hashes:
            ambiguous_details.append(
                f"duplicate approval_subject_hash:{approval_subject_hash}"
            )
        elif approval_subject_hash is not None:
            seen_approval_subject_hashes.add(approval_subject_hash)

    if not ambiguous_details:
        return {
            "ok": True,
            "diagnostic": None,
        }

    return {
        "ok": False,
        "diagnostic": {
            "error_code": "AMBIGUOUS_APPROVAL_SUBJECT",
            "component": "approval_validator",
            "artifact": "ApprovalRequests.json",
            "message": "ambiguous approval subject: " + "; ".join(sorted(set(ambiguous_details))),
        },
    }


def validate_static_inputs(
    workflow_spec_path: str | Path,
    node_type_registry_path: str | Path,
    requested_auth_path: str | Path,
    approval_requests_path: str | Path,
    *,
    approval_decisions_path: str | Path | None = None,
    stop_on_first_error: bool = True,
) -> dict[str, Any]:
    # Validation is phased. A phase that produces any diagnostic returns before
    # the next phase runs, even when aggregate diagnostics are requested
    # (stop_on_first_error=False). This prevents later phases from interpreting
    # input that an earlier phase already found unsafe or malformed.
    #
    # Phase 1: authority-value validators (do not interpret bad authority values)
    # Phase 2: schema validators (graph validators must not see malformed shapes)
    # Phase 3: interpretation validators (graph, scope, approval semantics).
    # Ordering within the phase is deterministic and fail-closed:
    # secret-field, capability-envelope, safeguard-authority-claim,
    # authority-artifact-ownership, approval-binding, execution-binding,
    # runtime-reporting-boundary, audit-evidence-authority, approval-scope,
    # approval-identity, then graph/scope/approval.

    # Phase 1: authority-value validators.
    phase_authority_values = [
        lambda: validate_authority_values(workflow_spec_path, "WorkflowSpec.json"),
        lambda: validate_authority_values(
            node_type_registry_path, "NodeTypeRegistry.json"
        ),
        lambda: validate_authority_values(requested_auth_path, "RequestedAuth.json"),
        lambda: validate_authority_values(
            approval_requests_path, "ApprovalRequests.json"
        ),
    ]
    if approval_decisions_path is not None:
        phase_authority_values.append(
            lambda: validate_authority_values(
                approval_decisions_path, "ApprovalDecisions.json"
            )
        )

    # Phase 2: schema validators.
    phase_schema = [
        lambda: validate_workflow_spec_schema(workflow_spec_path),
        lambda: validate_node_type_registry_schema(node_type_registry_path),
        lambda: validate_requested_auth_schema(requested_auth_path),
        lambda: validate_approval_requests_schema(approval_requests_path),
    ]
    if approval_decisions_path is not None:
        phase_schema.append(
            lambda: validate_approval_decisions_schema(approval_decisions_path)
        )

    # Phase 3: interpretation validators.
    phase_interpretation = [
        lambda: validate_unsupported_secret_fields(
            workflow_spec_path, "WorkflowSpec.json"
        ),
        lambda: validate_unsupported_secret_fields(
            requested_auth_path, "RequestedAuth.json"
        ),
        lambda: validate_unsupported_secret_fields(
            approval_requests_path, "ApprovalRequests.json"
        ),
        lambda: validate_unsupported_capability_envelope_fields(
            workflow_spec_path, "WorkflowSpec.json"
        ),
        lambda: validate_unsupported_capability_envelope_fields(
            requested_auth_path, "RequestedAuth.json"
        ),
        lambda: validate_unsupported_capability_envelope_fields(
            approval_requests_path, "ApprovalRequests.json"
        ),
        lambda: validate_unsupported_safeguard_authority_claims(
            workflow_spec_path, "WorkflowSpec.json"
        ),
        lambda: validate_unsupported_safeguard_authority_claims(
            requested_auth_path, "RequestedAuth.json"
        ),
        lambda: validate_unsupported_safeguard_authority_claims(
            approval_requests_path, "ApprovalRequests.json"
        ),
        lambda: validate_unsupported_authority_artifacts(
            workflow_spec_path, "WorkflowSpec.json"
        ),
        lambda: validate_unsupported_authority_artifacts(
            requested_auth_path, "RequestedAuth.json"
        ),
        lambda: validate_unsupported_authority_artifacts(
            approval_requests_path, "ApprovalRequests.json"
        ),
        lambda: validate_unsupported_approval_bindings(
            workflow_spec_path, "WorkflowSpec.json"
        ),
        lambda: validate_unsupported_approval_bindings(
            requested_auth_path, "RequestedAuth.json"
        ),
        lambda: validate_unsupported_approval_bindings(
            approval_requests_path, "ApprovalRequests.json"
        ),
        lambda: validate_unsupported_execution_bindings(workflow_spec_path),
        lambda: validate_unsupported_runtime_reporting_claims(
            workflow_spec_path, "WorkflowSpec.json"
        ),
        lambda: validate_unsupported_runtime_reporting_claims(
            requested_auth_path, "RequestedAuth.json"
        ),
        lambda: validate_unsupported_runtime_reporting_claims(
            approval_requests_path, "ApprovalRequests.json"
        ),
        lambda: validate_unsupported_audit_evidence_authority_claims(
            workflow_spec_path, "WorkflowSpec.json"
        ),
        lambda: validate_unsupported_audit_evidence_authority_claims(
            requested_auth_path, "RequestedAuth.json"
        ),
        lambda: validate_unsupported_audit_evidence_authority_claims(
            approval_requests_path, "ApprovalRequests.json"
        ),
        lambda: validate_unsupported_approval_scope_claims(
            workflow_spec_path, "WorkflowSpec.json"
        ),
        lambda: validate_unsupported_approval_scope_claims(
            requested_auth_path, "RequestedAuth.json"
        ),
        lambda: validate_unsupported_approval_scope_claims(
            approval_requests_path, "ApprovalRequests.json"
        ),
        lambda: validate_unsupported_approval_identity_claims(
            workflow_spec_path, "WorkflowSpec.json"
        ),
        lambda: validate_unsupported_approval_identity_claims(
            requested_auth_path, "RequestedAuth.json"
        ),
        lambda: validate_unsupported_approval_identity_claims(
            approval_requests_path, "ApprovalRequests.json"
        ),
        lambda: validate_unknown_node_types(
            workflow_spec_path, node_type_registry_path
        ),
        lambda: validate_invalid_edge_endpoints(workflow_spec_path),
        lambda: validate_illegal_graph_cycle(workflow_spec_path),
        lambda: validate_disconnected_graph(workflow_spec_path),
        lambda: validate_invalid_fan_out(
            workflow_spec_path, node_type_registry_path
        ),
        lambda: validate_missing_required_scope(requested_auth_path),
        lambda: validate_ambiguous_approval_subjects(approval_requests_path),
    ]

    for phase in (phase_authority_values, phase_schema, phase_interpretation):
        diagnostics: list[dict[str, Any]] = []
        for validator in phase:
            result = validator()
            if result["ok"]:
                continue

            diagnostics.append(result["diagnostic"])
            if stop_on_first_error:
                return {
                    "ok": False,
                    "diagnostics": diagnostics,
                }

        # Gate the next phase: if this phase produced any diagnostics, stop here
        # rather than letting a later phase interpret already-rejected input.
        if diagnostics:
            return {
                "ok": False,
                "diagnostics": diagnostics,
            }

    return {
        "ok": True,
        "diagnostics": [],
    }
