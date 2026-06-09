# No-Op Broker Boundary Contract

This is design/contract documentation only unless otherwise stated. It defines
the future broker boundary before any code surface is added. It is not an
implementation. No fake/no-op broker interface is implemented by this slice, and
no real broker or sandbox behavior is implemented by this slice.

## Status / Scope

- Design/contract documentation only unless otherwise stated.
- V1 safe no-op has no broker implementation.
- V1 safe no-op has no sandbox implementation.
- V1 safe no-op performs no real execution.
- No fake/no-op broker interface is implemented by this slice.
- No real broker or sandbox behavior is implemented by this slice.

## Future Broker Role

- The broker is a future isolated execution boundary.
- The broker is not an authority boundary.
- The broker must not trust planner output.
- The broker must not consume planner-supplied compiled artifacts.
- The broker may eventually execute only compiler-approved capabilities.
- The broker must require compiler-owned authority artifacts.
- The broker must require explicit approval where required.
- The broker must preserve current-run/request scope.
- The broker must report decisions/results/evidence; it must not invent
  authority.

## Required Future Broker Inputs

- compiler-owned capability envelope / authority artifact
- approval binding / approval subject when required
- run id / request scope
- node id / node type
- side-effect class
- allowed inputs / outputs
- filesystem/network/tool permissions, explicitly denied by default unless
  compiler-authorized
- evidence/audit destination references
- no credentials/secrets in planner output, summaries, logs, or broker request
  payloads

## Required Future Broker Decisions

- permitted / denied / skipped / failed
- deterministic reason code
- effective allowed capability subset
- explicit denied capability list
- sandbox/attestation status where applicable
- no hidden authority expansion

## Required Future Broker Results

- node id / run id / request id
- status
- produced output references
- evidence references
- side effects attempted / denied / completed
- audit references
- errors / fail-closed findings
- no credentials/secrets
- no authority grants

## Authority Boundaries

- A broker decision does not approve anything.
- A broker result does not approve anything.
- A broker decision/result does not override compiler diagnostics.
- A broker decision/result does not override operator approval.
- A broker decision/result does not enable approval carryover.
- A broker decision/result does not enable authority subsumption.
- A broker decision/result does not create reusable authority.
- Future real execution still requires compiler-owned authority plus explicit
  approval where required.

## Display-Only Operator Status (Implemented)

For blocked explicit `innovation_review` runs, `cli.run_status_cli --summary`
renders a display-only `Broker Boundary Status:` section (placed after
`Verifier / Evidence Status:` and before `Operator Review Packet:`). It is
reporting-only and not authority: it reports that V1 safe no-op has no broker
implementation and no sandbox implementation (`broker_request_status`,
`broker_decision_status`, `broker_result_status` all `not_generated`;
`sandbox_status: not_implemented`; `execution_status: safe_noop_only`). It is
**not** a broker, **not** a fake/no-op broker interface, and **not** a sandbox:
it does not generate `BrokerRequest.json`, `BrokerDecision.json`, or
`BrokerResult.json`, reads no future fixtures, writes nothing, grants no
authority, and changes no approval or execution behavior. V1 remains safe no-op
only.

## V1 Non-Goals

- no broker
- no sandbox
- no fake/no-op broker interface
- no real execution
- no MCP/tool/connector calls
- no model inference
- no credentials/secrets
- no network behavior
- no new run artifact writes
- no verifier/evidence generation implementation
- no approval carryover/reusable approvals/authority subsumption
