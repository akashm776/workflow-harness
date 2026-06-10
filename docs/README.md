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
- [`CAPABILITY_ENVELOPE_V1_DESIGN.md`](CAPABILITY_ENVELOPE_V1_DESIGN.md) - the
  V1 boundary checkpoint for future compiled capability envelopes: planner may
  request capabilities but cannot authorize them, compiler remains the only
  future authority boundary that may produce compiled envelopes, and V1 rejects
  planner-supplied capability-envelope fields fail-closed.
- [`AUTHORITY_ARTIFACT_OWNERSHIP.md`](AUTHORITY_ARTIFACT_OWNERSHIP.md) - the
  future ownership boundary for planner-proposed vs compiler-owned vs
  runtime-owned vs operator-owned artifacts: planner proposals remain
  non-authoritative, compiler remains the authority boundary, runtime reports
  results without inventing authority, and V1 rejects planner-supplied
  compiler/runtime/operator authority artifact fields fail-closed.
- [`COMPILER_AUTHORIZATION_SUMMARY_DESIGN.md`](COMPILER_AUTHORIZATION_SUMMARY_DESIGN.md) -
  the future compiler-owned authorization summary boundary: planner must not
  supply it, it is derived only from compiler-validated candidate artifacts,
  and V1 safe no-op does not generate or consume it yet.
- [`COMPILER_AUTHORIZATION_SUMMARY_PROJECTION.md`](COMPILER_AUTHORIZATION_SUMMARY_PROJECTION.md) -
  the future projection contract for compiler-owned authorization summaries:
  inputs come only from compiler-validated artifacts and diagnostics, output
  sections stay deterministic and non-authoritative, and V1 safe no-op does
  not generate or consume the projection yet.
- [`STATIC_VALIDATION_HARDENING_MAP.md`](STATIC_VALIDATION_HARDENING_MAP.md) -
  a docs-only map of the current static validation phases, validator
  ownership, deterministic diagnostic order, and the rules for adding future
  fail-closed validators. It changes no compiler behavior.
- [`SAFEGUARD_ADVISORY_DESIGN.md`](SAFEGUARD_ADVISORY_DESIGN.md) - the future
  advisory-only safeguard review boundary: safeguard output is not authority,
  cannot approve or grant capabilities, and V1 does not call, download, or run
  any safeguard model.
- [`SKILL_PROMPT_REGISTRY_DESIGN.md`](SKILL_PROMPT_REGISTRY_DESIGN.md) - the
  future design for `SkillRegistry` and `PromptTemplateRegistry`: planner
  proposals remain non-authoritative, prompts and skills stay versioned/reviewed
  artifacts, and any future LLM/subagent skill execution must remain
  broker/sandbox mediated.
- [`APPROVAL_BINDING_CONTRACT.md`](APPROVAL_BINDING_CONTRACT.md) - the future
  contract for how operator-owned approvals bind to the current run, request,
  approval subject, candidate artifact revision/digest, and requested authority
  shape: approvals grant no authority outside the current request, do not carry
  over across runs, are not reusable ambient authority, and V1 safe no-op does
  not use approvals for real execution.
- [`EVIDENCE_LINEAGE_VERIFIER_OUTPUT_CONTRACT.md`](EVIDENCE_LINEAGE_VERIFIER_OUTPUT_CONTRACT.md) -
  the future reporting-only contract for evidence lineage and verifier output:
  both are reporting only and non-authoritative, planner may not supply them as
  authority, the compiler remains the authority boundary, and neither can
  approve, authorize execution, grant capabilities, override compiler
  diagnostics or operator approval, enable approval carryover/authority
  subsumption, or create reusable authority. V1 safe no-op does not generate or
  consume them yet.
- [`NOOP_BROKER_BOUNDARY_CONTRACT.md`](NOOP_BROKER_BOUNDARY_CONTRACT.md) - the
  future broker boundary contract: the broker is a future isolated execution
  boundary, not an authority boundary; it must not trust planner output or
  consume planner-supplied compiled artifacts, may eventually execute only
  compiler-approved capabilities with explicit approval where required, and its
  decisions/results cannot approve, authorize, grant capabilities, override
  compiler diagnostics or operator approval, enable approval carryover/authority
  subsumption, or create reusable authority. V1 safe no-op has no broker,
  sandbox, or fake/no-op broker interface.
- [`OPERATOR_COCKPIT_CONTRACT.md`](OPERATOR_COCKPIT_CONTRACT.md) - the current
  contract for the V1 safe no-op operator cockpit: it records the exact
  display-only section order for blocked explicit `innovation_review` rich
  summaries (Review Gate → Candidate Workflow → Fixture Lineage → Proposed Tool
  Access → Compiler Authorization Projection → Approval Binding Summary →
  Verifier / Evidence Status → Broker Boundary Status → Operator Review Packet),
  each section's responsibility, and the read-only/no-execution safety boundary.
  Planner stays non-authoritative, the compiler remains the sole authority
  boundary, and the sections grant no authority and write no artifacts.
- [`STATIC_VALIDATION_ORDERING_CONTRACT.md`](STATIC_VALIDATION_ORDERING_CONTRACT.md) -
  the current contract for compiler static validation ordering: it records the
  exact Phase 3 hardening order (secret-field → capability-envelope →
  safeguard-authority-claim → authority-artifact-ownership → approval-binding →
  execution-binding → runtime-reporting-boundary → audit-evidence-authority →
  graph/scope/approval), each diagnostic's exclusive ownership boundary, the
  planner-input scanner scope (planner-controlled artifacts only, never
  `ApprovalDecisions.json`), exact-object-key matching, and the fail-closed
  guarantees. It is docs/tests only and changes no behavior.

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
- `fixtures/future/capability-envelope/CompiledCapabilityEnvelope.example.json`
  is an inert display-only example shape. It is not executable, not consumed by
  compile/runtime, and grants no authority.
- `fixtures/future/compiler-authorization-summary/CompilerAuthorizationSummary.example.json`
  is an inert compiler-owned future authorization-summary example. It is
  display-only, not executable, not consumed by compile/runtime, and grants no
  runtime authority.
- `fixtures/future/compiler-authorization-summary/CompilerAuthorizationSummaryProjection.example.json`
  is an inert future authorization-summary projection example. It is
  display-only, not generated or consumed by V1, not executable, and grants no
  runtime authority.
- `fixtures/future/safeguard-advisory/WorkflowHarnessSafeguardPolicy.md` and
  `fixtures/future/safeguard-advisory/SafeguardAdvisory.example.json` hold
  advisory-only future safeguard policy/output examples. They are not
  control-plane inputs, not an approval mechanism, not an authority source,
  and no model is run from them.
- `fixtures/future/approval-binding/ApprovalBinding.example.json` is an inert
  display-only, operator-owned future approval-binding example. It is not
  executable, not consumed by compile/runtime, not reusable ambient authority,
  and grants no runtime authority.
- `fixtures/future/evidence-lineage/EvidenceLineage.example.json` and
  `fixtures/future/verifier-output/VerifierOutput.example.json` are inert
  display-only, reporting-only future evidence-lineage and verifier-output
  examples. They are not authority, not control-plane inputs, not executable,
  not consumed by compile/runtime, and grant no runtime authority.
- `fixtures/future/noop-broker/BrokerRequest.example.json`,
  `fixtures/future/noop-broker/BrokerDecision.example.json`, and
  `fixtures/future/noop-broker/BrokerResult.example.json` are inert display-only
  future broker request/decision/result examples. They are not authority, not
  control-plane inputs, not executable, not consumed by compile/runtime, and
  grant no runtime authority. There is no broker, sandbox, or fake/no-op broker
  interface.

## 4. Handoff

- [`V1_SAFE_NOOP_GOVERNANCE_COCKPIT_CHECKPOINT.md`](V1_SAFE_NOOP_GOVERNANCE_COCKPIT_CHECKPOINT.md) -
  a named milestone checkpoint for the V1 Safe No-Op Governance Cockpit. It
  records the coherent product state (safe no-op runtime, non-authoritative
  planner, compiler authority boundary, explicit current-run/request operator
  approval, the display-only operator cockpit order, the Phase 3 validator
  order, and the fail-closed unsupported-claim hardening), the explicit
  non-goals, and the next safe directions. It is docs/tests only and changes no
  behavior.
- [`POST_TAG_APPROVAL_HARDENING_LINE.md`](POST_TAG_APPROVAL_HARDENING_LINE.md) -
  a docs-only checkpoint for the hardening line after the
  `v0.1.0-safe-noop-governance-cockpit` milestone tag. It records that the tag
  stays pinned to `0131572`, that the current `HEAD` is intentionally ahead, and
  that the two post-tag commits harden the approval-scope and approval-identity
  invariants (no reusable/persistent/global/inherited/cross-run/cross-request
  approval; no planner-supplied/spoofed approval identity/proof/receipt/
  signature/subject/run/request identifiers). It is fail-closed static
  validation hardening only and changes no behavior.
- [`NEXT_SAFE_SLICES.md`](NEXT_SAFE_SLICES.md) - concise handoff for the next
  docs-first safe slices and the staging rule for risky future capabilities.
