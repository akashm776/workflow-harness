# Sandbox Backend Strategy

**Status: design only / not implemented.**

This document is a design-only ecosystem strategy checkpoint. It records how
future real execution should depend on existing agent, orchestration, and
sandbox/runtime systems without changing any current `workflow-harness`
behavior.

## Decision

`workflow-harness` will not implement sandbox isolation from scratch.

`workflow-harness` will not implement a full agent runtime from scratch.

`workflow-harness` will not implement Kubernetes agent orchestration from
scratch.

`workflow-harness` is not trying to replace these systems.

`workflow-harness` provides the governance/control-plane boundary around them.

Future real execution should use a pluggable sandbox backend or other
sandbox/runtime substrate behind `workflow-harness` governance.

## Non-Goals

This document does not introduce a broker API.

This document does not introduce a sandbox API.

This document does not introduce an execution API.

This document does not introduce Kubernetes integration.

This document does not introduce Hermes Agent integration.

This document does not introduce kagent/kagents integration.

This document does not introduce NemoClaw/OpenShell integration.

This document does not introduce a verifier implementation.

This document does not introduce evidence behavior.

This document does not introduce credentials behavior.

This document does not introduce network behavior.

This document does not introduce tool/MCP behavior.

This document does not implement real execution.

This document does not implement credentials behavior.

This document does not implement network behavior.

This document does not implement tool/MCP behavior.

## Ecosystem Positioning

`workflow-harness` should not reinvent the wheel. It should integrate with and
govern around existing systems such as:

- Kubernetes
- Hermes Agent
- NemoClaw/OpenShell
- kagent/kagents
- Firecracker
- gVisor
- Docker/Kubernetes isolation
- E2B
- Modal
- other sandbox/runtime substrates

Hermes Agent or another agent runtime may propose workflows, skills, or
workflow patterns.

kagent/kagents may provide Kubernetes-native agent deployment and operations.

Kubernetes may provide workload orchestration.

NemoClaw/OpenShell or another sandbox backend may provide sandboxed execution
and runtime containment.

`workflow-harness` is not trying to replace these systems. It adds governance
around them.

## Architecture Split

`workflow-harness` owns:

- workflow specs
- canonical artifact identity
- compiler validation
- compiler-owned capability requests
- approval request/decision governance
- current-run/request approval scope
- operator cockpit/status
- audit/verifier semantics
- broker adapter contract

Sandbox/backend substrate owns:

- process isolation
- filesystem restrictions
- network policy enforcement
- credential gatewaying
- inference routing
- tool/MCP execution containment
- sandbox lifecycle

## Future Shape

```text
user goal
   Hermes Agent / planner / agent runtime proposes a workflow
   workflow-harness compiler validates the concrete workflow and requested capabilities
   operator reviews current-run/request approval needs
   workflow-harness broker adapter dispatches only compiler-authorized and operator-approved work
   Kubernetes/kagent may orchestrate agent workloads
   NemoClaw/OpenShell or another sandbox backend contains execution
   sandbox/backend result returns to workflow-harness
   workflow-harness verifier/audit/status reports what happened
```

## Trust Boundaries

The trust boundary remains explicit:

```text
Planner suggests.
Compiler authorizes.
Operator approves.
Runtime executes only what was compiler-authorized and operator-approved.
Verifier reports.
Audit preserves lineage.
```

Hermes Agent is not authoritative.

kagent/kagents are not authoritative.

Kubernetes is not authoritative.

NemoClaw/OpenShell is not authoritative.

The sandbox/backend cannot create authority.

Runtime/broker/verifier cannot create authority.

Compiler remains the authority boundary.

Operator approval remains explicit and current-run/request scoped.

## Candidate Integration Points

Candidate integration points may include:

- Hermes Agent or another planner/agent runtime for non-authoritative proposal
- kagent/kagents for Kubernetes-native agent deployment and operations
- Kubernetes for workload orchestration
- NemoClaw/OpenShell as a candidate backend, not a replacement for
  `workflow-harness`
- Firecracker, gVisor, Docker/Kubernetes isolation, E2B, Modal, or another
  sandbox/runtime substrate for execution containment

NemoClaw/OpenShell is a candidate backend, not a replacement for
`workflow-harness`.

## Kubernetes and kagent/kagents Role

Kubernetes may schedule and run workloads.

kagent/kagents may package or operate Kubernetes-native agent workloads.

Neither Kubernetes nor kagent/kagents replace compiler authorization, artifact
identity, approval scope, or audit/verifier/status semantics.

## Hermes Agent Role

Hermes Agent or another agent runtime may suggest workflows, skills, or
workflow patterns.

Hermes Agent is not authoritative.

Planner suggestions remain proposals until `workflow-harness` compiler
validation authorizes concrete workflow and capability artifacts.

## NemoClaw/OpenShell Role

NemoClaw/OpenShell is a candidate backend for sandboxed execution containment.

NemoClaw/OpenShell is not authoritative.

Its role, if adopted later, would be isolation and containment, not governance.

## Sandbox-Policy Warning

The sandbox having policy does not replace compiler authorization.

The sandbox having policy does not replace artifact identity.

The sandbox having policy does not replace current-run/request approval scope.

The sandbox having policy does not replace audit/verifier/status semantics.

## Broker Adapter Contract, Future Only

If real execution is ever pursued, `workflow-harness` should speak to a backend
through a narrow broker adapter contract. That contract remains future-only.

The broker adapter would allow `workflow-harness` to preserve compiler-owned
capability requests, artifact identity, approval scope, and audit/verifier
semantics while delegating actual containment to an external runtime substrate.

Nothing in this document introduces a broker API, a sandbox API, or an
execution API.

## Approval and Authority Implications

Backend policy may restrict runtime behavior, but backend policy is not
authorization.

The sandbox/backend cannot create authority.

Runtime/broker/verifier cannot create authority.

Compiler remains the authority boundary.

Operator approval remains explicit and current-run/request scoped.

## Verifier/Audit/Status Implications

Sandbox or orchestration results would still return to `workflow-harness`
verifier, audit, and operator status semantics.

The sandbox having policy does not replace audit/verifier/status semantics.

The sandbox having policy does not replace compiler authorization, artifact
identity, or current-run/request approval scope.

## What This Does Not Implement

This strategy document does not implement:

- real execution
- broker implementation
- fake/no-op broker interface
- sandbox implementation
- Kubernetes integration
- Hermes Agent integration
- kagent/kagents integration
- NemoClaw/OpenShell integration
- MCP/tool/connector calls
- model inference
- network behavior
- credentials/secrets behavior
- verifier implementation
- evidence generation
- approval carryover
- reusable approvals
- authority subsumption
- canonical JSON/hashing changes

Protected files such as `compiler/canonical_json.py` remain untouched.

## Future Milestones

1. Define the broker adapter contract without granting authority.
2. Bind backend dispatch only to compiler-authorized and operator-approved
   work.
3. Preserve current-run/request approval semantics across orchestration and
   containment layers.
4. Keep verifier/audit/status semantics inside `workflow-harness`.
5. Add backend-specific integration only after those governance boundaries are
   reviewed.

Nothing in this document changes the current safe no-op product boundary.
