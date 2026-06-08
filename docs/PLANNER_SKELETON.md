# Planner Skeleton

This documents the prompt-to-WorkflowSpec planner **skeleton** only. It is a
deterministic stub, not a real planner. It exists to prove the planner-facing
seam without granting any authority or performing any work.

See `planner/workflow_spec_planner.py`.

## What It Is

- `build_stub_planner_candidate(goal: str) -> dict` accepts a plain-text goal and
  returns a deterministic candidate bundle shaped like the existing
  simple-workflow fixture.
- `write_planner_candidate(candidate, output_dir) -> dict` writes only the
  candidate input JSON files (`WorkflowSpec.json`, `RequestedAuth.json`,
  `ApprovalRequests.json`) and returns a manifest of what was written.

The candidate carries the original goal as **non-authoritative metadata only**.
The goal text is never written into the candidate authority-bearing artifacts.

## Deterministic Templates and Selection

Three deterministic templates exist, all non-authoritative proposals:

- `build_stub_planner_candidate(goal)` — the minimal stub (retrieve → synthesize).
- `build_innovation_planner_candidate(goal)` — a deterministic **innovation-agent
  template**: a linear `retrieve`/`synthesize` chain (load program data → gather
  example context → generate idea candidates → score against rubric → synthesize
  MVP plans) with innovation-oriented metadata. It uses only the registered
  `retrieve`/`synthesize` node types and compiles against the existing
  simple-workflow registry. Its `RequestedAuth` is proposal-only and uses
  example-prefixed connector/tool names (e.g. `example-bitbucket`,
  `example-confluence`, `example-issue-tracker`); nothing is called or executed.
- `build_innovation_review_planner_candidate(goal)` - a deterministic richer
  **innovation review template**: a linear `retrieve`/`synthesize` chain (load
  program data -> gather example context -> dedupe against existing work ->
  generate idea candidates -> score against rubric -> critique top ideas ->
  synthesize MVP plans). It also uses only the registered
  `retrieve`/`synthesize` node types and remains proposal-only.

`select_planner_candidate(goal)` chooses the template by **deterministic
whole-word keyword matching** (`innovation`, `idea`, `ideas`, `mvp`) — not by
authority inference and not by any model. Whole-word matching means `ideal` does
not select the innovation template. Unrelated goals fall back to the stub. The
selector returns `(template_name, candidate)`, and `workflow_demo_cli` reports the
chosen `planner_template`.

`workflow_demo_cli` also accepts an explicit `--planner-template` override
(`stub`, `innovation`, or `innovation_review`). This remains deterministic and
non-authoritative: it selects one fixed template explicitly, while the default
keyword-based behavior stays unchanged when the flag is omitted.

This is **not** LLM planning and **not** dynamic node creation: the graphs are
fixed deterministic templates. The raw goal text is never written into the
authority-bearing candidate artifacts.

## Planner Output Is Non-Authoritative

Planner output is **non-authoritative until compiler validation**. Candidate
artifacts are untrusted proposals. They grant no authority and bind nothing. The
deterministic compiler remains the sole authority boundary: only after the
compiler validates and compiles a candidate does any authority-bearing artifact
exist. Nothing in the planner infers, narrows, or grants authority.

A candidate flows through the same governance the compiler applies to any
proposal:

1. Phase 1 authority-value validation (rejects floats / non-finite values).
2. Phase 2 static schema validation (`INVALID_ARTIFACT_SCHEMA`).
3. Phase 3 interpretation validation (graph, scope, approval semantics).

The stub candidate is built to pass these phases against the simple-workflow
`NodeTypeRegistry.json`, but that is a convenience of the stub, not a guarantee
the planner is trusted.

## Explicit Non-Goals

This skeleton intentionally does not:

- call an LLM
- infer or grant real authority
- execute anything
- make tool or connector calls
- write compiled artifacts
- write runtime artifacts (no `ExecutionManifest.json`, no `ExecutionResult.json`)
- implement approval carryover
- implement authority subsumption

`write_planner_candidate` writes only candidate input files. Running the compiler
in `--check` mode over a candidate writes nothing.

## Operator CLI: `planner_check_cli`

`cli/planner_check_cli.py` is an operator-facing wrapper that turns a goal into a
candidate and runs the compiler check against it in one step. It writes only the
candidate input files and never writes compiled, audit, or runtime artifacts.

```text
python -m cli.planner_check_cli --goal "collect and synthesize evidence" --node-type-registry fixtures/valid/simple-workflow/input/NodeTypeRegistry.json --repo-root . --candidate-dir runs/planner-candidate
```

Arguments:

- `--goal` — plain-text goal (carried as non-authoritative metadata only)
- `--node-type-registry` — static governance `NodeTypeRegistry.json` to compile against
- `--repo-root` — repo root the candidate and registry paths resolve under
- `--candidate-dir` — where the candidate input files are written
- `--summary-only` — optional compact output

Default output:

```text
{
  "planner_result": {
    "planner_version": "...",
    "candidate_dir": "...",
    "written": ["WorkflowSpec.json", "RequestedAuth.json", "ApprovalRequests.json"]
  },
  "compile_summary": { ... }
}
```

With `--summary-only`:

```text
{
  "ok": ...,
  "compilation_status": "...",
  "diagnostics": [...],
  "candidate_dir": "..."
}
```

Exit codes: `0` when the compile summary is ok, `1` when it failed. The CLI runs
the compiler's validate/compile path only — the compiler remains the sole
authority boundary, and nothing is executed.

### `--dry-run`

`--dry-run` runs the full goal → candidate → compiler-check flow without leaving
candidate files on disk. The candidate is written only to a temporary directory
that is removed automatically; the requested `--candidate-dir` is **not** created
and no candidate files are written to it. No compiled, audit, or runtime
artifacts are written either. The temporary path is never exposed: the reported
`candidate_dir` is the requested target only, and dry-run output adds
`"dry_run": true`. `--summary-only` works together with `--dry-run`.

```text
python -m cli.planner_check_cli --goal "collect and synthesize evidence" --node-type-registry fixtures/valid/simple-workflow/input/NodeTypeRegistry.json --repo-root . --candidate-dir runs/planner-candidate --dry-run
```

## Determinism

Candidate identifiers are derived deterministically from the goal text (a stable
slug). The same goal always produces the same candidate bundle. This slug is a
convenience identifier only; it is not the canonical artifact hashing and carries
no authority meaning.
