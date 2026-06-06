# Safe Innovation Demo

A short, runnable walkthrough of the current product loop in **safe no-op mode**.
It generates a deterministic innovation-agent candidate from a goal, compiles it,
runs the safe no-op path, and inspects the result. No real execution happens.

See also [`PLANNER_SKELETON.md`](PLANNER_SKELETON.md) (the deterministic planner
and template selection) and [`V1_SAFE_NOOP_HARNESS.md`](V1_SAFE_NOOP_HARNESS.md)
(the full safe no-op operator surface).

## Two Commands

Run the demo into a self-contained run directory:

```text
python -m cli.workflow_demo_cli --goal "generate innovation ideas from program data" --node-type-registry fixtures/valid/simple-workflow/input/NodeTypeRegistry.json --repo-root . --run-dir runs/innovation-demo
```

Inspect the produced run with the opt-in read-only summary:

```text
python -m cli.run_status_cli --run-dir runs/innovation-demo --summary
```

## Expected Result

- The demo selects the innovation template: `planner_template: "innovation"`
  (the goal matches the whole-word keyword `innovation`/`ideas`).
- The candidate compiles: `compilation_status: compiled`.
- The no-op run is blocked: `execution_status: blocked`. This is expected when
  approval/review is required and no approval decision is supplied — the
  innovation candidate requests authority, so the compiler requires review, and
  without an approval decision the safe runtime does not proceed.
- **blocked is expected and safe.** It demonstrates the governance gate working:
  the run is a complete safe no-op run, with the manifest, no-op result, and audit
  log all written, but no work is performed.

The summary also shows the selected candidate workflow graph (read from the local
candidate proposal for **display only** — not validation and not authority):

```text
Candidate Workflow:
- retrieve-1 [retrieve] Load Program Data
  -> retrieve-2
- retrieve-2 [retrieve] Gather Example Context
  -> synthesize-1
- synthesize-1 [synthesize] Generate Idea Candidates
  -> synthesize-2
- synthesize-2 [synthesize] Score Against Rubric
  -> synthesize-3
- synthesize-3 [synthesize] Synthesize MVP Plans
```

## Safety Boundary

This walkthrough stays inside the safe boundary:

- **no real execution** occurs.
- **no tools** and **no connectors** are called; nothing contacts Jira,
  Confluence, Bitbucket, MCP, or the network. The candidate's `RequestedAuth` uses
  example-prefixed names and is a proposal only.
- planner output remains **non-authoritative** until the compiler validates it.
- the compiler remains the **sole authority boundary**.
- the runtime remains **safe no-op only**.

The `--summary` surface is read-only and fail-soft: it parses known local run
artifacts to report status and writes nothing.

## Explicit Approval Decision Demo

The blocked run above can be carried to a **completed safe no-op** by supplying an
**explicit** approval decision for this run's request — still with no real
execution. The flow composes existing commands; nothing is auto-approved.

1. Run the innovation demo (as above). It blocks because review/approval is
   required and no approval decision was supplied.
2. Inspect the generated approval request to find the `request_id`:

   ```text
   cat runs/innovation-demo/candidate/ApprovalRequests.json
   ```

3. Create an explicit `ApprovalDecisions.json` approving that exact `request_id`
   (use the `workflow_revision_id` from the same artifact):

   ```text
   {
     "schema_version": "m1",
     "workflow_revision_id": "<from ApprovalRequests.json>",
     "artifact_lifecycle_state": "completed",
     "decisions": [
       {
         "request_id": "<from ApprovalRequests.json>",
         "decision": "approved",
         "approved_by": "operator",
         "approved_at": "2026-06-06T00:00:00Z"
       }
     ]
   }
   ```

   Save it as `runs/innovation-demo/ApprovalDecisions.json`.

4. Rerun the safe no-op path over the same candidate, supplying the decision:

   ```text
   python -m cli.safe_run_cli --workflow-spec runs/innovation-demo/candidate/WorkflowSpec.json --node-type-registry runs/innovation-demo/NodeTypeRegistry.json --requested-auth runs/innovation-demo/candidate/RequestedAuth.json --approval-requests runs/innovation-demo/candidate/ApprovalRequests.json --approval-decisions runs/innovation-demo/ApprovalDecisions.json --repo-root runs/innovation-demo --output-dir runs/innovation-approved --node-id retrieve-1
   ```

5. Inspect the approved output run:

   ```text
   python -m cli.run_status_cli --run-dir runs/innovation-approved --summary
   ```

   The approved run reports `execution_status: completed`.

### What This Demonstrates

- Approval is **explicit** and applies to the **current run/request only**.
- There is **no approval carryover**, **no authority subsumption**, and **no
  inferred approval** — the decision must match the request's `request_id`.
- `completed` here still means a **completed safe no-op** only: no real execution
  occurs, and no tools/connectors (Jira, Confluence, Bitbucket, MCP, network) are
  called.
- The approved `ExecutionResult.json` still has `side_effects == []` and
  `produced_evidence == []`.

### One-Command Example Wrapper

For convenience, `examples/safe_innovation_demo.py` runs the whole flow. It is an
**example script, intentionally outside `cli/`** — it can write a demo-local
`ApprovalDecisions.json`, so it is kept out of the core CLI surface to avoid
implying a supported general auto-approval path.

No-approval mode (blocked only; writes no approval decision):

```text
python -m examples.safe_innovation_demo --run-root runs
```

Approval-demo mode (blocked, then explicit demo-local approval, then completed):

```text
python -m examples.safe_innovation_demo --run-root runs --demo-approve-current-request
```

Any approval it generates is **demo-local only**, applies to the **current
run/request only**, and is **not a general auto-approval mechanism**. It still
performs no real execution, calls no tools/connectors, implements no approval
carryover and no authority subsumption, and `completed` means a completed safe
no-op.
