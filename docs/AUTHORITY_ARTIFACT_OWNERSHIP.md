# Authority Artifact Ownership

This document is design only. It is not implemented as an execution feature,
approval mechanism, or runtime authority path.

## Purpose

The harness needs an explicit ownership contract for authority-bearing artifacts.
Planner proposals may describe desired work, but they must not smuggle in
compiler-owned, runtime-owned, or operator-owned authority artifacts.

This checkpoint defines which layer owns which artifact family and what V1 safe
no-op must reject fail-closed.

## Ownership Boundary

### Planner-owned / planner-proposed

These artifacts are proposals only and remain non-authoritative:

- candidate `WorkflowSpec.json`
- candidate `RequestedAuth.json`
- candidate `ApprovalRequests.json`
- future planner proposal metadata

Planner artifacts may request authority, but they cannot grant authority.

### Compiler-owned

These artifacts are compiler authority outputs, not planner inputs:

- validation diagnostics
- future compiled capability envelopes
- future compiled execution plans
- future authority manifests
- future compiled approval subjects

The compiler is the authority boundary. Only deterministic compiler output may
eventually produce compiled authority artifacts.

### Runtime-owned

These artifacts report execution or verification state, but do not invent
authority:

- `ExecutionManifest`
- `ExecutionResult`
- audit/status artifacts
- future evidence lineage
- future verifier outputs

Runtime may report results, but it does not invent authority and it must not
upgrade planner proposals into authority.

### Operator-owned

These artifacts express explicit human review intent:

- explicit approval decisions
- current-run/request approval intent

Operator approval must remain explicit and current-run/request scoped.

## V1 Safe No-Op Boundary

V1 safe no-op does not execute real tools, connectors, or MCP calls.

V1 does not generate compiled capability envelopes yet.

V1 does not consume compiled capability envelopes yet.

V1 does not allow planner-supplied compiler-owned or runtime-owned authority artifacts.

V1 does not allow planner-supplied operator approval artifacts to become effective approval decisions.

Future broker enforcement, if added later, must depend only on compiler-approved
authority and explicit operator approval where required.

## Rejection Contract

Planner-controlled artifacts should be rejected fail-closed if they try to
embed compiler-owned, runtime-owned, or operator-owned authority artifact
fields.

Current rejection-only validator contract:

- diagnostic: `UNSUPPORTED_AUTHORITY_ARTIFACT`
- component: `authority_artifact_ownership_validator`

This validator is exact-key only. It does not scan arbitrary prose, does not
interpret benign text, does not create compiled artifacts, and does not enable
runtime consumption.

## Non-Goals

- no real execution
- no tools/connectors
- no MCP/network calls
- no sandbox/broker implementation
- no model inference
- no approval carryover
- no authority subsumption
- no planner-generated authority
- no runtime-generated authority
- no compiled capability envelope generation in V1
- no compiled capability envelope consumption in V1
