# Next Safe Slices

This is a concise handoff for future docs-first safe slices. It changes no behavior and enables nothing.

## Current Checkpoint

- `Baseline before this handoff slice: f7de8c4 Update safe noop milestone status`
- `Implementation checkpoint before this operator-review-packet slice: 3d88c2b Show display-only proposed tool access`
- `V1 remains safe no-op only`
- `433 tests passing`

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

Display-only Operator Review Packet is now implemented as an opt-in
`cli.run_status_cli --summary` checklist for blocked safe no-op runs. It is
derived only from already-computed summary fields, is operator-facing only, is
not a new artifact, does not change approval logic, does not change execution
behavior, and grants no authority.

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
