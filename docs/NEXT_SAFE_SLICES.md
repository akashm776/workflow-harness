# Next Safe Slices

This is a concise handoff for future docs-first safe slices. It changes no behavior and enables nothing.

## Current Checkpoint

- `Baseline before this handoff slice: f7de8c4 Update safe noop milestone status`
- `Implementation checkpoint before this docs update: f4f6873 Add deterministic innovation review template`
- `V1 remains safe no-op only`
- `427 tests passing`

## Current Implemented Safety Runway

- safe innovation demo
- proposal-only skill/prompt registry design
- explicit deterministic `innovation_review` template
- inert future-only innovation context fixtures
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

## Recommended Next Safe Slices

1. Display-only fixture lineage
2. Display-only proposed tool access

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

### 3. Display-only fixture lineage

- summary/docs may show known future fixture paths as display-only
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
- fail-soft and operator-facing only if later implemented

### 4. Display-only proposed tool access

- summary may show proposed future tool needs as proposal-only
- no connector support
- no tool execution
- no approval semantics changes

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
