# Repo Terminology Map

**Status: documentation only.**

This document is documentation only.

This document does not implement runtime behavior.

This document does not implement compiler behavior.

This document does not implement schema behavior.

This document does not implement planner behavior.

This document does not implement broker behavior.

This document does not implement sandbox behavior.

This document does not implement verifier behavior.

This document does not implement execution behavior.

This document does not implement Kubernetes integration.

This document does not implement Hermes Agent integration.

This document does not implement kagent/kagents integration.

This document does not implement NemoClaw/OpenShell integration.

This document does not change canonical JSON.

This document does not change hashing.

## Purpose

This map prevents future confusion between current repo folder meanings and
future ecosystem or orchestration concepts.

The root `README.md` frames `workflow-harness` as a deterministic
policy-governed dynamic workflow harness. It also says the planner is
intentionally deferred and that the initial work should prove the
compiler/verifier loop with hand-authored workflow fixtures.

## Current Folder Meanings

### `schemas/`

`schemas/` is the control-plane artifact contract layer.

It contains canonical JSON Schemas for workflow-harness control-plane
artifacts.

`schemas/` is not execution.

It is not authorization by itself.

It is not the planner.

It is not the broker.

Schema, `WorkflowSpec`, `NodeTypeRegistry`, canonical JSON, and hashing changes
remain red-slice work.

### `planner/`

`planner/` currently contains a deterministic planner skeleton.

It turns a plain-text goal into candidate artifacts such as
`WorkflowSpec.json`, `RequestedAuth.json`, and `ApprovalRequests.json`.

It calls no LLM.

It infers no authority.

It writes no compiled artifacts.

It writes no runtime artifacts.

Planner output is non-authoritative until compiler validation.

### `compiler/`

`compiler/` is the authority boundary.

It owns static validation and compiled governance artifacts.

Compiler validation is what turns candidate proposals into compiler-owned
artifacts.

Runtime, broker, planner, schemas, and verifier do not create authority.

### `orchestrator/`

`orchestrator/` currently means the safe-noop local harness coordinator.

It wires the current local compile/write/load/verify/audit/manifest/result
flow.

`orchestrator/` is not Claude-style workflow orchestration.

`orchestrator/` is not a general workflow-pattern runtime.

`orchestrator/` is not Hermes Agent integration.

`orchestrator/` is not Kubernetes orchestration.

`orchestrator/` is not kagent/kagents integration.

`orchestrator/` is not NemoClaw/OpenShell integration.

`orchestrator/` is not a sandbox broker.

### `broker/`

`broker/` currently contains future sandbox/broker data-shape helpers only.

Broker helpers are build-only.

Broker helpers execute nothing.

Broker helpers authorize nothing.

Broker helpers verify no sandbox.

Broker helpers call no tools/connectors.

Broker helpers write no files.

Broker helpers are not a broker implementation.

Broker helpers are not a sandbox implementation.

Broker helpers are not runtime authority enforcement.

### `runtime/`

`runtime/` currently owns safe-noop runtime surfaces.

It also owns artifact loading/checking, execution manifest/result handling,
runtime verification checks, and read-only/fail-soft run status summary logic.

The run-status summary never writes anything.

The run-status summary never raises on missing, unreadable, or malformed JSON.

The run-status summary reads only known local run artifacts.

The run-status summary never reads tools, connectors, or network.

The run-status summary does not change runtime behavior.

### `tui/`

`tui/` renders display/operator status.

It is not authority.

It is not approval semantics.

It is not execution.

### `docs/`

`docs/` records design decisions and safety boundaries.

Design docs must not be interpreted as implemented behavior.

## Terms That Must Not Be Conflated

Current repo folder names must not be conflated with future ecosystem terms
such as Hermes Agent planning, Claude-style workflow orchestration,
Kubernetes/kagent orchestration, NemoClaw/OpenShell sandbox execution, a real
broker adapter, or a real verifier/evidence layer.

The current repo uses those names for safe-noop control-plane components,
documentation, or future data-shape sketches only.

## Current Implementation Boundary

The current planner is deterministic and non-authoritative.

The current compiler remains the authority boundary.

The current runtime remains safe-noop/read-only reporting.

The current operator cockpit and run-status surfaces are display-only
projections over local artifacts.

Nothing in the current repo turns `planner/`, `orchestrator/`, `broker/`,
`runtime/`, or `tui/` into external orchestration or execution substrates.

## Future Ecosystem Terms

`workflow-harness` should integrate with and govern around systems such as:

- Hermes Agent
- Kubernetes
- kagent/kagents
- NemoClaw/OpenShell
- Firecracker
- gVisor
- Docker/Kubernetes isolation
- E2B
- Modal
- other sandbox/runtime substrates

Those systems are future ecosystem reference points. They are not the current
meaning of repo folders.

## Claude Workflow Concepts Vs `orchestrator/`

Claude-style workflow orchestration asks who holds the plan, for example:

- subagent
- skill
- lead-agent team
- workflow script
- saved workflow
- compiled workflow spec

By contrast, `workflow-harness` current `orchestrator/` means the safe-noop
local harness coordinator.

It is not a workflow script runtime.

It is not an agent-team runtime.

It is not Kubernetes orchestration.

Future borrowed ideas may include:

- view raw proposed orchestration
- phase list
- agent/node count
- token budget
- concurrency limits
- loop stop condition
- resume/retry status

Those are future status/cockpit/verifier/audit concepts only, not current
implementation.

## Zero-Trust Language Mapping

This is terminology mapping only. It does not claim these future controls are
implemented today.

- trust nothing / verify everything / assume breach
- task-scoped permissions -> current-run/request approval scope
- identity -> canonical artifact identity and compiler-owned capability requests
- sandboxing -> delegated to NemoClaw/OpenShell/Kubernetes/backend substrate
- input/output controls -> future verifier/audit/status semantics
- memory poisoning -> future evidence/provenance and planner-input boundaries

## Red-Slice Terminology

The following terms remain red-slice areas and should not be changed casually:

- schema / `WorkflowSpec` / `NodeTypeRegistry`
- canonical JSON
- hashing
- compiler authority
- approval semantics
- broker implementation
- sandbox implementation
- verifier implementation
- evidence generation
- Hermes Agent integration
- Kubernetes integration
- kagent/kagents integration
- NemoClaw/OpenShell integration

## What This Document Does Not Implement

This document does not implement runtime behavior.

This document does not implement compiler behavior.

This document does not implement schema behavior.

This document does not implement planner behavior.

This document does not implement broker behavior.

This document does not implement sandbox behavior.

This document does not implement verifier behavior.

This document does not implement execution behavior.

This document does not implement Kubernetes integration.

This document does not implement Hermes Agent integration.

This document does not implement kagent/kagents integration.

This document does not implement NemoClaw/OpenShell integration.

This document does not change canonical JSON.

This document does not change hashing.
