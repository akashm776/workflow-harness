# Real Execution Threat Model

**Status: design only. Not implemented.**

This document defines the prerequisites that must be satisfied *before*
workflow-harness could ever move beyond safe no-op runtime behavior. It describes
intended future requirements and threats. No real execution exists in this
repository, and this document changes no behavior. It is a design target and a
gate, not a plan to enable execution now.

See also `docs/SECURITY_ASSUMPTIONS_AND_LIMITS.md` (current boundary and deferred
gaps) and `docs/AUTHORITY_SUBSUMPTION_DESIGN.md` (the authority partial order that
also remains design-only).

## 1. Current State: V1 Remains No-Op Only

V1 remains **no-op only**. The execution path is a deterministic stand-in: it
writes an `ExecutionManifest.json` and a no-op `ExecutionResult.json` and
performs no real work, no tool calls, no connector calls, and no side effects.
Nothing in this document changes that. Real execution stays disabled until every
prerequisite below is implemented and reviewed.

## 2. Trust Boundary

The trust boundary is unchanged and non-negotiable:

- The **planner remains untrusted**. Planner output is a proposal only and grants
  no authority.
- The **compiler remains the sole authority boundary**. Only deterministic
  compilation produces authority-bearing artifacts. No runtime, tool, connector,
  or retrieved datum may grant or widen authority outside the compiler.

Real execution does not relax this boundary; it raises the bar for what the
compiler and a sandbox must prove before any side effect is permitted.

## 3. Real Execution Is Not Implemented

Real execution is explicitly **not implemented**. There is no tool runner, no
connector client, no sandbox, and no side-effect channel in the codebase. The
sections below are requirements for a hypothetical future capability, not
descriptions of existing behavior.

## 4. Ambient Authority Risk

The central risk of real execution is **ambient authority**: a process that runs
real work inherits authority nobody declared or approved. A future execution
capability must treat all of the following as hostile ambient sources that must
be neutralized, not trusted:

- local environment variables (secrets, tokens, config)
- shell access and inherited shell state
- the local filesystem (home directory, caches, credential files)
- cloud credentials (instance metadata, profile/role credentials)
- OAuth tokens and refresh tokens
- MCP servers and connector sessions already authenticated on the host
- browser sessions and cookies

Any of these can grant authority that the compiler never approved. A local,
in-process runtime cannot neutralize them by itself (see
`SECURITY_ASSUMPTIONS_AND_LIMITS.md`). This is the core reason real execution is
gated.

## 5. Sandbox / Broker Requirement

Execution must not happen directly in the harness process. It must happen in an
isolated **broker/sandbox** that:

- runs with no inherited ambient credentials or session material,
- exposes only the compiled bindings the compiler approved,
- mediates every tool/connector call through a broker that enforces the compiled
  authority,
- is isolated at the OS / container / process / network level (for example a
  separate uid, a restricted container, a credential-free execution sandbox, or a
  network namespace),
- and can attest its own configuration so the harness can verify the sandbox
  state before trusting any result.

If the sandbox state cannot be verified, execution must not proceed.

## 6. Connector / Tool Allowlist Requirement

No tool or connector may be invoked unless it is on a compiler-approved
allowlist. Each entry must be:

- **declared** — present in a governed catalog, never ad hoc,
- **scoped** — bound to a structured, least-privilege scope,
- **versioned** — pinned to a specific tool/connector version,
- **compiler-approved** — admitted only through deterministic compilation into
  execution bindings.

Undeclared, unscoped, unversioned, or uncompiled tools and connectors are denied.

## 7. Side-Effect Policy

Side effects must be classified and governed by class, from least to most
dangerous:

- **read-only** — reads governed sources, no mutation.
- **local write** — writes only to run-local, sandboxed storage.
- **external write** — mutates an external system (e.g. ticket creation, repo
  push).
- **network call** — outbound network access.
- **export** — moves data outside the trust boundary.
- **deletion / destructive action** — irreversible or destructive operations.

Each class requires its own compiled authority and review/approval obligations.
More dangerous classes require stricter gating. No node may perform a side effect
of a class it was not compiled and approved to perform.

## 8. Post-Retrieval Re-Gating

Retrieved data must not silently expand authority or trigger new side effects.
What a `retrieve` step returns (its real classification, new references, or
embedded instructions) may differ from what was assumed at compile time.
Therefore:

- retrieved content is never authority-bearing,
- any action implied by retrieved data must be re-validated by the compiler
  before it can run,
- a higher-than-assumed data classification or a newly implied side effect forces
  recompilation and, where required, new approval.

Post-retrieval re-gating closes the gap between compile-time assumptions and
run-time reality.

## 9. Audit Requirements

Every proposed and every denied side effect must be logged deterministically.
The audit record must, at minimum, capture:

- the proposed side effect and its class,
- the compiled authority it was checked against,
- the decision (permitted / denied) and the reason,
- the node, revisions, and artifact references involved,
- and a stable, deterministic ordering and content suitable for review.

Denials are first-class audit events, not silent drops.

## 10. Failure Mode: Fail Closed

Execution must **fail closed** in every uncertain or non-narrowing case,
including:

- ambiguous authority,
- missing or unstructured scope,
- authority broader than what was approved,
- unverifiable sandbox state,
- any undeclared connector, tool, or session material becoming visible.

The default is to deny and require new compilation/approval. Execution never
proceeds on assumption, inference, or partial verification.

## 11. Non-Goals

This document does not enable or implement any of the following, and explicitly
keeps them out of scope:

- no tool execution
- no connector implementation
- no sandbox/broker implementation
- no side-effect channel
- no approval carryover
- no authority subsumption behavior

It is a design-only threat model. Real execution remains disabled until these
prerequisites are designed, implemented, and reviewed.
