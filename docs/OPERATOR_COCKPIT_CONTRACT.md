# Operator Cockpit Contract

This is the current contract documentation for the V1 safe no-op operator
cockpit: the display-only governance sections rendered by
`cli.run_status_cli --summary` for blocked explicit `innovation_review` runs. It
records the current section order and safety boundary before any pure broker
data-shape module or future broker-related code surface is added.

## Status / Scope

- Current contract documentation for the V1 safe no-op operator cockpit.
- V1 remains safe no-op only.
- No real execution.
- No tools/connectors/MCP/network/model/broker/sandbox behavior.
- Display-only / read-only reporting unless otherwise stated.
- No new artifacts are written by the rich summary.

## Applicability

- Applies to blocked explicit `innovation_review` rich summaries.
- Governance Readiness Checklist may also appear when existing summary fields
  ground a non-unknown lifecycle state for a run summary.
- Default / non-rich / generic summaries are not required to show the full
  cockpit.
- Approved runs do not show blocked-review cockpit sections unless existing
  behavior already does so.
- The cockpit is operator guidance only.

## Related Preview Helpers

- `python -m cli.workflow_strategy_preview_cli` is a deterministic,
  display-only workflow proposal strategy preview helper.
- It uses deterministic keyword matching only as a baseline preview and audit
  scaffold for future LLM/Hermes workflow selection.
- The future planner LLM/Hermes may choose different workflow strategies or
  pattern families using richer context.
- The preview does not replace intelligent workflow planning.
- Any future intelligent selection must still produce
  compiler-validatable candidate artifacts and remain subject to current-run
  operator approval.
- It previews strategy type, pattern family, expected phases, expected future
  candidate artifacts, and expected governance surfaces.
- It is planner-side only and is not a current run-status summary section or
  run artifact.
- It does not create candidate artifacts.
- It does not authorize anything.
- It does not approve anything.
- It does not execute anything.
- It does not create a broker request.
- It does not launch a sandbox/backend.
- It does not call models, tools, connectors, MCP, network, broker, sandbox,
  compiler, runtime, or planner artifact-generation APIs.
- It does not change compiler validation.
- It does not change approval matching.
- Compiler validation remains required before approval/runtime surfaces.

## Current Section Order

```text
Review Gate:
Compiler Governance Timeline:
Broker Handoff Readiness Preview:
Approved Capability Handoff Projection:
Governance Lifecycle Stage:
Governance Readiness Checklist:
Candidate Workflow:
Operator Review Notes:
Fixture Lineage:
Proposed Tool Access:
Compiler Authorization Projection:
Approval Binding Summary:
Verifier / Evidence Status:
Broker Boundary Status:
Operator Review Packet:
```

## Section Responsibilities

- **Review Gate:** blocked review status and current approval requirement.
- **Compiler Governance Timeline:** display-only timeline of observed/local
  governance status derived only from existing local run artifacts and summary
  facts. It does not authorize anything. It does not approve anything. It does
  not change compiler validation. It does not change approval matching. It does
  not execute tools, connectors, brokers, sandboxes, MCP, network calls, or
  model calls.
- **Broker Handoff Readiness Preview:** display-only local artifact readiness
  preview for a future broker contract layer only. It reports what local
  candidate/approval artifacts still appear missing before a future
  broker/sandbox handoff could safely be contracted. It does not create a
  broker request. It does not launch a sandbox/backend. It does not authorize
  anything. It does not approve anything. It does not execute anything. It does
  not change compiler validation. It does not change approval matching. It does
  not call tools, connectors, MCP, network, broker, sandbox, or model APIs.
- **Approved Capability Handoff Projection:** display-only local current-run
  request/node projection for a future broker contract layer only. It reports
  which current-run approval requests have matching local approved decisions and
  which remain blocked from that future contract layer. It does not authorize
  anything. It does not approve anything. It does not execute anything. It does
  not create a broker request. It does not launch a sandbox/backend. It does
  not change compiler validation. It does not change approval matching. It does
  not create reusable approvals. It does not create approval carryover. It does
  not call tools, connectors, MCP, network, broker, sandbox, or model APIs.
- **Governance Lifecycle Stage:** display-only projection of where the run sits
  in the governed workflow flow and the next safe operator action, derived only
  from existing status fields (`compilation_status`, `execution_status`,
  `review_required`, `blocked_by_review`). Stages are a small fixed vocabulary
  (`compiled_no_review_required`, `blocked_awaiting_operator_approval`,
  `completed_safe_noop`, `compile_failed`, `unknown`). It is not authoritative,
  loads no new artifacts, and grants nothing.
- **Governance Readiness Checklist:** display-only checklist derived from
  existing run-status summary fields and already-built summary projections. It
  grants no authority. It creates no approvals. It does not bind approvals. It
  does not authorize execution. It does not implement broker, sandbox,
  verifier, or evidence behavior. It compactly reports what is satisfied,
  missing, blocked, or inspect-only from already-known status facts only.
- **Candidate Workflow:** display-only candidate graph summary.
- **Operator Review Notes:** display-only, operator-authored, current-run scoped
  notes attached to candidate workflow nodes. They are not a control-plane
  artifact, not compiler input, and not approval data. They do not approve
  anything. They do not grant authority. They do not change compiler
  validation. They do not change approval matching. They do not feed
  replanning yet. They may be written locally with
  `python -m cli.operator_review_notes_cli`, which writes
  `candidate/OperatorReviewNotes.json` for the current run only.
- **Fixture Lineage:** display-only future fixture path lineage, not fixture
  loading.
- **Proposed Tool Access:** display-only requested tool/connector proposal data.
- **Compiler Authorization Projection:** display-only requested / approval-required
  / blocked / unsupported authority view.
- **Approval Binding Summary:** display-only current-run/request approval binding
  explanation, not approval logic.
- **Verifier / Evidence Status:** display-only safe no-op artifact presence and
  evidence/verifier status, not verifier output or evidence lineage generation.
- **Broker Boundary Status:** display-only statement that no broker/sandbox/artifacts
  exist in V1.
- **Operator Review Packet:** display-only section inventory and review packet
  summary.

## Authority Boundary

- Planner remains non-authoritative.
- Compiler remains the sole authority boundary.
- Operator approval remains explicit and current-run/request scoped.
- Runtime remains safe no-op.
- Compiler Governance Timeline is display-only.
- Compiler Governance Timeline reports observed/local governance status only.
- Compiler Governance Timeline does not authorize anything.
- Compiler Governance Timeline does not approve anything.
- Compiler Governance Timeline does not change compiler validation.
- Compiler Governance Timeline does not change approval matching.
- Compiler Governance Timeline does not execute tools, connectors, brokers,
  sandboxes, MCP, network calls, or model calls.
- Broker Handoff Readiness Preview is display-only.
- Broker Handoff Readiness Preview reports local artifact readiness for a
  future broker contract only.
- Broker Handoff Readiness Preview does not create a broker request.
- Broker Handoff Readiness Preview does not launch a sandbox/backend.
- Broker Handoff Readiness Preview does not authorize anything.
- Broker Handoff Readiness Preview does not approve anything.
- Broker Handoff Readiness Preview does not execute anything.
- Broker Handoff Readiness Preview does not change compiler validation.
- Broker Handoff Readiness Preview does not change approval matching.
- Broker Handoff Readiness Preview does not call tools, connectors, MCP,
  network, broker, sandbox, or model APIs.
- Approved Capability Handoff Projection is display-only.
- Approved Capability Handoff Projection reports local current-run approved
  request/node pairs for a future broker contract layer only.
- Approved Capability Handoff Projection does not authorize anything.
- Approved Capability Handoff Projection does not approve anything.
- Approved Capability Handoff Projection does not execute anything.
- Approved Capability Handoff Projection does not create a broker request.
- Approved Capability Handoff Projection does not launch a sandbox/backend.
- Approved Capability Handoff Projection does not change compiler validation.
- Approved Capability Handoff Projection does not change approval matching.
- Approved Capability Handoff Projection does not create reusable approvals.
- Approved Capability Handoff Projection does not create approval carryover.
- Approved Capability Handoff Projection does not call tools, connectors, MCP,
  network, broker, sandbox, or model APIs.
- The verifier/evidence/broker status sections do not authorize, approve, grant
  capabilities, or execute.
- Operator Review Notes are display-only and operator-authored.
- Operator Review Notes are current-run scoped notes attached to candidate
  workflow nodes.
- `python -m cli.operator_review_notes_cli` writes local operator-authored
  display-only notes for the current run only.
- Operator Review Notes do not approve anything.
- Operator Review Notes do not grant authority.
- Operator Review Notes do not change compiler validation.
- Operator Review Notes do not change approval matching.
- Operator Review Notes do not feed replanning yet.
- `python -m cli.operator_approval_decisions_cli` writes a local
  current-run/request-scoped `ApprovalDecisions.json` artifact only.
- Operator approval decision CLI does not authorize by itself.
- Operator approval decision CLI does not change compiler validation.
- Operator approval decision CLI does not change approval matching.
- Operator approval decision CLI does not create reusable approvals.
- Operator approval decision CLI does not create approval carryover.
- Operator approval decision CLI does not execute anything.
- Operator approval decision CLI does not call tools, connectors, MCP, network,
  broker, sandbox, or model APIs.
- Summary sections do not override compiler diagnostics.
- Summary sections do not override operator approval.
- Governance Readiness Checklist is display-only.
- Governance Readiness Checklist is derived from existing run-status summary
  fields.
- Governance Readiness Checklist grants no authority.
- Governance Readiness Checklist creates no approvals.
- Governance Readiness Checklist does not bind approvals.
- Governance Readiness Checklist does not authorize execution.
- Governance Readiness Checklist does not implement broker, sandbox, verifier,
  or evidence behavior.
- Summary sections do not enable approval carryover.
- Summary sections do not enable authority subsumption.
- Summary sections do not create reusable authority.

## Input / Read Boundary

- The rich summary reads only existing local run/candidate artifacts already used
  by the current status model.
- No future fixtures are read.
- No future fixtures become control-plane inputs.
- No external systems are called.
- No credentials/secrets are read.
- No network behavior.

## V1 Non-Goals

- no real execution
- no broker/sandbox
- no fake/no-op broker interface
- no MCP/tool/connector calls
- no model inference
- no verifier implementation
- no evidence generation implementation
- no approval carryover/reusable approvals/authority subsumption
- no canonical JSON/hashing changes
