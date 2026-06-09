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

## V1 Non-Goals

This document does not implement:

- approval carryover
- authority subsumption
- broker execution
- MCP/tool calls
- model inference
- credential/secret handling
