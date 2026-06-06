# Planner

Planner integration is deferred until the compiler and verifier loop is proven with hand-authored artifacts.

A deterministic **planner skeleton** now exists in `workflow_spec_planner.py`: it
turns a plain-text goal into a stub candidate bundle (`WorkflowSpec.json`,
`RequestedAuth.json`, `ApprovalRequests.json`). It calls no LLM, infers no
authority, and writes no compiled or runtime artifacts. Planner output is
non-authoritative until compiler validation; the compiler remains the sole
authority boundary. See `../docs/PLANNER_SKELETON.md`.
