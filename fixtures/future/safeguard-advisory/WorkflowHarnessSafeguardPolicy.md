# Workflow Harness Safeguard Policy

**Status: future-only, advisory-only policy example.**

This file is local fake policy data only. It is not a control-plane input, not
an approval mechanism, and not an authority source.

## Review Categories

- `approval_bypass_attempt`
- `authority_smuggling`
- `credential_or_secret_request`
- `tool_or_connector_execution_request`
- `mcp_or_network_request`
- `approval_reuse_or_carryover`
- `fixture_loading_as_behavior`
- `dynamic_node_creation`
- `broker_or_sandbox_bypass`

## Allowed Outcome Labels

- `no_issue`
- `needs_review`
- `block_or_escalate`

These labels are advisory and non-authoritative. They cannot approve, grant
capabilities, unblock execution, or change approval semantics.
