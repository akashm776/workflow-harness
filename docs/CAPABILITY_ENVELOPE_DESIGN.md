# Capability Envelope Design

**Status: design only. Not implemented.**

This document describes a future node-scoped capability envelope for
`workflow-harness`. It is a design target only. It does not implement
execution, tools, connectors, MCP/network access, sandbox/broker behavior, LLM
planning, dynamic nodes, or real side effects.

## Trust Boundary

- Planner may propose desired tools, skills, prompt templates, and authority,
  but cannot authorize them.
- Compiler remains the sole authority boundary.
- Runtime may eventually invoke an isolated broker/sandbox with
  compiler-produced node-scoped capability envelopes; the broker/sandbox
  enforces the envelope.
- A node should receive no ambient authority.

## Intended Purpose

A future capability envelope is the compiler-produced, node-scoped statement of
exactly what a node may use for one run and one request context. It is the
opposite of ambient access:

- Tool access is explicit per node.
- Skill access is explicit per node.
- Prompt templates are versioned artifacts, not arbitrary planner strings.
- A skill does not automatically imply tool access.
- Capability envelopes must be current-run/request scoped.

## Separation From MCP

Harness governance metadata must remain separate from MCP wire-protocol fields.
Fields such as `connector_id`, `side_effect_class`, `approval_request_id`,
`approval_subject_hash`, broker binding references, and audit/evidence policy
are workflow-harness governance data, not MCP protocol extensions.

Future MCP/tool execution must be broker-mediated and use standard MCP
transports and methods such as `stdio`, Streamable HTTP, `tools/list`,
`tools/call`, `resources/list`, `resources/read`, `prompts/list`, and
`prompts/get`.

## Approval and Authority Limits

- No approval carryover.
- No authority subsumption.
- Capability envelopes must remain current-run/request scoped.
- A future envelope may carry `approval_request_id` and
  `approval_subject_hash`, but only as compiler-produced run-local governance
  references.

## Credential Handling

No credentials should appear in planner output, compiled artifacts, logs,
summaries, or capability envelopes.

## Conceptual Example

The following is conceptual only. It is **not** an executable schema, not a
wire format, and not an implemented artifact.

```json
{
  "run_id": "...",
  "node_id": "retrieve-jira-1",
  "allowed_tools": [
    {
      "connector_id": "jira-readonly",
      "operation": "search_issues",
      "side_effect_class": "read_external",
      "scope": "project:DEMO/read_issues"
    }
  ],
  "allowed_skills": ["jira_issue_summarizer:v1"],
  "allowed_prompt_templates": ["jira_issue_summary_prompt_v1"],
  "allowed_inputs": ["ProgramContext.json"],
  "allowed_outputs": ["JiraDedupeContext.json"],
  "approval_request_id": "...",
  "approval_subject_hash": "...",
  "expires": "end_of_run"
}
```

This example shows the intended shape of a future envelope:

- node-scoped allowed tools
- node-scoped allowed skills
- versioned prompt template references
- explicit input/output artifact boundaries
- run/request-scoped approval references

It does not grant authority by itself and does not imply any direct MCP or tool
execution path.

## Non-Goals

This design does not enable any of the following:

- execution
- tools
- connectors
- MCP/network access
- sandbox/broker behavior
- LLM planning
- dynamic nodes
- real side effects

It is a design-only description of a future compiler-produced authority surface.
