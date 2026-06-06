# Milestone Status

## Current Milestone

`V1 Safe No-Op Harness`

## Test Status

- `271 tests` passing

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

- `SECURITY_ASSUMPTIONS_AND_LIMITS.md` records the current security boundary and
  the deferred enforcement gaps.
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

## Explicit Non-Goals

- no real execution
- no tools or connectors
- no authority subsumption
- no approval carryover
- no full TUI framework (a dependency-free status view and loop already exist)
- no planner
- no real policy evaluation

## Recommended Next Milestone Options

1. CLI hardening
2. TUI status viewer
3. prompt-to-WorkflowSpec planner
4. first real but sandboxed local tool
