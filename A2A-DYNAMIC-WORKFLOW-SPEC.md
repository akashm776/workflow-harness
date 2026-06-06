# Project Specification: Deterministic Policy-Governed Dynamic Workflow Harness

## Summary

This system accepts a user prompt, generates a task-specific workflow DAG, validates and compiles authority deterministically, captures run-scoped human governance decisions, and executes only verified compiled nodes.

The implementation is organized around four layers:

1. `Planner Layer`
   - Generates proposal artifacts only.
   - Emits structured workflow, node, task, and requested-authority artifacts.
   - Grants no authority.
2. `Deterministic Governance Layer`
   - Validates graph shape, node semantics, scopes, tools, requested permissions, evidence lineage references, and revision state.
   - Computes review requirements, approval requirements, effective authority, execution bindings, and artifact staleness.
   - Emits the only authority-bearing execution artifacts.
3. `Human Governance Layer`
   - Edits only run-scoped governance artifacts.
   - Adds review gates.
   - Narrows requested access.
   - Approves elevated access on a run-scoped basis.
   - Triggers recompilation when governance inputs change.
4. `Execution Layer`
   - Verifies compiled artifact integrity and staleness before launch.
   - Executes nodes only from compiled bindings.
   - Produces structured evidence, outputs, side-effect manifests, revision history, and audit events.

The compiler and artifact model are the product-critical components. Planner integration is downstream of the governed compile/execute loop.

## Objectives

- Generate dynamic workflow DAGs per task.
- Restrict workflow nodes to a bounded governed node catalog in v1.
- Separate requested authority from effective authority.
- Require deterministic compilation before node execution.
- Support node-level human review and approvals.
- Support content-only reruns, evidence-refresh reruns, and policy-changing reruns.
- Keep audit, evidence, and revision history durable and structured.
- Prevent hidden authority through ambient credentials, undeclared tools, undeclared skills, or undeclared env state.
- Keep markdown non-authoritative.

## Non-Goals For v1

- remote distributed A2A runtime
- arbitrary planner-defined node types
- arbitrary planner-defined permission vocabulary
- natural-language policy interpretation inside the compiler
- authority derived from markdown or freeform notes
- end-to-end determinism of planner behavior, evidence content, or model output quality

## Core Design Rules

- No node runs from planner output.
- No authority is inferred from freeform text.
- No policy-changing rerun may occur without recompilation.
- No evidence-refresh rerun may be treated as content-only.
- No runtime may consume raw planner artifacts for authority decisions.
- No undeclared connector access, tool access, or skill visibility is allowed at runtime.
- No compiled artifact may be modified directly by the TUI.
- All control-plane artifacts are schema-validated JSON.
- `RequestedAuth.json` and `EffectivePolicy.json` are distinct artifacts.
- `ApprovalRequests.json` is the canonical approval-request artifact name.

## Workflow Graph Model

Each run contains a `WorkflowSpec.json` defining a DAG with:

- workflow id
- prompt summary
- graph-only revision id
- workflow revision id
- policy bundle digest
- node list
- node ids
- node types
- directed edges
- entry nodes
- terminal nodes
- optional parallel groups
- merge semantics
- workflow-level constraints
- global run settings
- executable run context summary

### Graph Constraints

- Graph must be acyclic in v1.
- Node ids must be unique.
- All non-entry nodes must declare upstream dependencies.
- Planner may not emit disconnected nodes.
- Fan-out is allowed only from node types marked parallel-capable.
- Merge behavior must be explicit.
- Any `execute` node requiring elevated authority must be downstream of required approval nodes.
- Nodes consuming evidence must reference evidence artifacts and manifests, not arbitrary file paths.
- Graph-shape limits are enforced by workflow-shape policy.

## Bounded Node-Type Catalog

The v1 catalog contains five node types:

- `retrieve`
- `synthesize`
- `critique`
- `approval-gate`
- `execute`

Each node type is defined in `NodeTypeRegistry.json` with:

- type id
- purpose
- allowed connector classes
- allowed tool classes
- allowed side effects
- whether elevated permissions are valid
- whether parallel execution is valid
- output schema family
- evidence behavior
- default review mode
- rerun rules

### Node-Type Semantics

`retrieve`
- Reads governed sources or source metadata.
- Produces `EvidenceArtifact.json` and `EvidenceManifest.json`.
- Read-only only.

`synthesize`
- Produces structured outputs from evidence artifacts.
- May not assume live-source access unless explicitly compiled.

`critique`
- Evaluates artifacts, claims, evidence coverage, and gaps.
- Produces critique artifacts and recommended changes.

`approval-gate`
- Represents required human approval.
- Produces approval records only.

`execute`
- Performs governed side effects such as file writes, ticket creation, or approved command execution.
- Requires compiled authority and approvals where required.

## Authority Model

Authority exists in two separate artifact classes:

- `RequestedAuth.json`
- `EffectivePolicy.json`

`RequestedAuth.json` records requested capabilities. `EffectivePolicy.json` records compiled effective authority.

### Authority Dimensions

Authority is evaluated independently across:

- connector access
- resource scope
- tool execution
- skill visibility
- filesystem access
- side effects
- export behavior
- review requirement
- approval requirement

### Permission Vocabulary

Permissions use a fixed controlled vocabulary, for example:

- `jira.read`
- `jira.write`
- `confluence.read`
- `confluence.write`
- `bitbucket.read`
- `bitbucket.write`
- `sharepoint.read`
- `sharepoint.write`
- `filesystem.read`
- `filesystem.write`
- `shell.execute`
- `web.search`
- `artifact.export`

All scoped permissions must include structured scope.

### Scope Model

Scope is structured, not textual.

Examples:
- Jira: project key, board id, issue type
- Confluence: space key, page id
- Bitbucket: project key, repo slug, ref
- SharePoint: site id, library id, folder path
- Filesystem: run-local absolute path
- Shell: executable allowlist or command family id

If required scope is missing, compilation fails closed.

## Policy Governance

Policy is determined only by deterministic inputs.

### Static Governance Inputs

- `global-policy.json`
- `connector-policy/*.json`
- `tool-policy.json`
- `data-classification-policy.json`
- `workflow-shape-policy.json`
- `NodeTypeRegistry.json`

### Run-Scoped Governance Inputs

- `NodeReviewConfig.json`
- `NodeChangeRequest.json`
- `ApprovalDecisions.json`

### Proposal Inputs

- `WorkflowSpec.json`
- `AgentCard.json`
- `Task.json`
- `RequestedAuth.json`

### Policy Precedence

Precedence is fixed:

1. global denies
2. data-classification restrictions
3. connector restrictions
4. tool restrictions
5. node-type restrictions
6. workflow-shape restrictions
7. run-scoped human narrowing and approvals
8. planner requests only if still valid after prior rules

Planner artifacts never override governance.

## Deterministic Compiler

The compiler performs only deterministic operations:

- schema validation
- graph validation
- node-type validation
- scope validation
- permission classification
- review classification
- approval request generation
- effective policy compilation
- execution binding generation
- compilation reporting
- compiled artifact indexing
- staleness computation

The compiler does not:

- guess missing scope
- infer planner intent
- reinterpret markdown
- auto-broaden permissions

### Compiler Outputs

- `ApprovalRequests.json`
- `EffectivePolicy.json`
- `ExecutionBindings.json`
- `CompilationReport.json`
- `CompiledArtifactIndex.json`

### Compiled Artifact Index

`CompiledArtifactIndex.json` contains:

- workflow revision id
- graph-only revision id
- node revision id
- policy bundle digest
- compiler version
- schema version set
- `EffectivePolicy.json` hash
- `ExecutionBindings.json` hash
- declared input dependency digests
- compile timestamp

## Revision Model

### Workflow Revisions

The system tracks two workflow-level identities:

- `graph_revision_id`
  - increments when graph structure changes
- `workflow_revision_id`
  - includes graph context plus policy bundle digest and executable run context

A new `workflow_revision_id` is created when any of the following change:

- graph structure
- global run settings
- executable run context
- policy bundle digest

A new `graph_revision_id` is created only when graph structure changes.

### Node Revisions

A new `node_revision_id` is created when any node-local artifact or execution-relevant node input changes, including:

- node task content
- node review config
- node change request
- node requested authority
- referenced evidence revision set
- node-local compile-affecting settings

Node-local changes do not create a new workflow revision unless they also change workflow-level revision inputs.

### Compile Revisions

Compiled artifacts are versioned by:

- workflow revision id
- node revision id
- policy bundle digest
- compiler version
- schema version set

## Staleness Model

Compiled artifacts become stale on any change to their declared input dependency set, including:

- proposal inputs
- governance inputs
- policy bundle
- approval decisions
- workflow revision
- node revision
- compiler version
- schema version
- referenced evidence revision set

Staleness requires recompilation before execution. Staleness alone does not imply new human approval.

## Approval Model

### Approval Request Artifact

The canonical approval artifact is `ApprovalRequests.json`.

### Approval Carryover

Approvals bind to a canonical `approval_subject_hash`, not merely a node id.

Approval may carry forward across node revisions only when the approval-subject hash is unchanged.

If authority is narrowed without broadening or ambiguity:

- compiler may carry forward the prior approval
- compiler must emit an audit event documenting carryover

If authority is broadened, changed, or ambiguous:

- a new approval is required

## Human Governance Model

The human may:

- inspect proposal artifacts
- inspect compiled artifacts
- add review to any node
- narrow connectors, scopes, tools, and skills
- request additional grounding sources
- approve elevated access on a run-scoped basis
- request reruns

The human may not:

- directly modify `EffectivePolicy.json`
- directly modify `ExecutionBindings.json`
- bypass mandatory review
- trigger authority changes without recompilation

### Review Modes

Each node is compiled to one of:

- `auto`
- `reviewable`
- `mandatory-review`

The human may strengthen review requirements. The human may not weaken mandatory review without policy change and recompilation.

## Rerun Model

Reruns are typed and revisioned.

### `content-only` rerun

- no authority change
- same effective policy revision
- same pinned evidence artifact set
- new instructions, rubric, or critique only
- node may not refresh, replace, expand, or reinterpret evidence sources

### `evidence-refresh` rerun

- creates new evidence lineage
- cannot be content-only
- may reuse same authority if connector, scope, classification, tool, export, and side-effect authority are unchanged
- if authority remains unchanged, this is not automatically policy-changing, but recompilation is still required because evidence revision inputs changed

### `policy-changing` rerun

- changes requested connectors, scopes, tools, skills, side effects, export behavior, classification exposure, or other authority-bearing dimensions
- requires recompilation
- may require new approval

### Retrieval Query Rule

A changed retrieval query is always evidence-affecting. It creates a new evidence lineage and cannot be content-only.

- same-authority query changes are `evidence-refresh` reruns
- query changes that alter source, scope, connector, classification, tool, export, or side-effect authority are `policy-changing` reruns

### Rerun Artifacts

- `NodeReviewConfig.json`
- `NodeChangeRequest.json`
- `NodeRerunHistory.json`

Every rerun creates a new node revision linked to:

- prior requested auth
- prior effective policy
- prior outputs
- new requested auth
- new effective policy
- review rationale

## Data Governance And Evidence Model

Data governance is first-class.

### Data Classification

Connector resources and evidence artifacts are classified, for example:

- `public`
- `internal`
- `sensitive`
- `restricted`

Classification policy determines:

- which node types may read each class
- when review is mandatory
- whether direct excerpts are allowed
- whether export is allowed
- whether redaction is required

### Evidence Artifacts

Every `retrieve` node produces:

- `EvidenceArtifact.json`
- `EvidenceManifest.json`

Evidence manifest fields:

- evidence id
- source connector
- source identifier
- scope used
- retrieval query
- retrieval time
- classification
- lineage id
- content hash if available

Downstream nodes consume evidence artifacts by reference. They do not refetch live sources by default.

### Evidence Reuse Rule

Content-only reruns pin and reuse the same evidence artifact set.

Any evidence refresh creates new evidence lineage and new evidence revision references.

## Runtime Binding Model

Runtime may consume only:

- `EffectivePolicy.json`
- `ExecutionBindings.json`
- `CompiledArtifactIndex.json`

Runtime may not use proposal artifacts for authority.

### Runtime Requirements

- verify compiled artifact hashes and revisions before start
- reject stale compiled artifacts
- reject undeclared connector env vars
- reject undeclared tools
- reject undeclared skills
- record visible connector bindings
- record visible tool set
- record visible skill set
- enforce output schema family
- emit structured execution results

### v1 Credential Constraint

v1 may rely on host-available connector authentication, but runtime must expose only compiled bindings and must fail if undeclared connector or session material is visible.

## Audit Model

Audit is append-only.

### `AuditLog.jsonl` Events Include

- workflow proposed
- proposal validated
- graph rejected
- approval requested
- approval decided
- approval carried forward
- policy compiled
- bindings generated
- integrity verified
- node started
- node completed
- node failed
- rerun requested
- rerun compiled
- policy delta detected
- evidence lineage changed
- compiled artifact marked stale

Each event includes:

- run id
- graph revision id
- workflow revision id
- node id
- node revision id
- actor type
- timestamp
- relevant artifact references

## Canonical Artifacts

- `WorkflowSpec.json`
- `NodeTypeRegistry.json`
- `AgentCard.json`
- `Task.json`
- `RequestedAuth.json`
- `NodeReviewConfig.json`
- `NodeChangeRequest.json`
- `ApprovalRequests.json`
- `ApprovalDecisions.json`
- `EffectivePolicy.json`
- `ExecutionBindings.json`
- `CompilationReport.json`
- `CompiledArtifactIndex.json`
- `EvidenceArtifact.json`
- `EvidenceManifest.json`
- `ExecutionManifest.json`
- `SideEffectManifest.json`
- `NodeRerunHistory.json`
- `AuditLog.jsonl`

Markdown may exist as a rendered operator view only.

## Directory Structure

```text
workflow-harness/
  policy/
  registry/
  schemas/
  planner/
  compiler/
  runtime/
  tui/
  runs/
```

### `policy/`

```text
policy/
  global-policy.json
  data-classification-policy.json
  tool-policy.json
  workflow-shape-policy.json
  connectors/
```

### `registry/`

```text
registry/
  NodeTypeRegistry.json
```

### `schemas/`

```text
schemas/
  WorkflowSpec.schema.json
  AgentCard.schema.json
  Task.schema.json
  RequestedAuth.schema.json
  NodeReviewConfig.schema.json
  NodeChangeRequest.schema.json
  ApprovalRequests.schema.json
  ApprovalDecisions.schema.json
  EffectivePolicy.schema.json
  ExecutionBindings.schema.json
  CompilationReport.schema.json
  CompiledArtifactIndex.schema.json
  EvidenceArtifact.schema.json
  EvidenceManifest.schema.json
  ExecutionManifest.schema.json
  AuditEvent.schema.json
```

### `runs/<run-id>/`

```text
runs/<run-id>/
  workflow/
  nodes/<node-id>/
  approvals/
  execution/
  audit/
```

## TUI Requirements

The TUI must support:

- workflow graph inspection
- node list inspection
- requested vs effective authority diff
- approval queue inspection
- review-mode editing
- node change request editing
- evidence manifest inspection
- rerun history inspection
- compiled policy inspection
- execution bindings inspection
- audit log inspection

### TUI Write Scope

The TUI may write only:

- `NodeReviewConfig.json`
- `NodeChangeRequest.json`
- `ApprovalDecisions.json`

### TUI Read Scope

The TUI may inspect:

- proposal artifacts
- `ApprovalRequests.json`
- `CompilationReport.json`
- `EffectivePolicy.json`
- `ExecutionBindings.json`
- evidence manifests
- execution manifests
- audit logs

## Acceptance Criteria

The system is complete when all are true:

- planner emits a valid DAG using only registered node types
- compiler rejects unknown node types
- compiler rejects vague scopes
- compiler rejects illegal graph shapes
- retrieve nodes cannot obtain write authority
- execute nodes cannot run without required approvals
- no compiled artifact is mutated by the TUI
- any authority change creates a new effective policy revision
- runtime verifies hash and revision continuity before execution
- runtime fails on undeclared sensitive env visibility
- connector access is bindings-scoped only
- evidence manifests exist for every retrieval node
- policy-changing reruns require recompilation
- evidence-refresh reruns create new evidence lineage
- content-only reruns preserve prior effective policy revision and pinned evidence set
- audit log explains proposal, approval, compile, execution, and revision lineage

## Implementation Sequence

1. artifact schemas
2. node registry
3. deterministic compiler core
4. effective policy and bindings generation
5. revision model and staleness engine
6. runtime verifier
7. evidence artifacts and manifests
8. TUI approval and governance loop
9. hand-authored `WorkflowSpec.json` compile/execute proof
10. planner integration

Planner integration occurs after the compiler/runtime governance loop is proven with hand-authored artifacts.

## Test Plan

- hand-authored workflow compiles and executes from compiled artifacts only
- planner generates valid DAG from prompt
- planner emits unknown node type and compiler rejects
- planner emits missing scope for scoped permission and compiler rejects
- planner emits illegal cycle and compiler rejects
- retrieve node requests `bitbucket.write` and compiler denies
- execute node requests `shell.execute` and compiler emits approval request
- human narrows connector scope and compiler emits narrower effective policy
- human adds new data source and rerun is classified evidence-refresh or policy-changing per rules
- content-only rerun reuses policy revision and pinned evidence set
- changed retrieval query is classified evidence-refresh, never content-only
- approval carries forward only when approval-subject hash is unchanged
- approval carry-forward emits audit event
- runtime rejects stale `CompiledArtifactIndex.json`
- runtime rejects mismatched `EffectivePolicy.json` hash
- runtime rejects mismatched `ExecutionBindings.json` hash
- runtime rejects artifact set compiled against older schema/compiler versions when declared stale
- runtime detects undeclared connector env var and aborts
- connector adapter rejects out-of-scope request at runtime
- evidence manifest lineage is recorded and consumed downstream
- audit log records approval-request -> approval-decision -> recompile cycle

## Assumptions

- workflow graphs are DAGs in v1
- node types are bounded in v1
- compiler is deterministic code only
- approvals are run-scoped only
- JSON is canonical
- markdown is non-authoritative
- runtime is local in v1
- authority compilation is deterministic; planner behavior and output quality are not

## Diagram Files

- See `architecture-authority-flow.puml` for the trust and execution authority flow.
- See `architecture-artifact-audit.puml` for artifact ownership, revisioning, and audit lineage.
