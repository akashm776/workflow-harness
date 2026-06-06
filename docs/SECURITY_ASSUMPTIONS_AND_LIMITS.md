# Security Assumptions And Limits

This document records the security posture of the current implementation as a
**design clarification**. It does not describe planned behavior as if it were
present, and it does not introduce any runtime behavior. Its purpose is to make
the boundary between what the code enforces today and what the specification
aspires to enforce explicit, so that the gaps are reviewed rather than assumed
closed.

For the intended end-state design, see `A2A-DYNAMIC-WORKFLOW-SPEC.md`. For the
current operator surface, see `docs/V1_SAFE_NOOP_HARNESS.md`.

## Current Implementation Limits

These are properties of the code as it exists now, not aspirations.

- **No approval carryover.** Approvals do not carry forward across runs, node
  revisions, or recompilations. Each compile resolves approvals only from the
  approval decisions presented to that compile. The spec's
  `approval_subject_hash`-keyed carryover is not implemented.
- **No narrowed-authority reuse.** The compiler does not detect that a change is
  a pure narrowing of authority and does not reuse a prior approval on that
  basis. Any change that would require a fresh approval under the spec is treated
  as requiring a fresh decision; nothing is carried.
- **Approval decisions require an exact match.** A requested approval is
  considered approved only when an approval decision exists whose `node_id` and
  `approval_subject_hash` both match exactly (see
  `compiler/approval_resolution.py`). There is no fuzzy, partial, or
  subsumption-based matching. A changed subject hash invalidates the approval.
- **V1 has no real execution.** The execution path is a deterministic no-op. It
  writes an `ExecutionManifest.json` and a no-op `ExecutionResult.json` and
  performs no work product side effects.
- **V1 makes no tool or connector calls.** No tool is invoked and no connector is
  contacted. Permission vocabulary (`jira.read`, `bitbucket.write`,
  `shell.execute`, etc.) is compiled and recorded but never exercised against a
  live system.

## Ambient Credential Limitation

- **The V1 Python runtime cannot hard-prevent ambient credentials by itself.** A
  local in-process Python runtime can compare declared connector/env state
  against an allowlist, but it cannot stop library code from reading ambient
  credentials such as keychain entries, cloud instance metadata, an existing SSO
  session, or process-inherited tokens. Within a single process boundary this
  protection is **policy-by-convention, not enforcement.**
- **Hard ambient-auth enforcement requires isolation the runtime does not
  provide.** Actually preventing access to ambient credentials requires
  OS-level, container-level, process-level, and/or network-level isolation
  (for example a separate uid, a restricted container, a credential-free
  execution sandbox, or a network namespace). This is out of scope for V1 and is
  a prerequisite for trusting any future real-execution path.

## Canonical JSON Is Part Of The Trust Boundary

- **Canonical JSON is part of the trust boundary.** All revision identities,
  dependency digests, the `approval_subject_hash`, and every compiled-artifact
  hash depend on the canonical serialization in `compiler/canonical_json.py`. The
  canonicalization scheme (key ordering, number handling, string/unicode
  handling, separators) is therefore security relevant: a change to it silently
  changes every hash and revision id. Canonical JSON is implemented in
  `compiler/canonical_json.py` and must be treated as part of the trust boundary.
  The exact canonicalization contract should remain stable and documented before
  real authority reuse or external interoperability depends on it.
- **Numeric gap is now closed for validated authority-bearing artifacts.**
  Previously the canonical JSON contract carried an open risk that floats and
  non-finite values (`NaN`, `Infinity`, `-Infinity`) could enter
  authority-bearing artifacts and silently affect hashes, digests,
  `approval_subject_hash`, or runtime verification. That gap is now closed for
  validated authority-bearing artifacts: `compiler/authority_value_validator.py`
  rejects floats and non-finite values during compile, failing closed with a
  `DISALLOWED_AUTHORITY_VALUE` diagnostic, for both loaded input artifacts and
  compiler-emitted authority artifacts. This is a validation gate only;
  `compiler/canonical_json.py` is unchanged. Two broader cautions remain: the
  serializer is still **not** RFC 8785 / JCS compliant, and the canonical
  contract must still be held stable and documented before real authority reuse
  or external interoperability depends on it.

## Artifact Shape Validation

- **All five control-plane input artifacts now have shape validation.**
  `WorkflowSpec.json` is validated for its required top-level fields and node/edge
  primitive shape, `NodeTypeRegistry.json` for its required fields and node-type
  entry shape, `RequestedAuth.json` for its required fields and connector/tool
  entry shape, `ApprovalRequests.json` for its required fields and request entry
  shape, and `ApprovalDecisions.json` for its required fields and decision entry
  shape. `ApprovalDecisions.json` is validated only when it is present/provided.
  All fail closed with an `INVALID_ARTIFACT_SCHEMA` diagnostic before any graph or
  policy interpretation. This validation runs in a phased order — authority-value
  validation, then schema validation, then interpretation validation — where each
  phase gates the next even when aggregate diagnostics are requested.
- **Shape validation is not the whole trust boundary.** Static schema hardening
  across the control-plane inputs is complete, but broader limitations still
  remain and are unchanged by it: no authority subsumption, no approval carryover,
  no real execution, no ambient-credential isolation, and no post-retrieval
  re-gating. Schema validation checks structure, not authority semantics; the
  deferred enforcement gaps documented elsewhere in this file still apply.

## Data Classification Timing Gap

- **Classification discovered after retrieval is not handled by compile-time
  policy alone.** The current model treats data classification as a compile-time
  input. In reality a `retrieve` node's classification may only be known *after*
  it fetches (refreshed content could return at a higher classification than was
  assumed). Closing this gap requires future work: either **post-retrieval
  re-gating** (re-evaluating authority once the real classification is known) or
  a **worst-case compile assumption** (compiling against the most restrictive
  plausible classification up front). Neither is implemented today, so
  classification-driven authority is only as correct as the classification known
  at compile time.

## Authority Subsumption Is Not Defined

- **Authority subsumption requires a future explicit partial order before reuse
  is allowed.** The spec's notions of "narrowed without broadening or ambiguity"
  presuppose a partial order (a lattice) over each authority dimension —
  connector, scope, tool, skill, filesystem, side effect, export, review, and
  approval. No such partial order is defined or implemented. Until it is defined
  and reviewed, **no narrowed-authority reuse or approval carryover may be
  enabled**, because there is no sound basis for deciding that one authority set
  is strictly contained in another. Exact-match approval (above) is the safe
  fail-closed stand-in until then.

## Summary Of The Current Boundary

The current system proves the deterministic control-plane flow — validate,
compile, bind, verify, audit — with a safe no-op execution stand-in. It does
**not** yet enforce the spec's full authority model. The most security-critical
deferred pieces are the authority partial order, post-retrieval classification
re-gating, and true ambient-credential isolation. Each must be designed and
reviewed before approval carryover, narrowed-authority reuse, or real execution
is enabled.
