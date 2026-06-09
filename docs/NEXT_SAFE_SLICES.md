# Next Safe Slices

This is a concise handoff for future docs-first safe slices. It changes no behavior and enables nothing.

## Current Checkpoint

- `Baseline before this handoff slice: f7de8c4 Update safe noop milestone status`
- `Implementation checkpoint before this safeguard-advisory slice: 6c81a23 Reject unsupported capability envelopes`
- `Implementation checkpoint before this authority-artifact slice: 4d9a468 Document static validation diagnostic order`
- `Implementation checkpoint before this secret-field slice: 51a214f Reject unsupported authority artifacts`
- `Implementation checkpoint before this hardening-map slice: 0ae585c Reject unsupported secret fields`
- `Implementation checkpoint before this authorization-summary slice: 2bac7e4 Document static validation hardening map`
- `Implementation checkpoint before this projection slice: 07c100e Document compiler authorization summary design`
- `Implementation checkpoint before this display-only compiler-authorization-projection slice: af7ca95 Document compiler authorization summary projection`
- `Implementation checkpoint before this approval-binding-rejection slice: ad83cad Document approval binding contract`
- `Implementation checkpoint before this approval-binding-summary slice: 4a6edcf Reject unsupported approval binding claims`
- `Implementation checkpoint before this verifier-evidence-status slice: c98d66a Document evidence lineage verifier output contract`
- `Implementation checkpoint before this broker-boundary-status slice: 5ca5d17 Document noop broker boundary contract`
- `V1 remains safe no-op only`
- `519 tests passing`

## Current Implemented Safety Runway

- safe innovation demo
- proposal-only skill/prompt registry design
- explicit deterministic `innovation_review` template
- inert future-only innovation context fixtures
- display-only fixture lineage for `innovation_review` summary
- display-only proposed tool access for `innovation_review` summary
- display-only Operator Review Packet for blocked summaries
- Review Gate visibility
- tool/MCP design boundary
- inert side-effect class registry
- fail-closed unsupported execution binding rejection
- capability envelope design
- capability envelope V1 design checkpoint
- inert future-only capability envelope example fixture
- fail-closed unsupported capability envelope rejection
- fail-closed unsupported secret field rejection
- static validation hardening map
- compiler authorization summary design
- inert future-only compiler authorization summary fixture
- compiler authorization summary projection design
- inert future-only compiler authorization summary projection fixture
- display-only compiler authorization projection for blocked `innovation_review` summaries
- safeguard advisory design checkpoint
- inert future-only safeguard advisory fixtures
- fail-closed unsupported safeguard authority-claim rejection
- authority artifact ownership contract
- fail-closed unsupported authority artifact rejection
- approval binding contract
- fail-closed unsupported approval-binding rejection
- display-only approval binding summary for blocked `innovation_review` summaries
- display-only verifier / evidence status for blocked `innovation_review` summaries
- display-only broker boundary status for blocked `innovation_review` summaries
- milestone docs updated

The richer deterministic innovation template slice is now implemented as the
explicit `--planner-template innovation_review` path. Default goal-based
selection remains unchanged, existing `innovation` behavior remains unchanged,
and the example wrapper default remains the existing safe innovation demo
behavior.

Local fixture input artifacts now also exist as inert future-only fake data under
`fixtures/future/innovation-context/`. V1 does not load them, execute anything
from them, connect to tools/connectors/MCP from them, or grant any authority.

Display-only fixture lineage is now implemented as an opt-in
`cli.run_status_cli --summary` section for explicit `innovation_review`
proposals. It is derived from already-read candidate workflow metadata only,
lists known future fixture paths as display-only strings, does not load fixture
contents, does not make fixtures control-plane inputs, and remains fail-soft
and operator-facing only.

Display-only proposed tool access is now implemented as an opt-in
`cli.run_status_cli --summary` section for explicit `innovation_review`
proposals. It is derived from the local candidate `RequestedAuth.json`
proposal only, shows proposed tools and connector metadata as display-only
operator guidance, does not execute tools, does not enable connector support,
does not change approval semantics, and remains fail-soft and operator-facing
only.

Display-only compiler authorization projection is now implemented as an opt-in
`cli.run_status_cli --summary` section for blocked explicit
`innovation_review` proposals. It is derived only from already-read
`EffectivePolicy.json`, blocked-review state, and existing
`CompilationReport.json` diagnostics; it is display-only, compiler-owned
summary metadata only, not executable, not persisted as an artifact, grants no
runtime authority, does not load future fixtures, does not write artifacts,
and does not change approval resolution or execution behavior. This is now
hardened as a display-only summary contract only, not an artifact-generation
milestone.

Display-only Operator Review Packet is now implemented as an opt-in
`cli.run_status_cli --summary` checklist for blocked safe no-op runs. It is
derived only from already-computed summary fields, is operator-facing only, is
not a new artifact, does not change approval logic, does not change execution
behavior, and grants no authority.

Capability envelope V1 design is now documented in
`CAPABILITY_ENVELOPE_V1_DESIGN.md`. It states that planner requests remain
non-authoritative, only the compiler may eventually produce compiled envelopes,
V1 does not execute envelopes, and future broker/sandbox enforcement remains
out of scope.

An inert future-only capability-envelope example now exists at
`fixtures/future/capability-envelope/CompiledCapabilityEnvelope.example.json`.
It is display-only, not executable, compiler-owned example data only, is not
consumed by compile/runtime/CLI behavior, and grants no authority.

Fail-closed unsupported capability-envelope rejection is now implemented in
`compiler/static_validation.py`. Planner-controlled artifacts that attempt to
include capability-envelope, authority-envelope, or
approved-capability fields are rejected with
`UNSUPPORTED_CAPABILITY_ENVELOPE`. This is rejection-only, does not generate
capability envelopes, does not consume capability envelopes, and does not
change runtime, CLI summary, approval, or execution behavior.

Fail-closed unsupported secret-field rejection is now implemented in
`compiler/static_validation.py`. Planner-controlled artifacts that attempt to
include exact secret-like key names such as token, secret, password, api_key,
private_key, credential, or credentials are rejected with
`UNSUPPORTED_SECRET_FIELD`. This is rejection-only, does not scan arbitrary
string values, does not add credential storage, and does not change runtime,
CLI summary, approval, or execution behavior.

Safeguard advisory design is now documented in `SAFEGUARD_ADVISORY_DESIGN.md`.
It states that safeguard output is advisory only, is not authority, cannot approve,
cannot grant capabilities, cannot unblock execution, and V1 does not call, download, or run any safeguard model.

Inert future-only safeguard advisory fixtures now exist at
`fixtures/future/safeguard-advisory/WorkflowHarnessSafeguardPolicy.md` and
`fixtures/future/safeguard-advisory/SafeguardAdvisory.example.json`. They are
advisory-only examples, not control-plane inputs, not an approval mechanism,
not an authority source, and no model is run from them.

Fail-closed unsupported safeguard authority-claim rejection is now implemented
in `compiler/static_validation.py`. Planner-controlled artifacts that attempt
to include safeguard approval, authorization, execution-unblock, or authority
override claims are rejected with
`UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM`. This is rejection-only, does not add
model inference, does not add API/network behavior, and does not change
runtime, CLI summary, approval, or execution behavior.

Authority artifact ownership is now documented in
`AUTHORITY_ARTIFACT_OWNERSHIP.md`. It states that candidate
`WorkflowSpec.json`, `RequestedAuth.json`, and `ApprovalRequests.json` remain
planner proposals only, compiler-owned and runtime-owned authority artifacts
must not be planner-supplied, operator approval remains explicit and
current-run/request scoped, and V1 safe no-op does not generate or consume
compiled capability envelopes.

Fail-closed unsupported authority artifact rejection is now implemented in
`compiler/static_validation.py`. Planner-controlled artifacts that attempt to
include compiler-owned diagnostics, compiled plans/manifests, runtime results,
audit or evidence artifacts, or approval-decision artifacts are rejected with
`UNSUPPORTED_AUTHORITY_ARTIFACT`. This is rejection-only, does not create
compiled artifacts, does not consume compiled artifacts, and does not change
runtime, CLI summary, approval, or execution behavior.

`STATIC_VALIDATION_HARDENING_MAP.md` now documents the current
`validate_static_inputs(...)` hardening layers: Phase 1 authority-value
validation, Phase 2 schema validation, and the current Phase 3 interpretation
ordering of secret-field, capability-envelope, safeguard-authority-claim,
authority-artifact-ownership, execution-binding, then graph/scope/approval
validators. It also records validator ownership for
`UNSUPPORTED_SECRET_FIELD`, `UNSUPPORTED_CAPABILITY_ENVELOPE`,
`UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM`, `UNSUPPORTED_AUTHORITY_ARTIFACT`, and
`UNSUPPORTED_EXECUTION_BINDING`, plus the rule that future validators remain
deterministic and fail-closed. This is docs-only and changes no compiler
behavior.

`COMPILER_AUTHORIZATION_SUMMARY_DESIGN.md` now documents a future
compiler-owned authorization summary. It states that planner must not supply
it, it is derived only from compiler-validated candidate artifacts, it may
summarize requested authority, blocked authority, approval-required authority,
and unsupported authority, it does not grant runtime execution by itself, it
does not replace `ApprovalDecisions.json`, it does not enable approval
carryover, it is scoped to the current run/request/artifact revision, and V1
safe no-op does not generate or consume it yet.

An inert future-only compiler authorization summary fixture now exists at
`fixtures/future/compiler-authorization-summary/CompilerAuthorizationSummary.example.json`.
It is compiler-owned, display-only, not executable, not consumed by V1,
contains no credentials, grants no runtime authority, and is fixture/test data
only.

`COMPILER_AUTHORIZATION_SUMMARY_PROJECTION.md` now documents a future
projection contract for compiler-owned authorization summaries. It states that
inputs are limited to compiler-validated `RequestedAuth.json`,
compiler-validated `ApprovalRequests.json`, static validation diagnostics, and
current run/request/artifact-revision context; output sections are
`requested_authority`, `approval_required`, `blocked_authority`, and
`unsupported_authority`; projection is deterministic and non-authoritative;
and V1 safe no-op does not generate or consume the projection yet.

An inert future-only compiler authorization summary projection fixture now
exists at
`fixtures/future/compiler-authorization-summary/CompilerAuthorizationSummaryProjection.example.json`.
It is display-only, not generated by V1, not consumed by V1, not executable,
contains no credentials, grants no runtime authority, and is fixture/test data
only.

## Recommended Next Safe Slices

No new next safe slice is recorded in this handoff. Re-evaluate after this
display-only operator-surface checkpoint.

## Slice Boundaries

### 1. Proposal-only skill/prompt registry design

- docs/design only first
- define future `SkillRegistry` and `PromptTemplateRegistry`
- no execution
- no LLM planning
- no dynamic skill creation
- no arbitrary planner prompts becoming executable

### 2. Richer deterministic innovation template

- deterministic template only
- add dedupe/critique/scoring/MVP-plan nodes
- safe no-op only
- approval-gated
- no connectors/tools/MCP/network
- no dynamic node creation
- no LLM planner

### Implemented checkpoint: Display-only fixture lineage

- `cli.run_status_cli --summary` now shows known future fixture paths as
  display-only for explicit `innovation_review` proposals
- known fixture paths may include:
  - `fixtures/future/innovation-context/ProgramContext.json`
  - `fixtures/future/innovation-context/RepoContextSummary.json`
  - `fixtures/future/innovation-context/ConfluenceContextSummary.json`
  - `fixtures/future/innovation-context/IssueTrackerContextSummary.json`
  - `fixtures/future/innovation-context/Rubric.json`
- no fixture loading
- no fixture content loading
- not control-plane inputs
- no planner/compiler/runtime behavior
- no connector/MCP/tools
- no authority or approval changes
- no fixture-driven planning
- fail-soft and operator-facing only

### Implemented checkpoint: Display-only proposed tool access

- `cli.run_status_cli --summary` now shows proposed future tool needs as
  display-only for explicit `innovation_review` proposals
- it is derived from the local candidate `RequestedAuth.json` proposal only
- proposal-only
- no connector support
- no tool execution
- no approval semantics changes

### Implemented checkpoint: Display-only Operator Review Packet

- `cli.run_status_cli --summary` now shows an operator-facing checklist for
  blocked safe no-op runs
- it is derived only from already-computed summary fields
- it is not a new artifact
- it is not approval logic
- it is not execution behavior
- no authority is granted

### Implemented checkpoint: Display-only compiler authorization projection

- `cli.run_status_cli --summary` now shows a
  `Compiler Authorization Projection:` section for blocked explicit
  `innovation_review` proposals
- it is derived only from already-read `EffectivePolicy.json`,
  blocked-review state, and existing `CompilationReport.json` diagnostics
- display-only
- compiler-owned summary metadata only
- not executable
- not persisted as an artifact
- no runtime authority
- no fixture loading
- no artifact writing
- no approval behavior changes
- no execution behavior changes

## Hard Non-Goals

- no real execution
- no tools/connectors
- no MCP/network calls
- no sandbox/broker implementation
- no LLM planning
- no dynamic node creation
- no approval carryover
- no authority subsumption
- no approval matching semantics changes
- no canonical JSON/hashing changes
- do not edit `compiler/canonical_json.py`

## Decision Rule

Every risky future capability should first appear as a design doc, then inert
data/fixtures, then compiler rejection or display-only reporting, before any execution path exists.
