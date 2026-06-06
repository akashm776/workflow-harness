# Milestone Status

## Current Milestone

`V1 Safe No-Op Harness`

## Test Status

- `389 tests` passing

## Major Implemented Layers

- `M1` contracts
- `M2` static validation
- compiler artifacts
- runtime verifier
- artifact writer and loader
- audit events and append-only audit log
- execution manifest and execution result
- `safe_noop_run`
- `safe_run_cli`
- `run_status_cli --view`
- `run_status_cli --text`
- read-only text status renderer
- dependency-free TUI view model and renderer
- CLI hardening:
  - `--summary-only`
  - `--dry-run`
  - `--check`

## Design Hardening Documentation

- `README.md` is the documentation index: it organizes the docs into current
  implemented harness, security/design boundaries, and inspection-only safe code
  surfaces, and restates that V1 is no-op only, planner output is
  non-authoritative, and the compiler is the sole authority boundary.
- `SECURITY_ASSUMPTIONS_AND_LIMITS.md` records the current security boundary and
  the deferred enforcement gaps.
- `AUTHORITY_SUBSUMPTION_DESIGN.md` is a design-only checkpoint: it defines the
  future partial-order model that would be required before approval carryover or
  narrowed-authority reuse. Authority subsumption is design-only and is not
  implemented; exact-match approval remains the current behavior.
- `REAL_EXECUTION_THREAT_MODEL.md` is a design-only checkpoint and is not
  implemented; V1 remains no-op only. Real execution remains blocked behind
  sandbox/broker isolation, connector/tool allowlists, a side-effect policy,
  post-retrieval re-gating, deterministic audit, and fail-closed requirements.
- `SIDE_EFFECT_CATALOG_DESIGN.md` is a design-only checkpoint and is not
  implemented; V1 remains no-op only with no real tools or connectors. It defines
  the future governed catalog/allowlist for declared, scoped, versioned, and
  compiler-approved tools/connectors and the side-effect classes (read-only,
  local write, external write, network call, export, deletion/destructive). It
  does not implement tools, connectors, sandbox/broker, side effects, authority
  subsumption, or approval carryover.
- `SANDBOX_BROKER_INTERFACE_DESIGN.md` is a design-only checkpoint and is not
  implemented; V1 remains no-op only. It defines the future interface between the
  harness and an isolated execution broker/sandbox — isolation requirements and
  the broker input, decision, and result contracts, with sandbox attestation and
  fail-closed behavior. It does not implement a sandbox, broker, tools,
  connectors, a side-effect channel, authority subsumption, or approval
  carryover.
- `CANONICAL_JSON_V1.md` documents the currently implemented canonical JSON
  contract.
- canonical JSON characterization tests pin the current serializer and hashing
  behavior (`tests/test_canonical_json.py`).
- authority schema hardening rejects floats and non-finite values in
  authority-bearing artifacts:
  - `compiler/authority_value_validator.py` is the validation gate.
  - violations fail compile with `DISALLOWED_AUTHORITY_VALUE` diagnostics.
  - applied to loaded input artifacts and compiler-emitted authority artifacts.
  - `canonical_json.py` and hashing behavior are unchanged.
- static schema validation rejects malformed proposal shapes:
  - WorkflowSpec static schema validation checks required top-level fields and
    node/edge primitive types.
  - NodeTypeRegistry static schema validation checks required fields and
    node-type entry shape (`node_type`, `max_outgoing_edges`, `required_scopes`,
    `side_effect_class`).
  - RequestedAuth static schema validation checks required fields and
    connector/tool entry shape (`requested_connectors`, `connector_name`,
    `scope`, `requested_tools`, `tool_name`).
  - ApprovalRequests static schema validation checks required fields and request
    entry shape (`requests`, `request_id`, `node_id`, `approval_subject_hash`).
  - ApprovalDecisions static schema validation checks required fields and
    decision entry shape (`decisions`, `request_id`, `decision`); it runs only
    when `ApprovalDecisions.json` is present/provided.
  - `INVALID_ARTIFACT_SCHEMA` diagnostics (artifact + JSON path) apply to all five
    control-plane inputs:
    - `WorkflowSpec.json`
    - `NodeTypeRegistry.json`
    - `RequestedAuth.json`
    - `ApprovalRequests.json`
    - `ApprovalDecisions.json`
  - static schema hardening across control-plane inputs is complete.
  - validation is phased, and each phase gates the next even in aggregate mode:
    1. authority-value validation
    2. schema validation (Phase 2 now validates all five control-plane input
       shapes)
    3. interpretation validation (graph, scope, approval semantics)
- planner skeleton produces non-authoritative candidate proposals only:
  - `planner/workflow_spec_planner.py` builds a deterministic stub candidate
    (`WorkflowSpec.json`, `RequestedAuth.json`, `ApprovalRequests.json`) from a
    plain-text goal; the goal is carried as non-authoritative metadata only.
  - planner output is non-authoritative until compiler validation; the compiler
    remains the sole authority boundary.
  - no LLM call, no real authority inference, no execution, no compiled or
    runtime artifacts are written by the planner.
  - `cli/planner_check_cli.py` turns a `--goal` into a candidate and runs the
    compiler validate/compile check against a provided `NodeTypeRegistry.json`,
    writing only candidate input files (no compiled, audit, or runtime
    artifacts); exits 0 on compile ok, 1 on failure.
  - `planner_check_cli --dry-run` runs the same check via a temporary candidate
    bundle, leaving nothing on disk (no candidate-dir, no artifacts) and never
    exposing the temporary path; output adds `"dry_run": true`.
  - documented in `PLANNER_SKELETON.md`.
- side-effect audit event helpers are inspection-only pure builders:
  - `audit/side_effect_audit_event.py` provides `side_effect_proposed`,
    `side_effect_permitted`, `side_effect_denied`, and `side_effect_failed`,
    delegating to `make_audit_event` and packing domain fields into `details`
    (`side_effect_class`, optional tool/connector/scope/checked-authority/
    correlation/artifact/node-revision fields, and `reason_code` for
    denied/failed).
  - these are pure audit event builders only: no execution, no tools/connectors,
    no broker/sandbox, no side-effect catalog enforcement, no authority
    subsumption, no approval carryover, and no file writes; they authorize
    nothing and the compiler remains the sole authority boundary.
- side-effect catalog schema-shape validator is a pure standalone inspection
  helper:
  - `compiler/side_effect_catalog_schema_validator.py` provides
    `validate_side_effect_catalog_schema`, a pure standalone `SideEffectCatalog.json`
    schema-shape validator returning the existing `INVALID_ARTIFACT_SCHEMA`
    diagnostic convention.
  - it is not wired into `validate_static_inputs`, and `SideEffectCatalog.json` is
    not a control-plane input yet.
  - it grants no authority, enforces no runtime behavior, calls no
    tools/connectors, implements no sandbox/broker, and changes no canonical JSON
    or hashing.
- sandbox/broker contract shapes are pure data-shape builders:
  - `broker/sandbox_broker_contract.py` provides `build_broker_request`,
    `build_broker_decision`, and `build_broker_result` — pure data-shape builders
    for future broker request, decision, and result dictionaries.
  - it enforces only light shape invariants: a request requires exactly one of
    `tool_name` or `connector_name`; a denied decision requires `reason_code`; a
    failure/denied result requires `reason_code`.
  - it does not implement a broker, a sandbox, execution, tools/connectors,
    runtime/compiler wiring, catalog enforcement, authority subsumption, approval
    carryover, or any canonical JSON/hashing changes.
- example/future-only side-effect catalog fixture:
  - `fixtures/future/side-effect-catalog/SideEffectCatalog.json` is an
    example/future-only fixture validated only by the standalone side-effect
    catalog schema validator.
  - it is not active governance input, not a control-plane input, not consumed by
    compile/runtime, and grants no authority.
- end-to-end safe no-op workflow demo CLI:
  - `cli/workflow_demo_cli.py` composes the deterministic planner candidate, the
    compiler, the safe no-op run, and the status-inspection command into one
    operator demo loop.
  - it uses a self-contained run directory as the `effective_repo_root` (candidate
    inputs and a copied `NodeTypeRegistry.json` live under `--run-dir`).
  - it performs no real execution, calls no tools/connectors, implements no
    sandbox/broker, does not make planner output authoritative, and keeps runtime
    safe no-op only.
  - a blocked no-op outcome (`execution_status: "blocked"`) is expected when
    review/approval is required and no approval decision is supplied.
- opt-in read-only run-status summary surface:
  - `runtime/run_status_summary.py` (`summarize_run_directory`),
    `tui/run_status_summary_view.py` (`render_run_status_summary_view`), and
    `cli.run_status_cli --summary` provide an opt-in, read-only, fail-soft summary
    over known local safe-run artifacts.
  - the existing `inspect_run_directory`, default JSON output, `--text`, and
    `--view` remain existence-only and unchanged.
  - the summary reads only known local artifacts, writes nothing, calls no
    tools/connectors, performs no execution, and grants no authority.
  - it can show compile status, execution status, review-required,
    blocked-by-review, candidate-dir presence, artifact rows, and a status
    command.
- deterministic innovation-agent planner template:
  - `planner/workflow_spec_planner.py` now has `build_innovation_planner_candidate`
    and `select_planner_candidate`.
  - innovation-style goals matching whole-word keywords (`innovation`, `idea`,
    `ideas`, `mvp`) select the innovation template; unrelated goals use the
    existing stub template.
  - the innovation template is a deterministic, linear retrieve/synthesize chain
    that compiles against the existing simple registry.
  - it uses only proposal artifacts and example-prefixed names.
  - it calls no real connectors/tools, performs no execution, and planner output
    remains non-authoritative.
  - `workflow_demo_cli` reports `planner_template` (`"stub"` or `"innovation"`).
- safe innovation demo walkthrough and smoke test:
  - `SAFE_INNOVATION_DEMO.md` and `tests/test_safe_innovation_demo.py` document and
    test the two-command safe innovation demo (`workflow_demo_cli` then
    `run_status_cli --summary`).
  - it remains safe no-op only and calls no real tools/connectors; the smoke test
    asserts `planner_template: "innovation"`, `compilation_status: compiled`, and
    `execution_status: blocked`.

## Explicit Non-Goals

- no real execution
- no tools or connectors
- no authority subsumption
- no approval carryover
- no full TUI framework (a dependency-free status view and loop already exist)
- no LLM-backed planner and no authoritative planner output (the deterministic
  planner skeleton exists, but its output stays non-authoritative until compiler
  validation)
- no real policy evaluation

## Recommended Next Milestone Options

Design- and inspection-first, consistent with the current no-op boundary. Real
execution and real tools remain out of scope until their design checkpoints are
complete and reviewed.

1. Optional broker contract validators/examples: pure shape validation or
   example payloads for the broker request/decision/result shapes (still no
   broker implementation, no sandbox, no execution).
2. Documentation drift/link consistency audit: verify the docs index and
   cross-references stay accurate (docs/tests only; no runtime wiring).
3. TUI/operator view improvements over existing safe no-op artifacts (rendering
   only; no real execution).
4. Deterministic innovation-agent workflow template in safe no-op mode (candidate
   shape/template only; no real connectors, no execution).
