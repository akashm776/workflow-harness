# Evidence Lineage / Verifier Output Contract

This is design/contract documentation only unless otherwise stated. It describes
the future evidence-lineage and verifier-output reporting contract before any
implementation writes new artifacts. It is not an implementation. V1 safe no-op
does not generate or consume future evidence lineage artifacts yet, and does not
generate or consume future verifier output artifacts yet.

## Status / Scope

- Design/contract documentation only unless otherwise stated.
- V1 safe no-op does not generate or consume future evidence lineage artifacts
  yet.
- V1 safe no-op does not generate or consume future verifier output artifacts
  yet.
- Runtime remains safe no-op.
- Verifier output is reporting only.
- Evidence lineage is reporting only.

## Ownership

- Planner may not supply verifier output as authority.
- Planner may not supply evidence lineage as authority.
- Compiler remains the authority boundary.
- Runtime/verifier may report observations but cannot invent authority.
- Operator approval remains explicit and current-run/request scoped.

## Future Evidence Lineage Reporting

Future evidence lineage should bind/report (reporting only, never authority):

- current run id / run directory context
- workflow/candidate identity where available
- workflow revision / graph revision / artifact digest where available
- node id / node type where relevant
- approval request / approval subject hash where relevant
- compiler diagnostics where relevant
- execution/broker decision references only after a future broker exists
- produced outputs / evidence references, not ambient authority

## Future Verifier Output Reporting

Future verifier output should report (reporting only, never authority):

- checks performed
- inputs observed
- expected vs observed status
- evidence references
- audit / event references
- fail-closed findings
- unverifiable or missing evidence as explicit unknown/failed states

## Authority Boundaries

- Verifier output does not authorize execution.
- Evidence lineage does not authorize execution.
- Verifier output does not approve anything.
- Evidence lineage does not approve anything.
- Verifier output does not grant capabilities.
- Evidence lineage does not grant capabilities.
- Neither can override compiler diagnostics.
- Neither can override operator approval.
- Neither enables approval carryover.
- Neither enables authority subsumption.
- Neither creates reusable authority.
- Future broker/sandbox execution still requires compiler-owned authority plus
  explicit approval where required.

## V1 Non-Goals

- no real execution
- no broker/sandbox
- no MCP/tool/connector calls
- no model inference
- no credentials/secrets
- no network behavior
- no new run artifact writes
- no verifier implementation
- no evidence generation implementation
