# Sandbox / Broker Interface Design

**Status: design only. Not implemented.**

This document defines the future interface between workflow-harness and an
isolated execution broker/sandbox. It describes intended future contracts and
requirements. No sandbox, broker, tool runner, connector client, or side-effect
channel exists in this repository, and this document changes no behavior. It is a
design target and a gate, not a plan to enable execution now.

See also `docs/REAL_EXECUTION_THREAT_MODEL.md` (the prerequisites that gate any
real execution), `docs/SIDE_EFFECT_CATALOG_DESIGN.md` (the governed catalog of
tools/connectors/side-effect classes), and `docs/AUTHORITY_SUBSUMPTION_DESIGN.md`
(the authority partial-order model that also remains design-only).

## 1. Status

This is a design-only checkpoint. The sandbox/broker interface is **not
implemented**. There is no broker process, no sandbox, and no interface code in
the repository.

## 2. Current State: V1 Remains No-Op Only

V1 remains **no-op only**. No sandbox, broker, tools, connectors, or side-effect
channel exists. The execution path is a deterministic stand-in that performs no
real work. Nothing in this document changes that.

## 3. Trust Boundary

The trust boundary is unchanged:

- The **planner remains untrusted**. Planner output is a proposal only and may
  not drive the broker.
- The **compiler remains the sole authority boundary**. The broker may act only
  on compiled authority; it never infers, adds to, or widens authority, and no
  retrieved datum or sandbox result may grant authority.

## 4. Purpose

The broker/sandbox is the **only** future place where real execution could ever
happen, and only under compiled authority. It exists so that any real side effect
is mediated through a single isolated chokepoint that enforces compiled bindings
and can be audited. The harness process itself never executes real work.

## 5. Isolation Requirements

The sandbox must run with no inherited authority. At minimum it must guarantee:

- **no inherited environment secrets** (no ambient env vars / tokens),
- **no inherited shell or session state**,
- **no ambient cloud, OAuth, browser, or MCP/connector credentials**,
- a **restricted filesystem** (no access to host home/credentials/caches),
- a **restricted network** (no outbound access unless explicitly compiled),
- **run-local storage only** unless broader storage is explicitly compiled.

Isolation must be enforced at the OS / container / process / network level, not
by convention inside a shared process.

## 6. Broker Input Contract

The harness gives the broker only compiled, authority-bearing inputs:

- compiled artifact references,
- compiled execution bindings,
- node identity and revision,
- the approved side-effect class,
- the declared tool/connector identity and version,
- the structured scope,
- an audit correlation id.

The broker receives nothing else. It does not read proposal artifacts, planner
output, or any host state to decide what to do.

## 7. Broker Decision Contract

Before acting, the broker emits a deterministic decision:

- **permitted / denied**,
- a **reason code**,
- the **checked authority** (which compiled bindings/dimensions were evaluated),
- the **sandbox attestation / verification result**,
- the **side-effect class**,
- **deterministic audit fields** (stable content and ordering).

A decision of `denied` is terminal for that attempt and is a first-class audited
event.

## 8. Broker Result Contract

If permitted, execution produces a result that must guarantee:

- **success / failure / denied** status,
- **no hidden authority expansion** (the action stayed within compiled bindings),
- **no unreviewed exports**,
- **no undeclared files or network effects**,
- **stable references to produced outputs only when allowed**.

Any observed effect outside the compiled bindings invalidates the result and is
treated as a failure that fails closed.

## 9. Attestation Requirement

The harness must **verify sandbox state before trusting any result**. The broker
must attest its isolation configuration, and the harness must check that
attestation. If the sandbox state cannot be verified, the attempt **fails
closed** — no result is trusted and no output is consumed.

## 10. Relationship to `REAL_EXECUTION_THREAT_MODEL.md`

The broker/sandbox is the mechanism that would satisfy the sandbox-isolation
prerequisite named in `REAL_EXECUTION_THREAT_MODEL.md`. This document specifies
that interface; it does not lift any other gate in the threat model. Real
execution remains blocked.

## 11. Relationship to `SIDE_EFFECT_CATALOG_DESIGN.md`

The broker enforces, at execution time, the entries defined by
`SIDE_EFFECT_CATALOG_DESIGN.md`: only declared, scoped, versioned, and
compiler-approved tools/connectors of an approved side-effect class may run, and
only within their `sandbox_requirements`. The broker adds no capability beyond
the catalog.

## 12. Relationship to `AUTHORITY_SUBSUMPTION_DESIGN.md`

The broker may later consume the authority dimensions described in
`AUTHORITY_SUBSUMPTION_DESIGN.md` when checking a request against compiled
bindings. That is a possible future relationship only: **authority subsumption
behavior remains not implemented**, and the broker neither narrows authority nor
carries approvals forward. Exact-match approval remains the current behavior.

## 13. Audit Requirements

Every proposed, permitted, denied, and failed side-effect attempt must be
deterministically auditable. The audit trail must capture the decision, the
checked authority, the side-effect class, the sandbox attestation result, and the
node/revision/correlation references, with stable content and ordering suitable
for review. Denials and failures are first-class audit events, not silent drops.

## 14. Failure Modes

The broker fails closed in every uncertain or non-conforming case, including:

- an **undeclared tool** or connector,
- **broader-than-approved scope**,
- **missing or unstructured scope**,
- **ambiguous authority**,
- **sandbox unverifiable** state,
- **unexpected output, export, or network access**.

The default is to deny and require new compilation/approval. The broker never
proceeds on inference, assumption, or partial verification.

## 15. Non-Goals

This document does not enable or implement any of the following, and explicitly
keeps them out of scope:

- no sandbox implementation
- no broker implementation
- no tool execution
- no connector implementation
- no side-effect channel
- no approval carryover
- no authority subsumption behavior

It is a design-only interface specification. Real execution remains disabled until
these prerequisites are designed, implemented, and reviewed.
