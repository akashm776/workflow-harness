# Workflow Harness

This is the standalone v1 implementation workspace for the deterministic policy-governed dynamic workflow harness.

Current focus:

1. `M1`: schemas, canonical hashing, revision ids, dependency digest shape
2. `M2`: static compiler validation
3. `M3`: lifecycle and artifact ownership foundation

Primary design inputs:

- `A2A-DYNAMIC-WORKFLOW-SPEC.md`
- `architecture-authority-flow.puml`
- `architecture-artifact-audit.puml`

The planner is intentionally deferred. Initial work should prove the compiler and verifier loop using hand-authored workflow fixtures.
