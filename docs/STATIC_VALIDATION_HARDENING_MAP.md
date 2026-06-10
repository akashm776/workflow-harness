# Static Validation Hardening Map

This is a docs-only map of the current `validate_static_inputs(...)` hardening
layers. It records current validator ownership, diagnostic order, and the rules
for adding future validators. It changes no behavior and is not a public API.

The exact Phase 3 order and per-diagnostic ownership boundaries are pinned as a
contract in
[`STATIC_VALIDATION_ORDERING_CONTRACT.md`](STATIC_VALIDATION_ORDERING_CONTRACT.md).

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
5. approval-binding validator
6. execution-binding validator
7. runtime-reporting-boundary validator
8. audit-evidence-authority validator
9. approval-scope validator
10. approval-identity validator
11. graph/scope/approval validators
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
- `UNSUPPORTED_APPROVAL_BINDING`: planner-supplied approval-binding, approval
  token, approval carryover, reusable-approval, or standing-approval exact key
  names. Exact-key rejection only; it does not implement approval binding,
  approval carryover, authority subsumption, or any approval resolution
  behavior.
- `UNSUPPORTED_EXECUTION_BINDING`: tool, connector, MCP, or broker execution
  binding claims.
- `UNSUPPORTED_RUNTIME_REPORTING_CLAIM`: planner-supplied future
  evidence/verifier/broker/sandbox reporting or authority claims
  (`verifier_result`, `broker_request`, `broker_decision`, `broker_result`,
  `broker_boundary`, `sandbox_attestation`, `sandbox_status`,
  `runtime_authority`, `broker_authority`, `verifier_authority`,
  `evidence_authority`). Exact-key rejection only. `evidence_lineage` and
  `verifier_output` remain owned by `UNSUPPORTED_AUTHORITY_ARTIFACT` and are not
  duplicated here. This validator adds no broker, sandbox, verifier, or evidence
  behavior.
- `UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM`: planner-supplied claims that
  audit/evidence records can approve, authorize, grant, satisfy, or override
  authority (`audit_authority`, `audit_approval`, `audit_grant`,
  `audit_override`, `audit_decision`, `audit_authorizes`, `audit_approved_by`,
  `audit_satisfies_approval`, `audit_satisfies_authority`,
  `audit_override_diagnostics`, `evidence_approval`, `evidence_grant`,
  `evidence_override`, `evidence_decision`, `evidence_authorizes`,
  `evidence_approved_by`, `evidence_satisfies_approval`,
  `evidence_satisfies_authority`, `evidence_override_diagnostics`). Exact-key
  rejection only. It owns only the "audit/evidence can approve/authorize/grant/
  override/satisfy authority" claim family; `evidence_authority` stays owned by
  `UNSUPPORTED_RUNTIME_REPORTING_CLAIM` and `evidence_lineage`/`verifier_output`/
  `audit_log` stay owned by `UNSUPPORTED_AUTHORITY_ARTIFACT`. It adds no audit,
  evidence, or verifier behavior.
- `UNSUPPORTED_APPROVAL_SCOPE_CLAIM`: planner-supplied claims that operator
  approval is reusable, persistent, global, inherited, or valid across
  runs/requests (`approval_reuse`, `persistent_approval`, `global_approval`,
  `cross_run_approval`, `prior_run_approval`, `inherited_approval`,
  `approval_inheritance`, `approval_subsumption`,
  `approval_valid_for_future_runs`, `approval_valid_across_requests`,
  `approval_valid_across_runs`, `approval_expires_never`,
  `approval_scope_override`, `request_scope_override`, `run_scope_override`).
  Exact-key rejection only. `approval_carryover` and `reusable_approval` (and
  `standing_approval`/`standing_approvals`) stay owned by
  `UNSUPPORTED_APPROVAL_BINDING`. It implements no reusable approval, approval
  carryover, authority subsumption, or real approval binding, and changes no
  approval resolution/matching behavior.
- `UNSUPPORTED_APPROVAL_IDENTITY_CLAIM`: planner-supplied approval/run/request
  identity, proof, receipt, signature, or subject identifier claims
  (`approval_id`, `approval_decision_id`, `approval_proof`, `approval_receipt`,
  `approval_certificate`, `approval_signature`, `operator_signature`,
  `approved_by_operator`, `operator_approved`, `approval_subject_override`,
  `approval_subject_identity`, `approval_subject_ref`,
  `approval_subject_digest_override`, `approval_run_id`, `approval_request_id`,
  `approval_scope_id`, `run_approval_id`, `request_approval_id`). Exact-key
  rejection only. `approval_token` (and `approval_tokens`) stay owned by
  `UNSUPPORTED_APPROVAL_BINDING`; the legitimate schema fields `request_id`,
  `approval_subject_hash`, and `workflow_revision_id` remain accepted. It
  implements no real approval binding and changes no approval
  resolution/matching behavior.

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
