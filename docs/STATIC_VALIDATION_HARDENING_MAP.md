# Static Validation Hardening Map

This is a docs-only map of the current `validate_static_inputs(...)` hardening
layers. It records current validator ownership, diagnostic order, and the rules
for adding future validators. It changes no behavior and is not a public API.

## Validation Phases

### Phase 1: authority-value validation

- Rejects invalid authority-bearing values before semantic interpretation.
- Current diagnostic ownership includes `DISALLOWED_AUTHORITY_VALUE`.

### Phase 2: schema validation

- Rejects malformed control-plane artifacts before graph, scope, or approval
  interpretation.
- Current diagnostic ownership includes `INVALID_ARTIFACT_SCHEMA`.

### Phase 3: interpretation validation

Current Phase 3 order:

```text
1. secret-field validator
2. capability-envelope validator
3. safeguard-authority-claim validator
4. authority-artifact-ownership validator
5. execution-binding validator
6. graph/scope/approval validators
```

## Validator Ownership

- `UNSUPPORTED_SECRET_FIELD`: exact secret-like key names only. No arbitrary
  string scanning.
- `UNSUPPORTED_CAPABILITY_ENVELOPE`: planner-supplied
  capability-envelope/authority-envelope fields.
- `UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM`: safeguard approval,
  authorization, or execution-unblock claims.
- `UNSUPPORTED_AUTHORITY_ARTIFACT`: planner-supplied compiler-owned,
  runtime-owned, or operator-owned authority artifacts.
- `UNSUPPORTED_EXECUTION_BINDING`: tool, connector, MCP, or broker execution
  binding claims.

## Rules For Adding Future Validators

- Prefer exact-key rejection for early hardening.
- Never grant authority.
- Never add execution in a validator.
- Never call tools, connectors, MCP, network, or models from validation.
- Do not scan arbitrary prose unless explicitly designed and tested.
- Place new validators according to ownership and diagnostic order.
- Update ordering tests when order changes.
- Keep validation deterministic and fail-closed.

## Explicit Non-Goals

- no real execution
- no connector/MCP/tool calls
- no model inference
- no broker/sandbox
- no approval carryover
- no authority subsumption
- no canonical JSON/hashing changes
