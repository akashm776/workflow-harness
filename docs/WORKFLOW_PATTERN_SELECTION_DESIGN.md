# Workflow Pattern Selection Design

**Status: design only / not implemented.**

This document is a design-only checkpoint for future workflow-pattern
selection. It does not implement runtime behavior, schema behavior, compiler
behavior, planner behavior, broker behavior, sandbox behavior, or execution
behavior.

## Decision

Future `workflow-harness` may support selectable workflow patterns such as
Plan-Solve, ReAct, bounded only, REWOO / dependency-aware DAG,
LLMCompiler-style parallel DAG, Reflection, Storm-like research synthesis, and
Handoff / multi-agent.

Workflow pattern selection is non-authoritative.

Planner or Hermes Agent may propose a workflow pattern.

Compiler validates the concrete workflow and requested capabilities.

Operator reviews approval implications.

Runtime executes only compiler-authorized and operator-approved work.

Verifier/audit/status report what happened.

## Non-Goals

This document does not change WorkflowSpec.

This document does not change schemas.

This document does not change canonical JSON.

This document does not change hashing.

This document does not implement planner behavior.

This document does not implement Hermes Agent integration.

This document does not implement kagent/kagents integration.

This document does not implement Kubernetes integration.

This document does not implement NemoClaw/OpenShell integration.

This document does not implement broker implementation.

This document does not implement sandbox implementation.

This document does not implement real execution.

## Pattern Selection Is Not Authority

The trust boundary remains:

```text
Planner suggests.
Compiler authorizes.
Operator approves.
Runtime executes only what was compiler-authorized and operator-approved.
Verifier reports.
Audit preserves lineage.
```

Workflow pattern selection is non-authoritative.

Hermes Agent is not authoritative.

A planner-selected pattern does not authorize tools.

A planner-selected pattern does not authorize execution.

A planner-selected pattern does not create approvals.

A planner-selected pattern does not bind approvals.

Compiler remains the authority boundary.

Operator approval remains explicit and current-run/request scoped.

Replanning must not inherit approval automatically.

Dynamic patterns require recompile/reapproval when requested scope changes.

## Ecosystem Positioning

`workflow-harness` should not reinvent Hermes Agent, kagent/kagents,
Kubernetes, NemoClaw/OpenShell, or agent-framework orchestration.

Hermes Agent / planner may propose pattern, skills, and workflow structure.

kagent/kagents and Kubernetes may operate agent workloads.

NemoClaw/OpenShell or another backend may contain execution.

`workflow-harness` governs the concrete compiled workflow, approvals, artifact
identity, audit, and status.

## Orchestration Form vs Pattern Family

Pattern family describes the shape of reasoning/work:

- Plan-Solve
- ReAct bounded loop
- REWOO / dependency-aware DAG
- LLMCompiler-style parallel DAG
- Reflection
- Storm-like research synthesis
- fan-out-and-synthesize
- adversarial verification
- generate-and-filter
- tournament
- loop-until-done
- handoff / multi-agent

Orchestration form describes who/what holds the plan:

- planner/Hermes-generated candidate workflow
- skill instruction
- subagent delegation
- lead-agent team
- workflow script
- saved workflow template
- compiled WorkflowSpec

Planner/Hermes may propose workflows.

A workflow script may also hold or propose orchestration.

A saved workflow template may propose repeatable orchestration.

None of these are authoritative.

Only `workflow-harness` compiler validation can turn a concrete proposal into
compiler-owned governed artifacts.

## Candidate Pattern Families

These are future design concepts only. They are not implemented patterns.

### Plan-Solve

Plan-Solve is a decomposable ordered task plan.

### ReAct, bounded only

ReAct, bounded only, is an observation/action loop with explicit max
iterations and tool authorization.

### REWOO / dependency-aware DAG

REWOO / dependency-aware DAG models explicit dependencies between planned
steps.

### LLMCompiler-style parallel DAG

LLMCompiler-style parallel DAG allows independent nodes to run concurrently
only after compiler validation.

### Reflection

Reflection is a generator/critic/revision loop with bounded iterations and no
new authority.

### Storm-like research synthesis

Storm-like research synthesis is an outline/retrieve/synthesize/report pattern
with source/evidence implications.

### Handoff / multi-agent

Handoff / multi-agent is role transfer or specialist delegation with role
boundaries and authority isolation.

## Current Implementation Grounding

The current planner is a deterministic skeleton that produces candidate
artifacts only.

Planner output is non-authoritative.

The current planner does not call an LLM.

The current planner does not execute anything.

The current planner does not write compiled artifacts.

The current compiler remains the authority boundary.

The current runtime remains safe no-op/read-only reporting.

The current operator cockpit/status surfaces are display-only projections.

## Pattern Metadata, Future Only

Any future pattern metadata would be illustrative only until separately
designed, compiled, and reviewed.

Illustrative only:

```json
{
  "workflow_pattern": {
    "pattern_id": "plan_solve",
    "pattern_version": "v1",
    "selection_reason": "goal decomposes into ordered subtasks",
    "constraints": {
      "max_steps": 8,
      "allows_replanning": true,
      "allows_parallel_nodes": false,
      "requires_operator_review": true
    }
  }
}
```

This sketch is illustrative only and does not change WorkflowSpec, schemas,
canonical JSON, or hashing.

## Compiler Validation Implications

Pattern choice may influence future compiler validation expectations, but
pattern choice itself is not authority.

The compiler still validates the concrete workflow graph, requested
capabilities, and any resulting approval implications.

No pattern proposal can bypass compiler validation.

## Operator Cockpit Implications

If pattern selection is surfaced later, the cockpit should treat it as
display-only operator context.

Pattern display would help explain why a workflow was proposed in a given
shape, but it would not authorize tools, execution, or approvals.

## Borrowed Orchestration Choices, Future Only

Borrowed orchestration choices may inform future cockpit/verifier/audit/status
surfaces only. They do not implement execution.

Future-only display or reporting concepts may include:

- view raw proposed orchestration
- phase list
- agent/node count
- token budget
- elapsed time
- per-phase status
- per-node status
- intermediate result summaries
- concurrency limits
- total-node/agent limits
- loop stop condition
- model/intelligence routing as proposed metadata
- resume/retry status as audit/status metadata

## Replanning And Approval Scope

Replanning must not inherit approval automatically.

Dynamic patterns require recompile/reapproval when requested scope changes.

A revised pattern may change workflow structure, tool needs, concurrency, or
approval implications, so any scope expansion must remain current-run/request
scoped and explicitly re-reviewed.

## Rejected Or Constrained Choices

Reusable workflow definitions may be allowed.

Reusable approvals are not allowed.

Saved workflow templates do not carry approval.

Do not ask again approval semantics are not allowed.

Pattern selection does not authorize tools.

Workflow script execution does not authorize tools.

Model routing does not authorize model access.

Subagent fan-out does not authorize new capabilities.

Replanning must produce a new candidate or revised candidate and must not
inherit approval automatically.

Dynamic patterns require recompile/reapproval when requested scope changes.

## Relationship To Sandbox/Backend Strategy

Workflow-pattern selection is separate from sandbox/backend selection.

Pattern choice describes planning structure.

Sandbox/backend choice describes runtime containment.

Neither pattern choice nor backend choice replaces compiler authorization,
approval scope, artifact identity, or audit/verifier/status semantics.

## Zero-Trust Mapping

This section is design-only mapping language. It does not implement these
controls.

- trust nothing / verify everything / assume breach
- task-scoped permissions -> current-run/request approval scope
- identity -> canonical artifact identity and compiler-owned capability requests
- sandboxing -> delegated to NemoClaw/OpenShell/Kubernetes/backend substrate
- input/output controls -> future verifier/audit/status semantics
- memory poisoning -> future evidence/provenance and planner-input boundaries

## What This Does Not Implement

This design does not implement:

- WorkflowSpec schema changes
- NodeTypeRegistry schema changes
- compiler validation
- canonical JSON
- hashing
- planner behavior
- Hermes Agent integration
- kagent/kagents integration
- Kubernetes integration
- NemoClaw/OpenShell integration
- broker implementation
- sandbox implementation
- real execution
- MCP/tool/connector calls
- model inference
- network behavior
- credentials/secrets behavior
- verifier implementation
- evidence generation
- approval carryover
- reusable approvals
- authority subsumption

## Future Milestones

1. Define design-only pattern metadata without changing current schemas.
2. Decide which patterns can be represented as deterministic compiled
   workflow structures.
3. Define how pattern context appears in operator status without granting
   authority.
4. Require recompile/reapproval whenever dynamic replanning changes requested
   scope.
5. Keep sandbox/backend strategy and workflow-pattern strategy as separate
   design layers.
