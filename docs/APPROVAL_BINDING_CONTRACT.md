# Approval Binding Contract

This is design/contract documentation only unless otherwise stated. It
describes how operator approvals are intended to bind to a request for future
compiler and runtime work. It is not an implementation. V1 safe no-op does not
use approvals for real execution, and nothing in this document changes approval
resolution behavior.

## Status

- Design/contract documentation only unless otherwise stated.
- V1 safe no-op does not use approvals for real execution.
- Planner remains non-authoritative.
- Compiler remains the sole authority boundary.
- Runtime remains safe no-op in V1.

## Ownership and Form

- Approvals are operator-owned.
- Approvals are explicit.
- Approvals are current-run scoped.
- Approvals are current-request scoped.

## Binding Rules

- Approvals bind to the approval subject.
- Approvals should bind to candidate artifact revision/digest where available.
- Approvals should bind to requested authority shape where available.

## Authority Boundaries

- Approvals do not grant authority outside the current request.
- Approvals do not carry over across runs.
- Approvals are not reusable ambient authority.
- Approvals do not authorize planner-supplied compiled artifacts.
- Approvals do not authorize runtime/broker behavior unless future
  compiler-owned authority artifacts also allow it.
- Future broker/sandbox execution must require compiler-owned authority plus
  explicit approval where required.

## Implemented Guard (Exact-Key Rejection)

One narrow fail-closed guard from this contract is now implemented. The
compiler static validator (`compiler/static_validation.py`,
`approval_binding_validator`) rejects planner-controlled
`WorkflowSpec.json`, `RequestedAuth.json`, and `ApprovalRequests.json`
artifacts that carry approval-binding or reusable-approval claims, emitting the
`UNSUPPORTED_APPROVAL_BINDING` diagnostic. It rejects these exact object keys
wherever they appear: `approval_binding`, `approval_bindings`,
`approval_token`, `approval_tokens`, `approval_carryover`, `reusable_approval`,
`reusable_approvals`, `standing_approval`, and `standing_approvals`.

This guard is exact-key rejection only. It does not scan ordinary words inside
string values, does not implement approval binding, does not implement approval
carryover, does not implement authority subsumption, does not change approval
resolution, and does not authorize runtime/broker execution. V1 remains safe
no-op only.

## Display-Only Operator Summary

For blocked explicit `innovation_review` runs, `cli.run_status_cli --summary`
renders a display-only `Approval Binding Summary:` section (placed after
`Compiler Authorization Projection:` and before `Operator Review Packet:`). It
explains, for the current blocked request only, what an approval would bind to,
derived solely from already-read local run data (candidate workflow identity,
`candidate/ApprovalRequests.json` read fail-soft, and existing
`CompilationReport.json` diagnostics). It is display-only and operator-owned;
it changes no approval resolution or matching, implements no real approval
binding, approval carryover, or reusable approvals, writes no artifacts, and
grants no authority.

## V1 Non-Goals

This document does not implement:

- approval carryover
- authority subsumption
- broker execution
- MCP/tool calls
- model inference
- credential/secret handling
