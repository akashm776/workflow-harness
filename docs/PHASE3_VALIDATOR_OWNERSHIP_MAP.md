# Phase 3 Validator Ownership Map

This is a consolidation map of the current compiler **Phase 3** (interpretation)
static validation stack. It records, per validator family, the purpose,
diagnostic code, component name, artifacts scanned, artifacts deliberately not
scanned, ownership exclusions, and what the validator must not imply.

It exists so future slices do not reorder validators, duplicate diagnostic
ownership, scan operator-owned artifacts with planner-input validators, or let a
fail-closed guard be mistaken for a grant.

## Status / Scope

- Consolidation documentation for the current Phase 3 validator stack.
- Docs/tests only.
- No behavior change.
- No new validator.
- No canonical JSON/hashing change.
- No runtime/execution change.

## What These Validators Are

The Phase 3 unsupported-claim validators are **fail-closed governance guards**.
They reject planner-controlled artifacts that attempt to assert capabilities,
authority, approvals, identity, or execution rights the V1 safe no-op governance
plane does not grant.

These validators **do not create** authority, approvals, evidence, execution
rights, or runtime capability. Rejecting a claim is the only thing they do; they
never approve, authorize, grant, satisfy, override, or enable anything.

## Product Framing (Preserved)

- The planner is **non-authoritative**; its artifacts are proposals only.
- The compiler is the **sole authority boundary**.
- Operator approval is **explicit and current-run/request scoped**.
- Runtime, broker, and verifier **cannot create authority**.
- No real execution, broker, sandbox, verifier, evidence generation, approval
  carryover, reusable approval, authority subsumption, or real approval binding
  is implemented in this scope.

## Matching Rule

- Unsupported-claim validators reject **exact object keys**.
- They do not fuzzy-match arbitrary string values.
- A benign string is not rejected merely because it contains a reserved term.

## Planner-Input Scanner Scope

The unsupported-claim validators scan **planner-controlled artifacts only**:

```text
WorkflowSpec.json
RequestedAuth.json
ApprovalRequests.json
```

They must **not** scan `ApprovalDecisions.json`. Operator approval decisions are
operator-authored, not planner proposals; a validator may scan them only if it
is explicitly designed for operator decisions.

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
9. approval-scope
10. approval-identity
11. graph/scope/approval
```

Each diagnostic owns its key family exclusively. Future slices must not
duplicate a key already owned by another validator.

## Validator Families

### 1. secret-field

- **Purpose:** reject planner-supplied secret material fields.
- **Diagnostic:** `UNSUPPORTED_SECRET_FIELD`
- **Component:** `secret_field_validator`
- **Scans:** planner-controlled artifacts.
- **Must not imply:** that secrets/credentials may be supplied, stored, or used.
  It adds no credential storage and does not scan arbitrary string values.

### 2. capability-envelope

- **Purpose:** reject planner-supplied future capability-envelope /
  authority-envelope / approved-capability fields.
- **Diagnostic:** `UNSUPPORTED_CAPABILITY_ENVELOPE`
- **Component:** `capability_envelope_validator`
- **Scans:** planner-controlled artifacts.
- **Must not imply:** that the planner may author or authorize capability
  envelopes. Only the compiler may ever produce compiled envelopes.

### 3. safeguard-authority-claim

- **Purpose:** reject planner claims that safeguards/approvals can approve,
  authorize, unblock execution, or override authority.
- **Diagnostic:** `UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM`
- **Component:** `safeguard_authority_claim_validator`
- **Scans:** planner-controlled artifacts.
- **Must not imply:** that safeguard output is authority. Safeguard output is
  advisory only and runs no model in this scope.

### 4. authority-artifact-ownership

- **Purpose:** reject planner-supplied compiler-owned / runtime-owned /
  operator-owned authority artifacts.
- **Diagnostic:** `UNSUPPORTED_AUTHORITY_ARTIFACT`
- **Component:** `authority_artifact_ownership_validator`
- **Owns:** unsupported authority artifacts such as `evidence_lineage`,
  `verifier_output`, `audit_log`, `approval_decisions`.
- **Scans:** planner-controlled artifacts.
- **Must not imply:** that compiled plans/manifests, runtime results, audit or
  evidence artifacts, or approval-decision artifacts may originate from the
  planner.

### 5. approval-binding

- **Purpose:** reject planner-supplied approval-binding fields.
- **Diagnostic:** `UNSUPPORTED_APPROVAL_BINDING`
- **Component:** `approval_binding_validator`
- **Owns (exclusively, not duplicated elsewhere):** `approval_carryover`,
  `reusable_approval`, `standing_approval`, `standing_approvals`,
  `approval_token`, `approval_tokens`.
- **Scans:** planner-controlled artifacts.
- **Must not imply:** any real approval binding, reusable approval, or approval
  carryover. It is rejection only.

### 6. execution-binding

- **Purpose:** reject planner-supplied execution-binding fields.
- **Diagnostic:** `UNSUPPORTED_EXECUTION_BINDING`
- **Component:** `execution_binding_validator`
- **Scans:** planner-controlled artifacts.
- **Must not imply:** that any execution path, broker, or sandbox exists.

### 7. runtime-reporting-boundary

- **Purpose:** reject planner claims of runtime/broker/sandbox reporting
  authority.
- **Diagnostic:** `UNSUPPORTED_RUNTIME_REPORTING_CLAIM`
- **Component:** `runtime_reporting_boundary_validator`
- **Owns:** fields such as `broker_request`, `broker_decision`, `broker_result`,
  `runtime_authority`, `evidence_authority`.
- **Scans:** planner-controlled artifacts.
- **Must not imply:** that runtime/broker/verifier output can create authority.

### 8. audit-evidence-authority

- **Purpose:** reject planner claims that audit/evidence records can approve,
  authorize, grant, satisfy, or override authority.
- **Diagnostic:** `UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM`
- **Component:** `audit_evidence_authority_validator`
- **Ownership exclusion:** `evidence_authority` stays owned by
  `UNSUPPORTED_RUNTIME_REPORTING_CLAIM`.
- **Scans:** planner-controlled artifacts.
- **Must not imply:** that audit/evidence generation exists or grants authority.

### 9. approval-scope

- **Purpose:** reject planner-controlled claims that operator approval is
  reusable, persistent, global, inherited, cross-run, or cross-request.
- **Diagnostic:** `UNSUPPORTED_APPROVAL_SCOPE_CLAIM`
- **Component:** `approval_scope_validator`
- **Scans only:**
  - `WorkflowSpec.json`
  - `RequestedAuth.json`
  - `ApprovalRequests.json`
- **Does not scan:**
  - `ApprovalDecisions.json`
- **Rejects planner-controlled claims that approval is:**
  - reusable
  - persistent
  - global
  - inherited
  - cross-run
  - cross-request
- **Ownership exclusion:** `approval_carryover`, `reusable_approval`,
  `standing_approval`, and `standing_approvals` remain owned by
  `UNSUPPORTED_APPROVAL_BINDING`.
- **Must not imply:** that approval can ever be reused or extended beyond the
  current run/request. It changes no approval resolution/matching behavior.

### 10. approval-identity

- **Purpose:** reject planner-controlled attempts to supply or spoof approval
  identity.
- **Diagnostic:** `UNSUPPORTED_APPROVAL_IDENTITY_CLAIM`
- **Component:** `approval_identity_validator`
- **Scans only:**
  - `WorkflowSpec.json`
  - `RequestedAuth.json`
  - `ApprovalRequests.json`
- **Does not scan:**
  - `ApprovalDecisions.json`
- **Rejects planner-controlled attempts to supply or spoof:**
  - approval identity
  - approval proof
  - approval receipt
  - approval signature
  - approval subject
  - approval run identifiers
  - approval request identifiers
- **Ownership exclusion:** `approval_token` and `approval_tokens` remain owned by
  `UNSUPPORTED_APPROVAL_BINDING`.
- **Legitimate schema fields must remain valid:**
  - `request_id`
  - `approval_subject_hash`
  - `workflow_revision_id`
- **Must not imply:** that planner-supplied identity can stand in for
  operator-owned approval identity. Operator approval identity lives only in the
  operator-authored `ApprovalDecisions.json`. It implements no real approval
  binding and changes no approval resolution/matching behavior.

### 11. graph/scope/approval

- **Purpose:** structural graph/scope/approval consistency.
- **Components:** `graph_validator`, `scope_validator`, `approval_validator`.
- **Representative diagnostics:** `UNKNOWN_NODE_TYPE`, `ILLEGAL_GRAPH_CYCLE`,
  `DISCONNECTED_GRAPH`, `INVALID_EDGE_ENDPOINT`, `INVALID_FAN_OUT`,
  `MISSING_REQUIRED_SCOPE`, `AMBIGUOUS_APPROVAL_SUBJECT`.
- **Must not imply:** any execution or granted authority; these enforce
  structural consistency only.

## Fail-Closed Guarantees

- Unsupported planner claims fail closed.
- Diagnostics do not grant authority.
- Audit/evidence/verifier/broker/sandbox concepts do not approve, authorize,
  grant capabilities, override diagnostics, override operator approval, enable
  carryover, enable authority subsumption, or create reusable authority.

## Related Docs

- [`STATIC_VALIDATION_ORDERING_CONTRACT.md`](STATIC_VALIDATION_ORDERING_CONTRACT.md)
  — the ordering and scanner-scope contract this map elaborates.
- [`STATIC_VALIDATION_HARDENING_MAP.md`](STATIC_VALIDATION_HARDENING_MAP.md)
  — the phase-level hardening map.
- [`POST_TAG_APPROVAL_HARDENING_LINE.md`](POST_TAG_APPROVAL_HARDENING_LINE.md)
  — the post-tag checkpoint that added the approval-scope and approval-identity
  invariants.
