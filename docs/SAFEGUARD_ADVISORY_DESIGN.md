# Safeguard Advisory Design

**Status: design only. Not implemented.**

This document prepares for future safeguard advisory review in
`workflow-harness`. It does not run any model, does not call any API, does not
download any model, and does not enable execution, tools, connectors,
MCP/network access, or broker/sandbox behavior.

## Trust Boundary

- Safeguard model output is advisory only.
- Safeguard output is not authority.
- Safeguard output cannot approve.
- Safeguard output cannot grant capabilities.
- Safeguard output cannot unblock execution.
- Safeguard output cannot change approval semantics.
- Deterministic compiler remains the authority boundary.
- Operator/human approval remains explicit.
- Future runtime/broker enforcement must depend only on compiler-approved
  authority, not safeguard output.

## V1 Status

- V1 does not call any safeguard model.
- V1 does not download any model.
- V1 does not use OpenAI API, Ollama, vLLM, LM Studio, Transformers, MCP,
  network, or local inference for safeguard review.

## Future Advisory Role

Future safeguard review may warn, block/escalate, or add review findings, but
may never approve, authorize, grant capabilities, or execute anything.

Only concise rationale and policy rule IDs should be stored in future outputs.
Do not depend on hidden chain-of-thought.

## V1 Guardrail

Planner-controlled artifacts and future advisory artifacts must not claim
approval or authority through fields such as `safeguard_approved`,
`approved_by_safeguard`, `execution_allowed`, `grant_capabilities`,
`unblock_execution`, `approval_override`, or `authority_override`.

When such keys appear, V1 should reject them fail-closed with
`UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM`.

## Non-Goals

This document does not enable:

- model inference
- OpenAI API integration
- Ollama integration
- vLLM integration
- LM Studio integration
- Transformers integration
- safeguard-based approval
- safeguard-based capability grants
- safeguard-based execution unblocking
