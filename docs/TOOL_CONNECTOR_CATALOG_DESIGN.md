# Tool / Connector Catalog Design

This document is **design only**. It does not implement tool execution,
connector access, MCP integration, broker behavior, sandboxing, runtime
execution, or compiler enforcement. V1 remains **safe no-op only**.

## Trust Boundary

- MCP/tool servers are **not authority boundaries**.
- Planner may propose tool use but cannot authorize it.
- Compiler remains the **sole authority boundary**.
- Runtime must **not call tools directly**.
- Future tool execution must go through an **isolated broker/sandbox**.

## Proposed Connector Declaration Model

Any future connector access must be declared in compiler-governed metadata by:

- connector ID
- operation
- side-effect class
- credential requirement
- requested scope

Unknown connectors, unknown operations, or unknown side-effect classes must
**fail closed**.

External read/write access requires **explicit current-run/request approval**.
There is **no approval carryover** and **no authority subsumption**.

## Credential and Data Handling

- No credentials should appear in planner output.
- No credentials should appear in compiled artifacts.
- No credentials should appear in logs.
- No credentials should appear in summaries.

Planner output remains proposal data only. A planner may describe desired tool
or connector access, but it must not embed secrets, tokens, session material, or
credential-bearing connection details.

## Current Milestone Limits

- No real connectors in V1 safe no-op.
- No MCP/network calls in the current milestone.
- No broker or sandbox implementation is enabled.
- No runtime tool invocation is enabled.

Current V1 safe no-op also rejects workflow-node execution bindings such as
`tool_binding`, `tool_access`, `connector_binding`, `connector_access`,
`broker_binding`, `mcp`, `mcp_binding`, `mcp_server`, or `mcp_tool`. This is
not a final MCP schema. It is a V1 fail-closed guard that rejects node-level
tool/connector/broker/MCP execution intent until broker-mediated execution is
designed and implemented. It preserves compatibility with future standard MCP integration rather than treating workflow-harness policy fields as MCP wire-protocol fields.

Any future MCP support must remain broker-mediated and use standard MCP
transports and methods such as `stdio`, Streamable HTTP, `tools/list`,
`tools/call`, `resources/list`, `resources/read`, `prompts/list`, and
`prompts/get`.

## Fail-Closed Rules

- If connector metadata is missing, execution must fail closed.
- If the requested operation is not declared, execution must fail closed.
- If the side-effect class is not declared, execution must fail closed.
- If approval is required and not explicitly provided for the current
  run/request, execution must fail closed.

These rules are future enforcement goals. They are not active execution
features in the current milestone.

## Staged Roadmap

- proposal-only connector metadata
- compiler rejection diagnostics
- display-only proposed tool access
- fixture-backed fake connector
- brokered local mock MCP
- brokered read-only real MCP
- approved write-capable connector

## Non-Goals

- This document does not authorize any connector.
- This document does not approve any operation.
- This document does not change approval matching semantics.
- This document does not introduce approval carryover.
- This document does not introduce authority subsumption.
- This document does not permit direct runtime MCP/tool calls.
