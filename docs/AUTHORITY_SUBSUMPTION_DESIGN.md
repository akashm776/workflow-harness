# Authority Subsumption Design

**Status: design only. Not implemented.**

This document defines the partial-order model that would be required *before*
approval carryover or narrowed-authority reuse could ever be implemented. It
describes intended future semantics. No code in this repository implements
authority subsumption, approval carryover, or authority reuse today, and this
document does not change any behavior.

See also `docs/SECURITY_ASSUMPTIONS_AND_LIMITS.md`, which records that
subsumption is undefined and that exact-match approval is the current
fail-closed behavior.

## Current Behavior: Exact-Match Approval

Today a requested approval is considered approved only when an approval decision
matches it **exactly** on `node_id` and `approval_subject_hash` (see
`compiler/approval_resolution.py`). Any change to the approval subject — and
therefore to its hash — invalidates the prior approval and requires a fresh
decision.

Exact-match approval remains the current behavior on purpose:

- It is sound without any authority model. A matching subject hash means the
  approved subject is byte-for-byte the same subject; nothing is inferred.
- It fails closed. When anything about the requested authority changes, the old
  approval simply does not apply, so no stale approval can leak forward.
- It needs no comparison of "how much" authority changed, which is exactly the
  judgement that is unsafe to make without a defined, reviewed model.

The cost of exact-match is approval churn: a trivial, strictly-narrowing change
(for example, removing one connector scope) still forces re-approval. That cost
is acceptable until a sound subsumption model exists.

## Why Subsumption Is Required Before Reuse

Approval carryover and narrowed-authority reuse both rest on a single claim:
*the new requested authority is no broader than what was already approved.*
Making that claim requires a **partial order** over authority — a way to decide,
for two authority sets A and B, whether A is equal to, strictly narrower than,
strictly broader than, or not comparable with B.

Without such an order, "this change only narrows authority" is an unverified
human assertion. Acting on it would let broadened or subtly different authority
ride forward on an old approval — a silent privilege escalation. Therefore no
reuse or carryover may be enabled until the partial order below is defined,
implemented, and reviewed.

## Authority Dimensions

Authority is compared independently across each of these dimensions. Each
dimension has its own notion of narrower/broader; they are not interchangeable.

- **connector** — which connectors are reachable.
- **scope** — the structured resource scope within a connector (project, space,
  repo, path, etc.).
- **tool** — which tools may execute.
- **skill** — which skills are visible.
- **filesystem** — readable/writable filesystem locations.
- **side effect** — which side effects (writes, ticket creation, command
  execution, etc.) are permitted.
- **export** — whether and how data may leave the boundary.
- **review** — the required review strength (e.g. auto / reviewable /
  mandatory-review).
- **approval** — the required approval obligations.

A future model must define, per dimension, what "narrower" means concretely
(for example: a subset of connectors is narrower; a contained structured scope
is narrower; a stricter review requirement is narrower, not broader).

## Relation Outcomes

Comparing the new authority against the approved authority on a single dimension
yields exactly one outcome:

- **equal** — identical authority on this dimension.
- **narrower** — the new authority is strictly contained in the approved
  authority (less access, or a stricter obligation) on this dimension.
- **broader** — the new authority grants more than the approved authority on
  this dimension.
- **incomparable** — neither contains the other (for example, two disjoint
  scopes, or two scopes where each allows something the other does not).
- **ambiguous** — the comparison cannot be decided soundly (missing structure,
  unnormalized values, or any case the model cannot classify with confidence).

`incomparable` and `ambiguous` are distinct: `incomparable` is a definite "these
do not nest"; `ambiguous` is "we cannot tell." Both are treated the same way for
the reuse decision (see below), but they are reported distinctly for audit and
diagnosis.

## Per-Dimension Narrowing Rules

Each dimension defines "narrower" on its own terms. A future model must implement
these as explicit, governed comparisons — never inferred from arbitrary labels.
"Narrower" always means less authority or a stricter obligation; the reverse is
"broader".

- **connector** — narrower is a subset of the approved connector set. A new set
  that adds any connector is broader. Disjoint sets are incomparable.
- **scope** — narrower is a structurally contained scope (for example
  `project/ABC/board/3` is narrower than `project/ABC`). Two scopes where each
  allows something the other does not are incomparable. Unstructured or
  unnormalized scope is ambiguous.
- **tool** — narrower is a subset of the approved tools. Adding a tool is broader.
- **skill** — narrower is a subset of the visible skills. Adding visibility is
  broader.
- **filesystem** — narrower is a subset of the approved paths, and a stricter
  access mode is narrower (read is narrower than read/write). Paths that overlap
  only partially are incomparable.
- **side effect** — side-effect narrowing must follow an
  explicit governed partial order, not a universal total order. A side-effect
  class may be treated as narrower **only when the relation is explicitly
  defined** by that governed order. The classes from
  `SIDE_EFFECT_CATALOG_DESIGN.md` (read-only,
  local write, external write, network call, export, deletion / destructive
  action) are named for reference only; this does **not** imply every pair is
  safely comparable. Any pair whose relation is not explicitly defined is
  incomparable or ambiguous and requires new approval.
- **export** — narrower is less export capability, but only where the governed
  order defines it (for example "no export" narrower than "redacted export"
  narrower than "full export"). Undefined or unlabeled export relations are
  ambiguous.
- **review** — a stricter review obligation is narrower; less review is broader.
  More review can be narrower. The ordering must be defined by governed policy,
  not inferred from arbitrary labels. Ambiguous review labels are never narrower.
- **approval** — a stricter or additional approval obligation is narrower;
  removing an approval obligation is broader. As with review, the relation must be
  defined by governed policy. Ambiguous approval labels are never narrower.

Across every dimension, **ambiguous is never narrower**, and any dimension that
is broader, incomparable, or ambiguous requires new approval. There is **no
scoring, no tradeoffs, and no partial credit** between dimensions.

## The Reuse Rule

Reuse of a prior approval may be *considered* only when **every** dimension
compares as **equal or strictly narrower**.

- If all dimensions are `equal` → the subject is unchanged in authority terms;
  this is the exact-match case generalized.
- If all dimensions are `equal` or `narrower`, with at least one `narrower` →
  the new authority is a strict narrowing and may be *considered* for reuse.

If **any** dimension is `broader`, `incomparable`, or `ambiguous`, the result
**fails closed**: no reuse, no carryover, and a new approval is required. A
single non-narrowing dimension is sufficient to require re-approval, regardless
of how the other dimensions compare. There is no averaging, scoring, or
trading-off across dimensions.

"May be considered" is deliberate: passing the narrowing rule is a necessary
precondition for reuse, not an automatic grant. Any future implementation would
still emit an audit event documenting the carryover and remain subject to the
broader governance model.

## Fail-Closed Default

The default for every undecided or non-narrowing case is to require new
approval. The model never broadens authority, never infers intent, and never
treats `ambiguous` as `narrower`. When in doubt, re-approve.

## Examples

These are design-only illustrations. They describe how a future model would
classify a single comparison; nothing here is implemented.

- **equal** — approved scope `project/ABC`, new request `project/ABC`. Identical;
  treated as the exact-match case generalized.
- **narrower** — approved scope `project/ABC`, new request
  `project/ABC/board/3`. The new scope is structurally contained, so this
  dimension is narrower.
- **broader** — approved connectors `{wiki}`, new request `{wiki, issue-tracker}`.
  The new set adds a connector, so this dimension is broader and requires new
  approval.
- **incomparable** — approved filesystem path `repo/src`, new request
  `repo/docs`. Neither contains the other; the relation does not nest, so it is
  incomparable and requires new approval.
- **ambiguous** — approved scope `project/ABC`, new request an unstructured
  string `"the ABC stuff"`. The comparison cannot be decided soundly, so it is
  ambiguous; ambiguous is never narrower, and it requires new approval.

A compact multi-dimension example: suppose connector is `equal`, scope is
`narrower`, and review is `narrower`, but side effect is `ambiguous` because the
governed order does not define the relevant pair. Reuse is only considered when
every dimension is equal or narrower, so the single ambiguous dimension makes
the whole comparison fail closed and require new approval — regardless of the
other dimensions. There is no scoring, no tradeoffs, and no partial credit.

Exact-match approval remains current behavior; none of these examples is
implemented.

## Not Implemented

To be explicit: authority subsumption is **not implemented**. There is no
partial order, no narrowing comparison, no approval carryover, and no
narrowed-authority reuse in the codebase. This document is a design target only.
Until it is implemented and reviewed, exact-match approval remains the sole
behavior.
