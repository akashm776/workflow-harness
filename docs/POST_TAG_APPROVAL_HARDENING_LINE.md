# Post-Tag Approval Hardening Line

This is a docs-only checkpoint recording the hardening line that begins **after**
the `v0.1.0-safe-noop-governance-cockpit` milestone tag. It explains why the
current `HEAD` is intentionally ahead of that tag and what the post-tag commits
protect.

## Status

- Docs/tests only.
- No behavior change.
- No canonical JSON/hashing change.
- No runtime/execution change.
- No new validator added in this slice.

## Milestone Tag vs Current HEAD

- The annotated tag `v0.1.0-safe-noop-governance-cockpit` marks the **V1 Safe
  No-Op Governance Cockpit** milestone at commit `0131572`
  (`Document V1 safe noop governance cockpit checkpoint`).
- The milestone tag remains pinned to `0131572`. It must not be moved.
- The current `HEAD` is **intentionally ahead** of that tag. Being ahead of the
  tag is expected, not a discrepancy.

## Post-Tag Commits

The two commits after the tag start the next hardening line:

```text
4f98ced Reject unsupported approval scope claims
927bb7d Reject unsupported approval identity claims
```

These extend the existing fail-closed static validation surface. They are
hardening-only: they reject additional planner-controlled claims that V1 does
not support.

## Hardened Approval Invariants

- **Approval-scope invariant.** The planner cannot claim that an approval is
  reusable, persistent, global, inherited, valid across runs, or valid across
  requests. Such claims fail closed.
- **Approval-identity invariant.** The planner cannot supply or spoof approval
  identity, proof, receipt, signature, subject, run, or request identifiers.
  Such claims fail closed.

Both invariants are fail-closed static validation hardening changes only. They
reject unsupported planner claims; they do not grant, approve, authorize, or
create authority.

## What These Commits Do Not Implement

These commits do **not** implement any of the following:

- reusable approval
- approval carryover
- authority subsumption
- real approval binding
- real execution
- broker behavior
- fake/no-op broker interface
- sandbox behavior
- verifier behavior
- evidence generation
- tool/MCP/model/network/credential behavior

## Trust Boundary (Unchanged)

- The planner remains non-authoritative.
- The compiler remains the sole authority boundary.
- Operator approval remains explicit and current-run/request scoped.
- The runtime remains safe no-op.

## Related Docs

- [`V1_SAFE_NOOP_GOVERNANCE_COCKPIT_CHECKPOINT.md`](V1_SAFE_NOOP_GOVERNANCE_COCKPIT_CHECKPOINT.md)
  — the milestone checkpoint at the tag.
- [`STATIC_VALIDATION_ORDERING_CONTRACT.md`](STATIC_VALIDATION_ORDERING_CONTRACT.md)
  — the Phase 3 validator order these invariants live within.
