# Safe No-Op Demo Script

Status: demo script only

## Demo Thesis

Most agent demos show capability.
This demo shows controlled capability.

This is a safe-noop governance/control-plane proof, not real agent execution.

## What This Demo Shows

- A planner proposal is non-authoritative.
- The compiler remains the authority boundary.
- Approval is current-run/request scoped.
- Runtime remains safe no-op.
- Operator-facing status surfaces are display-only and do not grant authority.
- Operator Review Notes are display-only, operator-authored, current-run scoped
  notes attached to candidate workflow nodes.
- Operator Review Notes do not approve anything.
- Operator Review Notes do not grant authority.
- Operator Review Notes do not change compiler validation.
- Operator Review Notes do not change approval matching.
- Operator Review Notes do not feed replanning yet.

Current trust boundary:

```text
Planner suggests.
Compiler authorizes.
Operator approves.
Runtime executes only what was compiler-authorized and operator-approved.
Verifier reports.
Audit preserves lineage.
```

## What This Demo Does Not Show

This demo is not real agent execution.
It is not a real broker demo.
It is not a real sandbox demo.
It is not a Hermes Agent integration.
It is not a Kubernetes/kagent integration.
It is not a NemoClaw/OpenShell integration.

No tools, connectors, MCP calls, network calls, model calls, broker calls, or
sandbox execution happen in this demo.

## Prerequisites

- Use the current `main` baseline and the existing safe no-op demo fixtures.
- Present the demo as governance/control-plane behavior over existing artifacts.
- If you inspect run summaries, describe them as operator-facing, display-only
  status surfaces.

## Blocked-Run Demo

Start with the blocked run to show that the governance gate stops the flow
before any real execution claim is possible.

```bash
python -m examples.safe_innovation_demo \
  --run-root runs/manual-review \
  --planner-template innovation_review \
  --allow-overwrite
```

Inspect the blocked run:

```bash
python -m cli.run_status_cli \
  --run-dir runs/manual-review/innovation-demo \
  --summary
```

Call out that the proposal exists, the compiler evaluated it, and the run stays
blocked until the current request is explicitly approved.

## Approved Safe-Noop Demo

Then show the approved safe-noop path. This demonstrates explicit approval for
the current request only, still without real execution.

```bash
python -m examples.safe_innovation_demo \
  --run-root runs/manual-approved \
  --planner-template innovation_review \
  --demo-approve-current-request \
  --allow-overwrite
```

Inspect both output directories:

```bash
python -m cli.run_status_cli \
  --run-dir runs/manual-approved/innovation-demo \
  --summary

python -m cli.run_status_cli \
  --run-dir runs/manual-approved/innovation-approved \
  --summary
```

When presenting the approved path, say clearly that approved still means
completed safe no-op, not a real broker or sandbox execution path.

## Suggested Narration

Use language close to this:

- I am not demoing an agent that can freely use tools.
- I am demoing a control plane that prevents a planner from becoming
  authoritative.
- The planner proposal is non-authoritative.
- The compiler remains the authority boundary.
- Approval is explicit and limited to the current run/request.
- Runtime remains safe no-op.

## Operator Cockpit Talking Points

The summary/operator cockpit can show operator-facing, display-only sections
such as:

- Review Gate
- Candidate Workflow
- Operator Review Notes
- Fixture Lineage
- Proposed Tool Access
- Compiler Authorization Projection
- Approval Binding Summary
- Verifier / Evidence Status
- Broker Boundary Status
- Operator Review Packet
- Governance Lifecycle Stage
- Governance Readiness Checklist

These are display-only status surfaces and do not grant authority.
Operator Review Notes remain operator-authored display-only notes only; they do
not approve anything and do not change compiler validation or approval
matching.

## Expected Claims

These are safe claims to make during the demo:

- The planner proposal is non-authoritative.
- The compiler remains the authority boundary.
- Approval is current-run/request scoped.
- Runtime remains safe no-op.
- The operator cockpit sections are display-only.
- The demo proves governance around proposed capability, not free-form agent
  execution.

## Claims To Avoid

Do not claim any of the following:

- This is real agent execution.
- This integrates Hermes Agent.
- This integrates Kubernetes or kagent.
- This integrates NemoClaw/OpenShell.
- This has a real broker.
- This has a real sandbox.
- This executes tools or connectors.
- This performs MCP calls.
- This performs network calls.
- This performs model inference.
- This implements verifier/evidence generation.
- This supports reusable approvals.
- This supports approval carryover.
- This supports authority subsumption.

## Troubleshooting

- If the blocked run appears first, that is expected and desirable. It shows the
  review gate working.
- If the approved run appears completed, describe it as completed safe no-op
  only.
- If a summary surface shows proposed tools or workflow structure, describe that
  data as display-only and non-authoritative.

## Next Development Step

After this demo script, the next recommended work is a bounded product-facing
development slice over existing artifacts only, such as improving demo/operator
UX without changing compiler authority, approval semantics, broker behavior,
sandbox behavior, schema behavior, canonical JSON, or hashing.
