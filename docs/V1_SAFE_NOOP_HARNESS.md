# V1 Safe No-Op Harness

## Current Scope

The current harness provides a deterministic, operator-facing no-op workflow path.
It composes:

- `safe_noop_run(...)`
- `cli/safe_run_cli.py`
- static compilation
- compiled artifact writing
- runtime bundle loading
- runtime start verification
- append-only audit log writing
- `ExecutionManifest.json` creation
- no-op execution
- `ExecutionResult.json` writing

The intended use is to prove the control-plane artifact flow without performing
real tool execution, connector calls, or side effects.

Examples assume commands are run from the repository root. On Windows, `py -m ...`
may also be used if `python` is not on PATH.

Current CLI hardening options:

- `--summary-only`
- `--dry-run`
- `--check`

## What It Currently Does

- Validates static workflow inputs and approval request shape
- Builds deterministic compiler artifacts
- Writes compiled artifacts to an output bundle
- Loads only runtime-consumed compiled artifacts
- Verifies whether a node may start from compiled state
- Emits orchestration audit events to `AuditLog.jsonl`
- Writes `ExecutionManifest.json` for approved and blocked non-failed runs
- Produces a no-op `ExecutionResult.json`

## What It Intentionally Does Not Do

- No real execution
- No tool calls
- No connector calls
- No runtime side effects
- No policy evaluation beyond the current skeleton
- No approval carryover
- No narrowed-authority reuse
- No leases or lifecycle FSM enforcement
- No broader staleness logic
- No full TUI framework; only dependency-free status view text exists

## Artifact Flow

```text
WorkflowSpec.json
NodeTypeRegistry.json
RequestedAuth.json
ApprovalRequests.json
ApprovalDecisions.json (optional)
        |
        v
compile_static_artifacts(...)
        |
        +--> CompilationReport.json
        +--> CompiledArtifactIndex.json
        +--> EffectivePolicy.json (only on successful compile)
        +--> ExecutionBindings.json (only on successful compile)
        |
        v
safe_noop_run(...)
        |
        +--> AuditLog.jsonl
        +--> ExecutionManifest.json (only when compile succeeded)
        +--> ExecutionResult.json (only when an execution manifest exists)
```

## CLI Examples

Approved workflow:

```text
python -m cli.safe_run_cli --workflow-spec fixtures/valid/simple-workflow/input/WorkflowSpec.json --node-type-registry fixtures/valid/simple-workflow/input/NodeTypeRegistry.json --requested-auth fixtures/valid/simple-workflow/input/RequestedAuth.json --approval-requests fixtures/valid/simple-workflow/input/ApprovalRequests.json --repo-root . --output-dir runs/simple-approved --node-id retrieve-1
```

Unapproved workflow:

```text
python -m cli.safe_run_cli --workflow-spec fixtures/valid/simple-workflow/input/WorkflowSpec.json --node-type-registry fixtures/valid/simple-workflow/input/NodeTypeRegistry.json --requested-auth fixtures/valid/simple-workflow/input/RequestedAuth.json --approval-requests fixtures/valid/simple-workflow/input/ApprovalRequests.json --approval-decisions fixtures/valid/simple-workflow/input/ApprovalDecisions-empty.json --repo-root . --output-dir runs/simple-unapproved --node-id retrieve-1
```

Failed compile:

```text
python -m cli.safe_run_cli --workflow-spec fixtures/invalid/unknown-node-type/input/WorkflowSpec.json --node-type-registry fixtures/invalid/unknown-node-type/input/NodeTypeRegistry.json --requested-auth fixtures/invalid/unknown-node-type/input/RequestedAuth.json --approval-requests fixtures/invalid/unknown-node-type/input/ApprovalRequests.json --repo-root . --output-dir runs/unknown-node-type --node-id retrieve-1
```

Check-only compile:

```text
python -m cli.safe_run_cli --workflow-spec fixtures/valid/simple-workflow/input/WorkflowSpec.json --node-type-registry fixtures/valid/simple-workflow/input/NodeTypeRegistry.json --requested-auth fixtures/valid/simple-workflow/input/RequestedAuth.json --approval-requests fixtures/valid/simple-workflow/input/ApprovalRequests.json --repo-root . --output-dir runs/check-only --node-id retrieve-1 --check
```

Run status inspection:

```text
python -m cli.run_status_cli --run-dir runs/simple-approved
```

Run status inspection in text mode:

```text
python -m cli.run_status_cli --run-dir runs/simple-approved --text
```

Run status inspection in view mode:

```text
python -m cli.run_status_cli --run-dir runs/simple-approved --view
```

End-to-end demo (goal to safe no-op run):

```text
python -m cli.workflow_demo_cli --goal "generate innovation ideas from program data" --node-type-registry fixtures/valid/simple-workflow/input/NodeTypeRegistry.json --repo-root . --run-dir runs/workflow-demo
```

`workflow_demo_cli` composes the deterministic planner candidate, the compiler,
and the safe no-op run into one operator loop. It writes a **self-contained safe
bundle** under `--run-dir` (candidate inputs under `<run-dir>/candidate` and a
copied `NodeTypeRegistry.json`), compiles and runs with
`effective_repo_root == run_dir`, and prints a `python -m cli.run_status_cli
--run-dir <run-dir> --view` command to inspect the result. It performs **no real
execution** and may produce `execution_status: "blocked"` when review/approval is
required and no approval decision is supplied.

## CLI Modes

- Default mode runs the full safe no-op orchestration path.
- `cli.workflow_demo_cli` runs the goal -> candidate -> compile -> safe no-op
  demo loop into a self-contained `--run-dir`; no real execution.
- `--summary-only` prints a compact operator summary instead of the full nested result.
- `--dry-run` compiles and summarizes only. It writes nothing.
- `--check` prints only `{ ok, compilation_status, diagnostics }`. It writes nothing.
- `cli.run_status_cli` is read-only and checks artifact existence only.
- Default `cli.run_status_cli` output is canonical JSON.
- `cli.run_status_cli --text` emits simple human-readable status.
- `cli.run_status_cli --view` emits future TUI-shaped screen text.

## Exit Codes

- `0` when compile succeeds
- `1` when compile fails
- `cli.run_status_cli` returns `0` when `complete_safe_noop_run` is true
- `cli.run_status_cli` returns `1` otherwise

## Emitted Files

Approved workflow emits:

- `CompilationReport.json`
- `CompiledArtifactIndex.json`
- `EffectivePolicy.json`
- `ExecutionBindings.json`
- `AuditLog.jsonl`
- `ExecutionManifest.json`
- `ExecutionResult.json`

Unapproved workflow emits:

- `CompilationReport.json`
- `CompiledArtifactIndex.json`
- `EffectivePolicy.json`
- `ExecutionBindings.json`
- `AuditLog.jsonl`
- `ExecutionManifest.json`
- `ExecutionResult.json`

Failed compile emits:

- `CompilationReport.json`
- `CompiledArtifactIndex.json`
- `AuditLog.jsonl`

## Current Safety Boundaries

- No real execution
- No tools or connectors
- Runtime artifacts are not included in `CompiledArtifactIndex.json`
- Approvals do not carry over between runs
- No policy evaluation beyond the current skeleton
- Runtime start depends on compiled artifacts only
- `--dry-run` and `--check` do not write compile bundles, audit logs, manifests, or execution results
- `inspect_run_directory(...)` and `cli.run_status_cli` do not read or validate JSON contents
- `render_run_status_text(...)` is a pure renderer and does not mutate the status input
- `render_run_status_view(...)` is a pure renderer and does not mutate the status input
