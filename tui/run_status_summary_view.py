"""Dependency-free text renderer for the read-only run summary.

Pure renderer: it does not mutate its input and performs no I/O. It only formats
the dict produced by ``runtime.run_status_summary.summarize_run_directory``.
"""

from __future__ import annotations

from typing import Any, Mapping


def _bool_text(value: Any) -> str:
    return "true" if value is True else "false"


def _field_text(value: Any) -> str:
    if value is None:
        return "unknown"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def render_run_status_summary_view(summary: Mapping[str, Any]) -> str:
    lines = [
        "Safe No-Op Run Summary",
        f"run_dir: {summary.get('run_dir', '')}",
        f"complete_safe_noop_run: {_bool_text(summary.get('complete_safe_noop_run'))}",
        f"compilation_status: {_field_text(summary.get('compilation_status'))}",
        f"execution_status: {_field_text(summary.get('execution_status'))}",
        f"review_required: {_field_text(summary.get('review_required'))}",
        f"blocked_by_review: {_bool_text(summary.get('blocked_by_review'))}",
        f"candidate_dir_present: {_bool_text(summary.get('candidate_dir_present'))}",
        "",
    ]

    artifacts = summary.get("artifacts", {})
    if isinstance(artifacts, Mapping):
        for artifact_name, artifact_status in artifacts.items():
            exists = False
            if isinstance(artifact_status, Mapping):
                exists = artifact_status.get("exists") is True
            marker = "[x]" if exists else "[ ]"
            lines.append(f"{marker} {artifact_name}")

    review_gate_lines = _review_gate_lines(
        summary.get("review_gate"),
        summary.get("approval_request_count"),
    )
    if review_gate_lines:
        lines.append("")
        lines.extend(review_gate_lines)

    candidate_lines = _candidate_workflow_lines(summary.get("candidate_workflow"))
    if candidate_lines:
        lines.append("")
        lines.extend(candidate_lines)

    fixture_lineage_lines = _fixture_lineage_lines(summary.get("fixture_lineage"))
    if fixture_lineage_lines:
        lines.append("")
        lines.extend(fixture_lineage_lines)

    proposed_tool_access_lines = _proposed_tool_access_lines(
        summary.get("proposed_tool_access")
    )
    if proposed_tool_access_lines:
        lines.append("")
        lines.extend(proposed_tool_access_lines)

    compiler_authorization_projection_lines = _compiler_authorization_projection_lines(
        summary.get("compiler_authorization_projection")
    )
    if compiler_authorization_projection_lines:
        lines.append("")
        lines.extend(compiler_authorization_projection_lines)

    approval_binding_summary_lines = _approval_binding_summary_lines(
        summary.get("approval_binding_summary")
    )
    if approval_binding_summary_lines:
        lines.append("")
        lines.extend(approval_binding_summary_lines)

    verifier_evidence_status_lines = _verifier_evidence_status_lines(
        summary.get("verifier_evidence_status")
    )
    if verifier_evidence_status_lines:
        lines.append("")
        lines.extend(verifier_evidence_status_lines)

    broker_boundary_status_lines = _broker_boundary_status_lines(
        summary.get("broker_boundary_status")
    )
    if broker_boundary_status_lines:
        lines.append("")
        lines.extend(broker_boundary_status_lines)

    operator_review_packet_lines = _operator_review_packet_lines(
        summary.get("operator_review_packet")
    )
    if operator_review_packet_lines:
        lines.append("")
        lines.extend(operator_review_packet_lines)

    status_command = summary.get("status_command")
    if status_command:
        lines.append("")
        lines.append(f"status command: {status_command}")

    return "\n".join(lines)


def _review_gate_lines(review_gate: Any, approval_request_count: Any) -> list[str]:
    if not isinstance(review_gate, Mapping):
        return []

    lines = ["Review Gate:"]

    blocked_reason = review_gate.get("blocked_reason")
    if blocked_reason is not None:
        lines.append(f"blocked_reason: {blocked_reason}")

    if isinstance(approval_request_count, int):
        lines.append(f"approval_request_count: {approval_request_count}")

    request_id = review_gate.get("request_id")
    if isinstance(request_id, str):
        lines.append(f"approval_request_id: {request_id}")

    node_id = review_gate.get("node_id")
    if isinstance(node_id, str):
        lines.append(f"node_id: {node_id}")

    reason = review_gate.get("reason")
    if isinstance(reason, str):
        lines.append(f"reason: {reason}")

    approval_requests_path = review_gate.get("approval_requests_path")
    if isinstance(approval_requests_path, str):
        lines.append(f"approval request artifact: {approval_requests_path}")

    lines.append(
        "unblock: supply a matching ApprovalDecisions.json for this run/request only"
    )
    return lines


def _candidate_workflow_lines(candidate_workflow: Any) -> list[str]:
    if not isinstance(candidate_workflow, Mapping):
        return []
    nodes = candidate_workflow.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return []

    edges = candidate_workflow.get("edges")
    outgoing: dict[str, list[str]] = {}
    if isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, Mapping):
                continue
            from_node_id = edge.get("from_node_id")
            to_node_id = edge.get("to_node_id")
            if isinstance(from_node_id, str) and isinstance(to_node_id, str):
                outgoing.setdefault(from_node_id, []).append(to_node_id)

    lines = ["Candidate Workflow:"]
    for node in nodes:
        if not isinstance(node, Mapping):
            continue
        node_id = node.get("node_id")
        node_type = node.get("node_type")
        if not isinstance(node_id, str) or not isinstance(node_type, str):
            continue
        display_name = node.get("display_name")
        suffix = f" {display_name}" if isinstance(display_name, str) else ""
        lines.append(f"- {node_id} [{node_type}]{suffix}")
        for to_node_id in outgoing.get(node_id, []):
            lines.append(f"  -> {to_node_id}")
    return lines


def _fixture_lineage_lines(fixture_lineage: Any) -> list[str]:
    if not isinstance(fixture_lineage, Mapping):
        return []

    lines = ["Fixture Lineage:"]
    lines.append(f"display_only: {_bool_text(fixture_lineage.get('display_only'))}")
    lines.append(f"not_loaded: {_bool_text(fixture_lineage.get('not_loaded'))}")
    lines.append(
        "not_control_plane_inputs: "
        f"{_bool_text(fixture_lineage.get('not_control_plane_inputs'))}"
    )

    paths = fixture_lineage.get("paths")
    if isinstance(paths, list):
        for path in paths:
            if isinstance(path, str):
                lines.append(f"- {path}")
    return lines


def _proposed_tool_access_lines(proposed_tool_access: Any) -> list[str]:
    if not isinstance(proposed_tool_access, Mapping):
        return []

    lines = ["Proposed Tool Access:"]
    lines.append(
        f"display_only: {_bool_text(proposed_tool_access.get('display_only'))}"
    )
    lines.append(
        f"proposal_only: {_bool_text(proposed_tool_access.get('proposal_only'))}"
    )
    lines.append(
        f"no_execution: {_bool_text(proposed_tool_access.get('no_execution'))}"
    )
    lines.append(
        "no_connector_support: "
        f"{_bool_text(proposed_tool_access.get('no_connector_support'))}"
    )

    tools = proposed_tool_access.get("tools")
    if isinstance(tools, list):
        for tool in tools:
            if not isinstance(tool, Mapping):
                continue
            tool_name = tool.get("tool_name")
            if not isinstance(tool_name, str):
                continue
            access_mode = tool.get("access_mode")
            suffix = f" access_mode={access_mode}" if isinstance(access_mode, str) else ""
            lines.append(f"- tool: {tool_name}{suffix}")

    connectors = proposed_tool_access.get("connectors")
    if isinstance(connectors, list):
        for connector in connectors:
            if not isinstance(connector, Mapping):
                continue
            connector_name = connector.get("connector_name")
            if not isinstance(connector_name, str):
                continue
            scope = connector.get("scope")
            suffix = f" scope={scope}" if isinstance(scope, str) else ""
            lines.append(f"- connector proposal: {connector_name}{suffix}")

    return lines


def _operator_review_packet_lines(operator_review_packet: Any) -> list[str]:
    if not isinstance(operator_review_packet, Mapping):
        return []

    lines = ["Operator Review Packet:"]
    lines.append(
        f"review_required: {_bool_text(operator_review_packet.get('review_required'))}"
    )
    lines.append(
        f"blocked_by_review: {_bool_text(operator_review_packet.get('blocked_by_review'))}"
    )

    decision_scope = operator_review_packet.get("decision_scope")
    if isinstance(decision_scope, str):
        lines.append(f"decision_scope: {decision_scope}")

    execution_mode = operator_review_packet.get("execution_mode")
    if isinstance(execution_mode, str):
        lines.append(f"execution_mode: {execution_mode}")

    lines.append("included_sections:")
    included_sections = operator_review_packet.get("included_sections")
    if isinstance(included_sections, list):
        for section_name in included_sections:
            if isinstance(section_name, str):
                lines.append(f"- {section_name}")

    return lines


def _compiler_authorization_projection_lines(
    compiler_authorization_projection: Any,
) -> list[str]:
    if not isinstance(compiler_authorization_projection, Mapping):
        return []

    lines = ["Compiler Authorization Projection:"]
    lines.append(
        "display_only: "
        f"{_bool_text(compiler_authorization_projection.get('display_only'))}"
    )
    lines.append(
        "compiler_owned_summary: "
        f"{_bool_text(compiler_authorization_projection.get('compiler_owned_summary'))}"
    )
    lines.append(
        "not_executable: "
        f"{_bool_text(compiler_authorization_projection.get('not_executable'))}"
    )
    lines.append(
        "not_persisted_as_artifact: "
        f"{_bool_text(compiler_authorization_projection.get('not_persisted_as_artifact'))}"
    )
    lines.append(
        "no_runtime_authority: "
        f"{_bool_text(compiler_authorization_projection.get('no_runtime_authority'))}"
    )
    lines.append(
        "current_run_scope_only: "
        f"{_bool_text(compiler_authorization_projection.get('current_run_scope_only'))}"
    )

    for field_name in (
        "requested_authority",
        "approval_required",
        "blocked_authority",
        "unsupported_authority",
    ):
        lines.append(f"{field_name}:")
        values = compiler_authorization_projection.get(field_name)
        if isinstance(values, list) and values:
            for value in values:
                if isinstance(value, str):
                    lines.append(f"- {value}")
        else:
            lines.append("- []")

    return lines


def _approval_binding_summary_lines(approval_binding_summary: Any) -> list[str]:
    if not isinstance(approval_binding_summary, Mapping):
        return []

    lines = ["Approval Binding Summary:"]
    for flag_name in (
        "display_only",
        "operator_owned",
        "not_reusable_authority",
        "no_approval_carryover",
        "no_runtime_authority",
        "current_run_scope_only",
        "current_request_scope_only",
    ):
        lines.append(
            f"{flag_name}: {_bool_text(approval_binding_summary.get(flag_name))}"
        )

    lines.append("approval_subjects:")
    approval_subjects = approval_binding_summary.get("approval_subjects")
    if isinstance(approval_subjects, list) and approval_subjects:
        for subject in approval_subjects:
            if not isinstance(subject, Mapping):
                continue
            lines.append(
                f"- request_id: {_field_text(subject.get('request_id'))}"
            )
            lines.append(f"  node_id: {_field_text(subject.get('node_id'))}")
            lines.append(
                "  approval_subject_hash: "
                f"{_field_text(subject.get('approval_subject_hash'))}"
            )
            lines.append(
                "  binds_to_current_request: "
                f"{_field_text(subject.get('binds_to_current_request'))}"
            )
            lines.append(
                "  binds_to_candidate_artifact: "
                f"{_field_text(subject.get('binds_to_candidate_artifact'))}"
            )
            lines.append(
                "  binds_to_requested_authority: "
                f"{_field_text(subject.get('binds_to_requested_authority'))}"
            )
    else:
        lines.append("- []")

    lines.append("unsupported_binding_claims:")
    unsupported_binding_claims = approval_binding_summary.get(
        "unsupported_binding_claims"
    )
    if isinstance(unsupported_binding_claims, list) and unsupported_binding_claims:
        for claim in unsupported_binding_claims:
            if isinstance(claim, str):
                lines.append(f"- {claim}")
    else:
        lines.append("- []")

    return lines


def _verifier_evidence_status_lines(verifier_evidence_status: Any) -> list[str]:
    if not isinstance(verifier_evidence_status, Mapping):
        return []

    lines = ["Verifier / Evidence Status:"]
    for flag_name in (
        "display_only",
        "reporting_only",
        "not_authority",
        "not_verifier_output_artifact",
        "not_evidence_lineage_artifact",
        "no_runtime_authority",
        "no_execution",
        "no_approval",
        "current_run_scope_only",
    ):
        lines.append(
            f"{flag_name}: {_bool_text(verifier_evidence_status.get(flag_name))}"
        )

    for field_name in (
        "manifest_status",
        "execution_result_status",
        "audit_log_status",
        "produced_evidence_count",
        "side_effect_count",
        "verification_status",
    ):
        lines.append(
            f"{field_name}: {_field_text(verifier_evidence_status.get(field_name))}"
        )

    lines.append("findings:")
    findings = verifier_evidence_status.get("findings")
    if isinstance(findings, list) and findings:
        for finding in findings:
            if isinstance(finding, str):
                lines.append(f"- {finding}")
    else:
        lines.append("- []")

    return lines


def _broker_boundary_status_lines(broker_boundary_status: Any) -> list[str]:
    if not isinstance(broker_boundary_status, Mapping):
        return []

    lines = ["Broker Boundary Status:"]
    for flag_name in (
        "display_only",
        "reporting_only",
        "not_authority",
        "not_broker_request_artifact",
        "not_broker_decision_artifact",
        "not_broker_result_artifact",
        "no_broker_implementation",
        "no_sandbox_implementation",
        "no_runtime_authority",
        "no_execution",
        "no_approval",
        "current_run_scope_only",
    ):
        lines.append(
            f"{flag_name}: {_bool_text(broker_boundary_status.get(flag_name))}"
        )

    for field_name in (
        "broker_request_status",
        "broker_decision_status",
        "broker_result_status",
        "sandbox_status",
        "execution_status",
    ):
        lines.append(
            f"{field_name}: {_field_text(broker_boundary_status.get(field_name))}"
        )

    lines.append("findings:")
    findings = broker_boundary_status.get("findings")
    if isinstance(findings, list) and findings:
        for finding in findings:
            if isinstance(finding, str):
                lines.append(f"- {finding}")
    else:
        lines.append("- []")

    return lines
