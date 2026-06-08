# Capability Envelope V1 Design

**Status: design only. Not implemented.**

This document is a V1 boundary checkpoint for future compiled capability
envelopes. It does not implement capability envelopes, execution, tools,
connectors, MCP/network access, broker/sandbox behavior, LLM planning, or real
side effects.

## Trust Boundary

- Planner may request capabilities, but cannot authorize them.
- Compiler is the only future authority boundary that may produce compiled
  capability envelopes.
- Runtime/broker may eventually execute only against compiler-approved
  envelopes.
- V1 currently does not execute envelopes.
- V1 currently does not grant capabilities.
- V1 currently does not call tools, connectors, or MCP.

## Required Properties

- Capability envelopes must be node-scoped.
- Capability envelopes must include explicit run scope and explicit node scope.
- Capability envelopes must be approval-bound when applicable.
- Capability envelopes must be auditable.
- Capability envelopes must be immutable once compiled.
- Capability envelopes must not contain credentials.

## V1 Guardrail

V1 safe no-op does not generate capability envelopes, does not consume
capability envelopes, and does not render capability envelopes in CLI summary
output.

Planner-controlled artifacts must not smuggle authority through fields such as
`capability_envelope`, `compiled_capability_envelopes`,
`authority_envelopes`, `runtime_capabilities`, `approved_capabilities`,
`credential`, or `credentials`. When present in planner-controlled artifacts,
V1 should reject them fail-closed with `UNSUPPORTED_CAPABILITY_ENVELOPE`
instead of treating them as meaningful input.

## Future Enforcement Boundary

Any future execution against capability envelopes must be broker/sandbox
mediated and compiler-approved. Future broker/sandbox enforcement is out of scope for this slice.

## Non-Goals

This document does not enable:

- execution
- tool support
- connector support
- MCP support
- compiler-generated capability envelopes
- runtime capability-envelope consumption
- broker/sandbox implementation
