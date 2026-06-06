# Side-Effect Catalog and Allowlist Design

**Status: design only. Not implemented.**

This document defines the future governed catalog for tools, connectors, and
side-effect capabilities. It describes intended future structure and rules. No
catalog, tool, connector, or side-effect channel exists in this repository, and
this document changes no behavior. It is a design target and a gate, not a plan
to enable tools or execution now.

See also `docs/REAL_EXECUTION_THREAT_MODEL.md` (the prerequisites that gate any
real execution) and `docs/AUTHORITY_SUBSUMPTION_DESIGN.md` (the authority
partial-order model that also remains design-only).

## 1. Status

This is a design-only checkpoint. The side-effect catalog and allowlist are
**not implemented**. There is no catalog file, no schema enforcement, no tool
runner, and no connector client in the codebase.

## 2. Current State: V1 Remains No-Op Only

V1 remains **no-op only**: there are no real tools and no real connectors. The
execution path is a deterministic stand-in that performs no side effects. Nothing
in this document changes that.

## 3. Trust Boundary

The trust boundary is unchanged:

- The **planner remains untrusted**. Planner output is a proposal only and may
  not declare or grant catalog entries.
- The **compiler remains the sole authority boundary**. Only deterministic
  compilation may admit a catalog entry into effective authority. No runtime,
  tool, connector, or retrieved datum may add to or widen the catalog.

## 4. Catalog Purpose

The catalog is the **governed declaration** of which tools, connectors, and
side-effect capabilities may ever be used. It exists so that capability is
explicit, reviewed, and bounded: nothing may act unless it appears in the catalog
and was admitted through compilation. The catalog is static governance input,
authored and reviewed out of band — never produced by the planner or by runtime.

## 5. Entry Admission Requirements

Every tool or connector entry must be:

- **declared** — present in the governed catalog, never ad hoc or inferred,
- **scoped** — bound to a structured, least-privilege scope,
- **versioned** — pinned to a specific tool/connector version,
- **compiler-approved** — admitted only through deterministic compilation into
  execution bindings.

An entry that is not declared, scoped, versioned, and compiler-approved is not
usable.

## 6. Side-Effect Classes

Each catalog entry declares exactly one side-effect class, ordered from least to
most dangerous:

- **read-only** — reads governed sources, no mutation.
- **local write** — writes only to run-local, sandboxed storage.
- **external write** — mutates an external system (e.g. ticket creation, repo
  push).
- **network call** — outbound network access.
- **export** — moves data outside the trust boundary.
- **deletion / destructive action** — irreversible or destructive operations.

More dangerous classes carry stricter scope, sandbox, audit, and review/approval
obligations.

## 7. Required Fields for a Future Catalog Entry

A future catalog entry is expected to require, at minimum:

- `connector_name` or `tool_name` — the declared identity of the capability.
- `version` — the pinned version of the tool/connector.
- `side_effect_class` — one of the classes in section 6.
- `allowed_scopes` — the structured, least-privilege scopes permitted.
- `authority_dimensions` — the authority dimensions this entry touches
  (connector, scope, tool, skill, filesystem, side effect, export, review,
  approval), aligning with `AUTHORITY_SUBSUMPTION_DESIGN.md`.
- `sandbox_requirements` — the isolation the entry requires before it may run
  (per `REAL_EXECUTION_THREAT_MODEL.md`).
- `audit_requirements` — what must be logged deterministically when the entry is
  proposed, permitted, or denied.
- `review_or_approval_requirements` — the review strength and approval
  obligations the entry carries.

These fields are a design target; no schema enforces them today.

## 8. Deny-by-Default Behavior

The catalog is **deny-by-default**. An action is denied and must fail closed when
it is any of:

- **undeclared** — not present in the catalog,
- **unscoped** — missing or unstructured scope,
- **unversioned** — no pinned version,
- **ambiguous** — cannot be soundly classified or matched,
- **broader than approved** — requests more than the compiled authority allows,
- **sandbox-unverifiable** — the required sandbox state cannot be verified.

There is no implicit allow, no inference of intent, and no partial-verification
pass-through. When in doubt, deny and require new compilation/approval.

## 9. Relationship to `REAL_EXECUTION_THREAT_MODEL.md`

This catalog is one of the prerequisites named in
`REAL_EXECUTION_THREAT_MODEL.md`. The threat model requires a connector/tool
allowlist, a side-effect policy, sandbox isolation, audit, and fail-closed
behavior before any real execution. This document specifies the allowlist and
side-effect-class portion of those prerequisites. It does not lift any other gate
in the threat model; real execution remains blocked.

## 10. Relationship to `AUTHORITY_SUBSUMPTION_DESIGN.md`

The catalog's `authority_dimensions` and `allowed_scopes` may later supply the
per-dimension inputs that authority subsumption would compare. That is a possible
future relationship only: **authority subsumption behavior remains not
implemented**, and this catalog neither defines nor enables narrowing, reuse, or
approval carryover. Exact-match approval remains the current behavior.

## 11. Non-Goals

This document does not enable or implement any of the following, and explicitly
keeps them out of scope:

- no tool execution
- no connector implementation
- no sandbox/broker implementation
- no runtime side-effect channel
- no approval carryover
- no authority subsumption behavior

It is a design-only catalog and allowlist schema. Real tools, connectors, and
side effects remain disabled until these prerequisites are designed, implemented,
and reviewed.
