# Compiler Authorization Summary Design

This is a design-only checkpoint for a future compiler-owned authorization
summary. It is not implemented. V1 safe no-op does not generate or consume this
summary yet.

## Ownership

- The authorization summary is compiler-owned.
- Planner must not supply it.
- It is derived only from compiler-validated candidate artifacts.
- Future broker or sandbox components may eventually consume only
  compiler-owned authorization artifacts, never planner-supplied ones.

## Purpose

The future summary may describe:

- requested authority
- blocked authority
- approval-required authority
- unsupported authority

This summary is informational and compiler-owned. It does not grant runtime
execution by itself.

## Boundaries

- It does not contain credentials or secrets.
- It does not replace `ApprovalDecisions.json`.
- It does not enable approval carryover.
- It is scoped to the current run, current request, and current artifact
  revision only.
- It does not make planner output authoritative.

## Future Consumption Boundary

- Future broker or sandbox behavior may eventually consume compiler-owned
  authorization artifacts only.
- Planner-supplied authorization artifacts must never be treated as runtime
  authority.
- Runtime execution must remain gated by compiler-owned authority artifacts and
  explicit approval where applicable.

## V1 Non-Goals

- no runtime execution
- no broker
- no connector, MCP, or tool calls
- no model inference
- no CLI rendering
- no planner behavior changes
- no compiler behavior changes in V1 safe no-op
