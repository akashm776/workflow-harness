# Compiler Authorization Summary Projection

This is a design-only checkpoint for how a future compiler-owned authorization
summary would be projected from existing compiler-validated artifacts. It is
not implemented. V1 safe no-op does not generate or consume this projection
yet.

## Inputs

Future projection inputs are limited to:

- compiler-validated `RequestedAuth.json`
- compiler-validated `ApprovalRequests.json`
- static validation diagnostics
- current run, request, and artifact revision context

## Projected Output Sections

The future projection may contain:

- `requested_authority`
- `approval_required`
- `blocked_authority`
- `unsupported_authority`

## Mapping Rules

- `requested_authority` is derived from validated requested scopes or
  capabilities only.
- `approval_required` is derived from explicit approval requests only.
- `blocked_authority` is derived from missing approvals, unapproved approval
  requirements, or policy rejection.
- `unsupported_authority` is derived from static validation diagnostics such
  as:
  - `UNSUPPORTED_SECRET_FIELD`
  - `UNSUPPORTED_CAPABILITY_ENVELOPE`
  - `UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM`
  - `UNSUPPORTED_AUTHORITY_ARTIFACT`
  - `UNSUPPORTED_EXECUTION_BINDING`
- Projection is deterministic.

## Boundaries

- Projection does not grant authority.
- Projection does not execute.
- Projection does not call tools, connectors, MCP, network, or models.
- Projection does not read secrets.
- Projection does not replace `ApprovalDecisions.json`.
- Projection does not enable approval carryover.
- Projection is scoped to the current run, current request, and current
  artifact revision only.

## V1 Non-Goals

- no compiler generation yet
- no runtime consumption
- no planner behavior changes
- no CLI rendering
- no execution
- no tool, connector, MCP, or network behavior
- no model inference
