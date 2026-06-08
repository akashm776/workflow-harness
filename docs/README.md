# Documentation Index

This index organizes the workflow-harness documentation. It is a navigation aid
only and changes no behavior.

## Status Summary

- **V1 remains safe no-op only.** The execution path is a deterministic stand-in;
  no real work is performed.
- **Planner output remains non-authoritative.** Planner artifacts are proposals
  until the compiler validates and compiles them.
- **The compiler remains the sole authority boundary.** Only deterministic
  compilation produces authority-bearing artifacts.
- **No real execution, tools, connectors, sandbox, or broker is implemented**,
  and there is **no approval carryover and no authority subsumption behavior**.
  The design and safe-code documents below describe future targets and pure
  inspection-only surfaces, not enabled capabilities.

## 1. Current Implemented Harness

- [`V1_SAFE_NOOP_HARNESS.md`](V1_SAFE_NOOP_HARNESS.md) — the current safe no-op
  operator surface and CLIs.
- [`MILESTONE_STATUS.md`](MILESTONE_STATUS.md) — implemented layers, test count,
  non-goals, and recommended next milestones.
- [`CANONICAL_JSON_V1.md`](CANONICAL_JSON_V1.md) — the implemented canonical JSON
  contract.
- [`PLANNER_SKELETON.md`](PLANNER_SKELETON.md) — the deterministic, non-authoritative
  planner skeleton and its compile-check CLI, including the deterministic
  innovation-agent template and the whole-word keyword selector (`planner_template`
  reported by the demo). No LLM planning, no real execution.
- `cli/workflow_demo_cli.py` — end-to-end safe operator demo loop (goal →
  deterministic candidate → compile → safe no-op run → status command) into a
  self-contained `--run-dir`. No real execution, no tools/connectors, no
  sandbox/broker; runtime stays safe no-op only.
- [`SAFE_INNOVATION_DEMO.md`](SAFE_INNOVATION_DEMO.md) — a short two-command safe
  no-op walkthrough (`workflow_demo_cli` + `run_status_cli --summary`), now
  including an explicit approval-decision path from blocked to completed safe
  no-op (`safe_run_cli --approval-decisions`). It is a safe no-op demonstration,
  not real execution.
- `examples/safe_innovation_demo.py` — an example wrapper that runs the safe
  innovation demo end to end (blocked, and optionally an explicit demo-local
  approval to completed). It is an example script, **not** a core CLI approval
  path; any approval it writes is demo-local and current-run/request-only.
- `cli.run_status_cli --summary` (`runtime/run_status_summary.py`,
  `tui/run_status_summary_view.py`) — an opt-in, read-only, fail-soft summary over
  known local safe-run artifacts, including an optional `Candidate Workflow:`
  graph section read from the local candidate proposal for display only. The
  default existence-only status path is unchanged. It reads only local artifacts,
  writes nothing, calls no tools/connectors, performs no execution, and grants no
  authority.

## 2. Security / Design Boundaries

These documents define the current security boundary, deferred gaps, and future
design gates. The design-only documents in this section are not implementations.

- [`SECURITY_ASSUMPTIONS_AND_LIMITS.md`](SECURITY_ASSUMPTIONS_AND_LIMITS.md) — the
  current security boundary and deferred enforcement gaps.
- [`AUTHORITY_SUBSUMPTION_DESIGN.md`](AUTHORITY_SUBSUMPTION_DESIGN.md) — the future
  authority partial-order model required before any approval carryover or
  narrowed-authority reuse (not implemented; exact-match approval remains current).
- [`REAL_EXECUTION_THREAT_MODEL.md`](REAL_EXECUTION_THREAT_MODEL.md) — the
  prerequisites that gate any move beyond safe no-op execution.
- [`SIDE_EFFECT_CATALOG_DESIGN.md`](SIDE_EFFECT_CATALOG_DESIGN.md) — the future
  governed catalog/allowlist for tools, connectors, and side-effect classes.
- [`SANDBOX_BROKER_INTERFACE_DESIGN.md`](SANDBOX_BROKER_INTERFACE_DESIGN.md) — the
  future interface between the harness and an isolated execution broker/sandbox.

- [`TOOL_CONNECTOR_CATALOG_DESIGN.md`](TOOL_CONNECTOR_CATALOG_DESIGN.md) - the
  future trust-boundary design for tool, connector, and MCP-style integration:
  planner proposals remain non-authoritative, compiler remains the sole
  authority boundary, runtime does not call tools directly, and any future tool
  execution must be brokered/sandboxed. No real connectors or MCP/network calls
  are enabled in V1 safe no-op.
- [`CAPABILITY_ENVELOPE_DESIGN.md`](CAPABILITY_ENVELOPE_DESIGN.md) - the future
  node-scoped capability envelope design: compiler-produced per-node tools,
  skills, prompt-template references, approvals, and broker bindings only. No
  ambient authority, no approval carryover, no authority subsumption, and no
  execution behavior is enabled in V1 safe no-op.
- [`SKILL_PROMPT_REGISTRY_DESIGN.md`](SKILL_PROMPT_REGISTRY_DESIGN.md) - the
  future design for `SkillRegistry` and `PromptTemplateRegistry`: planner
  proposals remain non-authoritative, prompts and skills stay versioned/reviewed
  artifacts, and any future LLM/subagent skill execution must remain
  broker/sandbox mediated.

## 3. Implementation Checkpoints / Safe Code Surfaces

These are pure, inspection-only code surfaces. They build or validate data
structures only: they execute nothing, authorize nothing, call no tools or
connectors, and are not wired into compile or runtime behavior.

- **Side-effect audit event helpers** (`audit/side_effect_audit_event.py`) — pure
  builders for `side_effect_proposed` / `permitted` / `denied` / `failed` audit
  events. Builders only; they authorize and execute nothing.
- **Side-effect catalog schema validator**
  (`compiler/side_effect_catalog_schema_validator.py`) — a pure standalone
  `SideEffectCatalog.json` schema-shape validator. It is not wired into
  `validate_static_inputs`, and `SideEffectCatalog.json` is not a control-plane
  input.
- **Sandbox/broker contract shapes** (`broker/sandbox_broker_contract.py`) — pure
  data-shape builders for future broker request, decision, and result
  dictionaries, with light shape invariants only. No broker, sandbox, or
  execution is implemented.

### Example / Future-Only Fixtures

- `fixtures/future/` holds example/future-only artifacts that are **not** active
  governance inputs, **not** control-plane inputs, and **not** consumed by compile
  or runtime. They exist only to demonstrate future shapes and to be exercised by
  standalone validators.
- `fixtures/future/side-effect-catalog/SideEffectCatalog.json` is an example
  catalog validated only by `compiler/side_effect_catalog_schema_validator.py`. It
  grants no authority. See [`../fixtures/future/README.md`](../fixtures/future/README.md).

## 4. Handoff

- [`NEXT_SAFE_SLICES.md`](NEXT_SAFE_SLICES.md) - concise handoff for the next
  docs-first safe slices and the staging rule for risky future capabilities.
