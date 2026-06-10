# Static Validation Ordering Contract

This is current contract documentation for compiler static validation ordering.
It records the mature Phase 3 hardening order and ownership boundaries so future
slices do not accidentally reorder validators, duplicate diagnostic ownership,
scan `ApprovalDecisions.json` with planner-input validators, treat future
evidence/verifier/broker/sandbox concepts as authority, or weaken fail-closed
behavior.

## Status / Scope

- Current contract documentation for compiler static validation ordering.
- Docs/tests only.
- No behavior change.
- No canonical JSON/hashing change.
- No runtime/execution change.

## Phase 3 Order

```text
1. secret-field
2. capability-envelope
3. safeguard-authority-claim
4. authority-artifact-ownership
5. approval-binding
6. execution-binding
7. runtime-reporting-boundary
8. audit-evidence-authority
9. graph/scope/approval
```

## Ownership Boundaries

- `UNSUPPORTED_SECRET_FIELD` owns unsupported secret material fields.
- `UNSUPPORTED_CAPABILITY_ENVELOPE` owns unsupported future capability envelope
  fields.
- `UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM` owns planner claims that
  safeguards/approvals can override authority.
- `UNSUPPORTED_AUTHORITY_ARTIFACT` owns unsupported authority artifacts such as
  `evidence_lineage`, `verifier_output`, `audit_log`, `approval_decisions`.
- `UNSUPPORTED_APPROVAL_BINDING` owns unsupported approval-binding fields.
- `UNSUPPORTED_EXECUTION_BINDING` owns unsupported execution-binding fields.
- `UNSUPPORTED_RUNTIME_REPORTING_CLAIM` owns unsupported runtime-reporting/broker/
  sandbox claim fields such as `broker_request`, `broker_decision`,
  `broker_result`, `runtime_authority`, `evidence_authority`.
- `UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM` owns unsupported audit/evidence
  approve/authorize/grant/override/satisfy-authority claim fields.
- graph/scope/approval validators own structural graph/scope/approval
  consistency.

Each diagnostic owns its key family exclusively; future slices must not
duplicate a key already owned by another validator.

## Scanner Scope

- Planner-input hardening validators scan planner-controlled artifacts only:
  - `WorkflowSpec.json`
  - `RequestedAuth.json`
  - `ApprovalRequests.json`
- They must not scan `ApprovalDecisions.json` unless a validator is explicitly
  designed for operator decisions.
- Operator approval decisions are not planner-authored proposals.

## Matching Rule

- Unsupported claim validators reject exact object keys.
- They must not fuzzy-match arbitrary string values.
- Benign strings are not rejected merely because they contain a reserved term.

## Fail-Closed Guarantees

- Unsupported planner claims fail closed.
- Planner remains non-authoritative.
- Compiler remains the authority boundary.
- Operator approval remains explicit and current-run/request scoped.
- Runtime remains safe no-op.
- Diagnostics do not grant authority.
- Audit/evidence/verifier/broker/sandbox concepts do not approve, authorize,
  grant capabilities, override diagnostics, override operator approval, enable
  carryover, enable authority subsumption, or create reusable authority.

## Non-Goals

- no real execution
- no broker/sandbox
- no fake/no-op broker interface
- no MCP/tool/connector calls
- no model inference
- no verifier implementation
- no evidence generation implementation
- no approval carryover/reusable approvals/authority subsumption
- no canonical JSON/hashing changes
