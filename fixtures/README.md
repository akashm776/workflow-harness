# Fixtures

Golden fixtures are the source-of-truth test inputs for the workflow-harness control plane.

## Contract

- Add golden fixtures:
  - `fixtures/valid/simple-workflow/`
  - `fixtures/valid/approval-required-workflow/`
  - `fixtures/valid/evidence-refresh-rerun/`
  - `fixtures/invalid/unknown-node-type/`
  - `fixtures/invalid/missing-scope/`
  - `fixtures/invalid/illegal-cycle/`
  - `fixtures/invalid/stale-compiled-index/`
  - `fixtures/invalid/approval-subject-changed/`
  - `fixtures/invalid/no-ambient-authority/`
  - `fixtures/invalid/policy-bundle-changed/`
  - `fixtures/invalid/wrong-artifact-owner/`

## Shape

Every valid fixture must use:

```text
fixtures/valid/<name>/
  input/
  expected/
```

Every invalid fixture must use:

```text
fixtures/invalid/<name>/
  input/
  expected/
    error.json
```

## Expected Error Contract

Each invalid fixture `expected/error.json` must contain at least:

```json
{
  "expected_error_code": "STABLE_MACHINE_CODE",
  "expected_component": "component_name",
  "expected_artifact": "ArtifactName.json",
  "expected_message_fragment": "stable human-readable fragment"
}
```

## M1 Scope

Before compiler behavior is implemented, fixtures are used to prove:

- schema correctness
- canonical hashing behavior
- revision-id determinism
- dependency-digest shape stability
- artifact ownership boundaries

Policy compilation, approval resolution, and runtime side effects are out of scope for fixture behavior in early M1.
