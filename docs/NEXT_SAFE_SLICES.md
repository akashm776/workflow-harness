# Next Safe Slices

This is a concise handoff for future docs-first safe slices. It changes no behavior and enables nothing.

## Current Checkpoint

- `Baseline before this handoff slice: f7de8c4 Update safe noop milestone status`
- `V1 remains safe no-op only`
- `411 tests passing`

## Current Implemented Safety Runway

- safe innovation demo
- Review Gate visibility
- tool/MCP design boundary
- inert side-effect class registry
- fail-closed unsupported execution binding rejection
- capability envelope design
- milestone docs updated

## Recommended Next Safe Slices

1. Proposal-only skill/prompt registry design
2. Richer deterministic innovation template
3. Local fixture input artifacts
4. Display-only proposed tool access

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

### 3. Local fixture input artifacts

- local committed fake data only
- no external reads
- no credentials
- no connector/MCP calls
- fixture lineage can be display-only

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
