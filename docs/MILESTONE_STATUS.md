# Milestone Status

## Current Milestone

`V1 Safe No-Op Harness`

## Test Status

- `484 tests` passing

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
- future-only innovation context fixtures:
  - `fixtures/future/innovation-context/` contains fake local
    `ProgramContext.json`, `RepoContextSummary.json`,
    `ConfluenceContextSummary.json`, `IssueTrackerContextSummary.json`, and
    `Rubric.json` summaries plus a fixture-local `README.md`.
  - they are inert example data only: not control-plane inputs, not loaded by
    planner/compiler/runtime/CLI/examples, and they do not enable execution,
    connector calls, MCP calls, or authority.
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
  - explicit `--planner-template innovation_review` selection now adds a richer
    deterministic review template only when requested.
  - default goal-based selection remains unchanged, and existing `innovation`
    behavior remains unchanged.
  - the innovation template is a deterministic, linear retrieve/synthesize chain
    that compiles against the existing simple registry.
  - the `innovation_review` template also compiles against the existing simple
    registry, uses only the existing `retrieve` and `synthesize` node types, and
    adds deterministic proposal stages for dedupe against existing work,
    generating idea candidates, scoring against a rubric, critiquing top ideas,
    and synthesizing MVP plans.
  - it uses only proposal artifacts and example-prefixed names.
  - it calls no real connectors/tools, performs no execution, and planner output
    remains non-authoritative.
  - `workflow_demo_cli` reports `planner_template` (`"stub"`, `"innovation"`, or
    `"innovation_review"`).
- safe innovation demo walkthrough and smoke test:
  - `SAFE_INNOVATION_DEMO.md` and `tests/test_safe_innovation_demo.py` document and
    test the two-command safe innovation demo (`workflow_demo_cli` then
    `run_status_cli --summary`).
  - it remains safe no-op only and calls no real tools/connectors; the smoke test
    asserts `planner_template: "innovation"`, `compilation_status: compiled`, and
    `execution_status: blocked`.
- candidate workflow graph visibility in the opt-in run-status summary:
  - `runtime/run_status_summary.py` now reads `<run-dir>/candidate/WorkflowSpec.json`
    fail-soft as display-only proposal data (the `candidate_workflow` field).
  - `tui/run_status_summary_view.py` renders a `Candidate Workflow:` section with
    node IDs, node types, display names, and edges.
  - it is read-only, writes nothing, grants no authority, validates nothing, and
    does not change `inspect_run_directory`, default JSON, `--text`, or `--view`.
- display-only Review Gate guidance in `run_status_cli --summary`:
  - the summary renders a `Review Gate:` section for blocked safe no-op runs.
  - it reads `candidate/ApprovalRequests.json` fail-soft for operator guidance only.
  - it does not validate approval semantics, approve anything, or change
    matching behavior.
  - unblocking still requires an explicit matching `ApprovalDecisions.json` for the current run/request only.
- explicit approval-decision demo path (blocked -> approved -> completed):
  - `tests/test_safe_innovation_approval_demo.py` and the approval section of
    `SAFE_INNOVATION_DEMO.md` demonstrate carrying the blocked innovation run to a
    completed safe no-op by supplying an explicit `ApprovalDecisions.json` via the
    existing `safe_run_cli --approval-decisions`.
  - approval is explicit and for the current run/request only; it changes no
    approval matching semantics and implements no carryover, subsumption, or
    execution. `completed` remains a completed safe no-op (`side_effects == []`).
- safe innovation demo example wrapper:
  - `examples/safe_innovation_demo.py` and `tests/test_safe_innovation_demo_example.py`
    provide a demo/example wrapper that composes the blocked and approved safe
    innovation demo paths.
  - it is an example script kept out of `cli/`; approval generation requires the
    explicit `--demo-approve-current-request` flag.
  - it can pass through `--planner-template innovation_review`, but its default
    remains the existing safe innovation demo behavior.
  - the generated approval is demo-local and current-run/request-only, not a
    general auto-approval mechanism.
  - no approval semantics, carryover, subsumption, or execution changed; runtime
    remains safe no-op only.
- explicit deterministic `innovation_review` blocked-run surface:
  - missing approval still blocks safely, the run remains safe no-op only, and
  `cli.run_status_cli --summary` shows both the candidate graph and
  `Review Gate:` guidance for the blocked run.
- display-only fixture lineage in the opt-in summary:
  - for explicit `innovation_review` proposals,
    `cli.run_status_cli --summary` now also renders a `Fixture Lineage:`
    section listing known future fixture paths under
    `fixtures/future/innovation-context/`.
  - it is derived from already-read candidate workflow metadata only.
  - it does not load fixture contents, does not make fixtures control-plane
    inputs, grants no authority, and remains fail-soft and operator-facing
    only.
- display-only proposed tool access in the opt-in summary:
  - for explicit `innovation_review` proposals,
    `cli.run_status_cli --summary` now also renders a
    `Proposed Tool Access:` section derived from the local candidate
    `RequestedAuth.json` proposal only.
  - it shows proposed tools and connector metadata as display-only,
    proposal-only operator guidance.
  - it does not execute tools, does not enable connector support, does not
    change approval semantics, grants no authority, and remains fail-soft and
    operator-facing only.
- display-only compiler authorization projection in the opt-in summary:
  - for blocked explicit `innovation_review` proposals,
    `cli.run_status_cli --summary` now also renders a
    `Compiler Authorization Projection:` section.
  - it is derived only from already-read `EffectivePolicy.json`, blocked-review
    state, and existing `CompilationReport.json` diagnostics.
  - it is display-only, compiler-owned summary metadata only, not executable,
    not persisted as an artifact, grants no runtime authority, and is scoped to
    the current run only.
  - it does not load future fixtures, does not write artifacts, does not
    change approval resolution, and does not change execution behavior.
- display-only operator review packet in the opt-in summary:
  - when a safe no-op run is blocked by review,
    `cli.run_status_cli --summary` now also renders an
    `Operator Review Packet:` checklist.
  - it is derived only from already-computed summary fields such as
    `review_required`, `blocked_by_review`, `review_gate`,
    `candidate_workflow`, `fixture_lineage`, `proposed_tool_access`, and
    `compiler_authorization_projection`.
  - it is operator-facing only, not a new artifact, not approval logic, not
    execution behavior, grants no authority, and remains fail-soft.
- tool/connector/MCP trust-boundary design checkpoint:
  - `TOOL_CONNECTOR_CATALOG_DESIGN.md` documents that tool and MCP proposals
  remain non-authoritative, the compiler remains the sole authority boundary,
    and any future MCP/tool execution must be broker-mediated and use standard MCP transports/methods.
  - V1 safe no-op still enables no real connectors and no MCP/network calls.
- inert side-effect class registry:
  - `registry/SideEffectClasses.json` is an inert class-ID registry only.
  - it defines stable side-effect class names/descriptions and enables no
    execution or approval.
- unsupported execution binding rejection:
  - `compiler/static_validation.py` rejects node-level tool/connector/broker/MCP
    execution intent in `WorkflowSpec.json` with
    `UNSUPPORTED_EXECUTION_BINDING`.
  - this is a V1 fail-closed guard only; it is not an MCP schema and it
    preserves future broker-mediated standard MCP compatibility.
- capability envelope design checkpoint:
  - `CAPABILITY_ENVELOPE_DESIGN.md` documents future compiler-produced,
    node-scoped capability envelopes.
  - runtime remains orchestration-only; any future isolated broker/sandbox would
    enforce the envelope.
  - skills, tools, prompt templates, approvals, and broker bindings stay
    explicit per node; no ambient authority is granted.
- capability envelope V1 checkpoint and fail-closed rejection:
- `CAPABILITY_ENVELOPE_V1_DESIGN.md` records that planner capability requests
  remain non-authoritative, only the compiler may eventually produce compiled
  envelopes, and V1 neither generates nor consumes capability envelopes.
- `AUTHORITY_ARTIFACT_OWNERSHIP.md` records the planner-proposed vs
  compiler-owned vs runtime-owned vs operator-owned artifact boundary: planner
  artifacts remain non-authoritative, compiler remains the authority boundary,
  runtime reports results but does not invent authority, and operator approval
  remains explicit and current-run/request scoped.
- `COMPILER_AUTHORIZATION_SUMMARY_DESIGN.md` records the future
  compiler-owned authorization summary boundary: planner must not supply it,
  it is derived only from compiler-validated candidate artifacts, it does not
  grant runtime execution by itself, and V1 safe no-op does not generate or
  consume it yet.
- `COMPILER_AUTHORIZATION_SUMMARY_PROJECTION.md` records the future projection
  contract for compiler-owned authorization summaries: inputs are limited to
  compiler-validated artifacts, static validation diagnostics, and current
  run/request/artifact-revision context; output sections remain deterministic
  and non-authoritative; and V1 safe no-op does not generate or consume the
  projection yet.
- `STATIC_VALIDATION_HARDENING_MAP.md` records the current static validation
  phases, current interpretation-validator ownership and ordering, and the
  rules for adding future validators. It is docs-only hardening and changes no
  compiler behavior.
- `fixtures/future/capability-envelope/CompiledCapabilityEnvelope.example.json`
  is an inert display-only, not executable, compiler-owned example shape only.
- `fixtures/future/compiler-authorization-summary/CompilerAuthorizationSummary.example.json`
  is an inert display-only, compiler-owned authorization-summary example only.
  It is not executable, not consumed by V1 safe no-op, contains no
  credentials, and grants no runtime authority.
- `fixtures/future/compiler-authorization-summary/CompilerAuthorizationSummaryProjection.example.json`
  is an inert display-only authorization-summary projection example only. It
  is not generated by V1, not consumed by V1, not executable, contains no
  credentials, and grants no runtime authority.
- `compiler/static_validation.py` now rejects planner-controlled capability or
  authority envelope fields in candidate artifacts with
  `UNSUPPORTED_CAPABILITY_ENVELOPE`.
- secret field checkpoint and fail-closed rejection:
  - `compiler/static_validation.py` now rejects planner-controlled secret-like
    exact key names in candidate artifacts with `UNSUPPORTED_SECRET_FIELD`.
  - `credential` and `credentials` are now owned by the dedicated
    secret-field validator rather than capability-envelope diagnostics.
  - this is rejection-only; it does not scan arbitrary string values, does not
    add credential storage, and does not change runtime, planner, CLI,
    approval, or execution behavior.
- safeguard advisory design checkpoint and fail-closed authority-claim rejection:
  - `SAFEGUARD_ADVISORY_DESIGN.md` records that safeguard output is advisory
    only, cannot approve or grant capabilities, and cannot unblock execution.
  - `fixtures/future/safeguard-advisory/WorkflowHarnessSafeguardPolicy.md` and
    `fixtures/future/safeguard-advisory/SafeguardAdvisory.example.json` are
    inert advisory-only future examples only.
- `compiler/static_validation.py` now rejects planner-supplied or
  model-supplied safeguard authority-claim keys in candidate artifacts with
  `UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM`.
- authority artifact ownership checkpoint and fail-closed rejection:
  - `AUTHORITY_ARTIFACT_OWNERSHIP.md` records that candidate
    `WorkflowSpec.json`, `RequestedAuth.json`, and `ApprovalRequests.json` are
    planner proposals only, while compiler/runtime/operator authority artifacts
    remain out of planner control.
  - `compiler/static_validation.py` now rejects planner-controlled
    compiler-owned, runtime-owned, or operator-owned authority artifact keys in
    candidate artifacts with `UNSUPPORTED_AUTHORITY_ARTIFACT`.
  - this is rejection-only; it does not create compiled artifacts, does not
    consume compiled artifacts, does not change approval behavior, and does not
    enable runtime authority.
- static validation diagnostic ordering contract:
  - `validate_static_inputs(...)` remains deterministic and fail-closed by
    phase: authority-value validators, then schema validators, then
    interpretation validators.
  - current interpretation validator ownership is:
    - secret-field validator:
      `UNSUPPORTED_SECRET_FIELD` for planner-supplied token, secret, password,
      API-key, private-key, or credential-like exact field names.
    - capability-envelope validator:
      `UNSUPPORTED_CAPABILITY_ENVELOPE` for unsupported capability/authority
      envelope fields.
    - safeguard-authority-claim validator:
      `UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM` for safeguard approval,
      authorization, or execution-unblock claims.
    - authority-artifact-ownership validator:
      `UNSUPPORTED_AUTHORITY_ARTIFACT` for planner-supplied compiler-owned,
      runtime-owned, or operator-owned authority artifact fields.
    - execution-binding validator:
      `UNSUPPORTED_EXECUTION_BINDING` for tool/connector/MCP/broker execution
      binding claims.
  - within the current interpretation phase, ordering is deterministic:
    secret-field checks, then capability-envelope checks, then safeguard-authority-claim checks, then authority-artifact-ownership checks, then execution-binding checks, then graph/scope/approval validators.
  - this is a hardening contract for safety regression tests, not a public API.

## Explicit Non-Goals

- no real execution
- no tools or connectors
- no MCP/network calls
- no sandbox/broker implementation
- no authority subsumption
- no approval carryover
- no full TUI framework (a dependency-free status view and loop already exist)
- no LLM-backed planner and no authoritative planner output (the deterministic
  planner skeleton exists, but its output stays non-authoritative until compiler
  validation)
- no dynamic node creation
- no skill/prompt registry implementation
- no fixture input artifact implementation
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
4. Local fixture input artifacts for deterministic templates (committed fake
   data only; no external reads, no credentials, no connector/MCP calls).
