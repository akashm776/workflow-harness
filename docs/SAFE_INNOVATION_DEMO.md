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
