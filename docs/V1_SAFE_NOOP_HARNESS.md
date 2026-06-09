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

Run status inspection in opt-in summary mode:

```text
python -m cli.run_status_cli --run-dir runs/simple-approved --summary
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

The summary reports the selected `planner_template`. Innovation/idea/MVP prompts
(whole-word keyword match) select the deterministic innovation template; other
goals use the stub template. An explicit `--planner-template innovation_review`
selects a richer deterministic review chain only when requested; default
goal-based selection remains unchanged, and existing `innovation` behavior
remains unchanged. The `innovation_review` template uses only the existing
`retrieve` and `synthesize` node types, compiles against the simple registry,
and adds deterministic proposal stages for dedupe against existing work,
generating idea candidates, scoring against a rubric, critiquing top ideas, and
synthesizing MVP plans. Blocked `innovation_review` runs still require explicit
current-run/request-only approval, remain safe no-op only, and `cli.run_status_cli
--summary` shows both `Candidate Workflow:` and `Review Gate:`. The example
wrapper can pass through `--planner-template innovation_review`, but its default
remains the existing safe innovation demo behavior. All templates remain
deterministic proposals only: no LLM planning, no real tools/connectors, no
sandbox, and no real execution.

The repository also includes `examples/safe_innovation_demo.py`, an example-only
wrapper kept out of `cli/`. It composes the blocked safe innovation demo path,
and optionally a demo-local explicit approval path, without creating a general
approval helper.

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
- The default `inspect_run_directory(...)`, default `cli.run_status_cli`,
  `--text`, and `--view` remain existence-only and unchanged.
- `cli.run_status_cli --summary` is a separate opt-in, read-only surface that
  parses known local artifacts fail-soft to show compile/execution status,
  review-required, blocked-by-review, candidate-dir presence, artifact rows, and
  a status command. When `<run-dir>/candidate/WorkflowSpec.json` exists it also
  shows an optional `Candidate Workflow:` section (node IDs, node types, display
  names, and edges) read from the local candidate proposal for display only. It
  reads only known local artifacts, writes nothing, calls no tools/connectors,
  performs no execution, and grants no authority. It does not validate artifacts
  or confer authority. The default `cli.run_status_cli` (default JSON, `--text`,
  `--view`) remains existence-only and unchanged.
- For explicit `innovation_review` proposals, `cli.run_status_cli --summary`
  also renders a display-only `Fixture Lineage:` section listing known future
  fixture paths under `fixtures/future/innovation-context/`. It is derived from
  already-read candidate workflow metadata only, does not load fixture
  contents, does not make fixtures control-plane inputs, remains fail-soft and
  operator-facing only, and grants no authority.
- For explicit `innovation_review` proposals, `cli.run_status_cli --summary`
  also renders a display-only `Proposed Tool Access:` section derived from the
  local candidate `RequestedAuth.json` proposal only. It remains proposal-only,
  does not execute tools, does not enable connector support, does not change
  approval semantics, remains fail-soft and operator-facing only, and grants no
  authority.
- For blocked explicit `innovation_review` proposals, `cli.run_status_cli
  --summary` also renders a display-only `Approval Binding Summary:` section,
  placed after `Compiler Authorization Projection:` and before `Operator Review
  Packet:`. It explains, for the current blocked request only, what an approval
  would bind to: it is display-only, operator-owned, not reusable authority, has
  no approval carryover, grants no runtime authority, and is current
  run/request scope only. It is derived only from already-read local run data
  (the candidate workflow identity, `candidate/ApprovalRequests.json` read
  fail-soft, and existing `CompilationReport.json` diagnostics), reports approval
  `request_id`/`node_id`/`approval_subject_hash` where available with fail-soft
  unknowns, and surfaces any `UNSUPPORTED_APPROVAL_BINDING` diagnostic already
  present. It does not change approval resolution or matching, implements no real
  approval binding, approval carryover, or reusable approvals, writes nothing,
  and grants no authority.
- When a safe no-op run is blocked by review, `cli.run_status_cli --summary`
  also renders a display-only `Operator Review Packet:` checklist derived only
  from already-computed summary fields such as `review_required`,
  `blocked_by_review`, `review_gate`, `candidate_workflow`,
  `fixture_lineage`, and `proposed_tool_access`. It is operator-facing only,
  not a new artifact, not approval logic, not execution behavior, and it grants
  no authority.
- When a safe no-op run is blocked by review, `cli.run_status_cli --summary`
  also renders a display-only `Review Gate:` section. It reads
  `candidate/ApprovalRequests.json` fail-soft for operator guidance only, does
  not validate approval semantics, and does not approve anything. Unblocking
  still requires an explicit matching `ApprovalDecisions.json` for the current run/request only.

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
- No MCP/network calls
- No sandbox/broker implementation
- Runtime artifacts are not included in `CompiledArtifactIndex.json`
- Approvals do not carry over between runs
- No policy evaluation beyond the current skeleton
- Runtime start depends on compiled artifacts only
- Compiler validation rejects unsupported node-level tool/connector/broker/MCP
  execution intent with `UNSUPPORTED_EXECUTION_BINDING`
- `--dry-run` and `--check` do not write compile bundles, audit logs, manifests, or execution results
- `inspect_run_directory(...)` and the default `cli.run_status_cli` (default JSON,
  `--text`, `--view`) do not read or validate JSON contents (existence-only)
- `cli.run_status_cli --summary` is the only status path that reads JSON; it is
  read-only and fail-soft, writes nothing, and validates nothing
- `render_run_status_text(...)` is a pure renderer and does not mutate the status input
- `render_run_status_view(...)` is a pure renderer and does not mutate the status input
