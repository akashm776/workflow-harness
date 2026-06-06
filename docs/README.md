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
  planner skeleton and its compile-check CLI.
- `cli/workflow_demo_cli.py` — end-to-end safe operator demo loop (goal →
  deterministic candidate → compile → safe no-op run → status command) into a
  self-contained `--run-dir`. No real execution, no tools/connectors, no
  sandbox/broker; runtime stays safe no-op only.

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
