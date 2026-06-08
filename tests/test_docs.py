from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = ROOT / "docs" / "V1_SAFE_NOOP_HARNESS.md"
MILESTONE_STATUS_PATH = ROOT / "docs" / "MILESTONE_STATUS.md"
SECURITY_LIMITS_PATH = ROOT / "docs" / "SECURITY_ASSUMPTIONS_AND_LIMITS.md"
CANONICAL_JSON_PATH = ROOT / "docs" / "CANONICAL_JSON_V1.md"
PLANNER_SKELETON_PATH = ROOT / "docs" / "PLANNER_SKELETON.md"
AUTHORITY_SUBSUMPTION_PATH = ROOT / "docs" / "AUTHORITY_SUBSUMPTION_DESIGN.md"
REAL_EXECUTION_THREAT_MODEL_PATH = ROOT / "docs" / "REAL_EXECUTION_THREAT_MODEL.md"
SIDE_EFFECT_CATALOG_PATH = ROOT / "docs" / "SIDE_EFFECT_CATALOG_DESIGN.md"
TOOL_CONNECTOR_CATALOG_PATH = ROOT / "docs" / "TOOL_CONNECTOR_CATALOG_DESIGN.md"
SANDBOX_BROKER_INTERFACE_PATH = ROOT / "docs" / "SANDBOX_BROKER_INTERFACE_DESIGN.md"
CAPABILITY_ENVELOPE_PATH = ROOT / "docs" / "CAPABILITY_ENVELOPE_DESIGN.md"
DOCS_INDEX_PATH = ROOT / "docs" / "README.md"
SAFE_INNOVATION_DEMO_PATH = ROOT / "docs" / "SAFE_INNOVATION_DEMO.md"


class DocsTests(unittest.TestCase):
    def test_v1_safe_noop_harness_doc_exists_and_mentions_current_operator_surface(
        self,
    ) -> None:
        self.assertTrue(DOC_PATH.exists())
        content = DOC_PATH.read_text(encoding="utf-8")

        self.assertIn("safe_noop_run", content)
        self.assertIn("safe_run_cli", content)
        self.assertIn("run_status_cli", content)
        self.assertIn("inspect_run_directory", content)
        self.assertIn("ExecutionManifest.json", content)
        self.assertIn("ExecutionResult.json", content)
        self.assertIn("AuditLog.jsonl", content)
        self.assertIn("--summary-only", content)
        self.assertIn("--dry-run", content)
        self.assertIn("--check", content)
        self.assertIn("--text", content)
        self.assertIn("--view", content)
        self.assertIn("render_run_status_text", content)
        self.assertIn("render_run_status_view", content)
        self.assertIn("workflow_demo_cli", content)
        self.assertIn("python -m cli.workflow_demo_cli", content)
        self.assertIn("self-contained safe", content)
        self.assertIn('execution_status: "blocked"', content)
        self.assertIn("python -m cli.safe_run_cli", content)
        # Opt-in summary surface and the preserved existence-only boundary.
        self.assertIn("cli.run_status_cli --summary", content)
        self.assertIn("remain existence-only", content)
        self.assertIn("read-only and fail-soft", content)
        # Planner template selection is surfaced in the demo summary.
        self.assertIn("planner_template", content)
        # Optional candidate workflow graph section in the summary.
        self.assertIn("Candidate Workflow", content)
        self.assertIn("display only", content)
        self.assertIn("python -m cli.run_status_cli", content)
        self.assertNotIn("C:\\Users\\", content)
        self.assertNotIn("```powershell", content)

    def test_milestone_status_doc_exists_and_mentions_current_snapshot(self) -> None:
        self.assertTrue(MILESTONE_STATUS_PATH.exists())
        content = MILESTONE_STATUS_PATH.read_text(encoding="utf-8")

        self.assertIn("V1 Safe No-Op Harness", content)
        self.assertIn("399 tests", content)
        self.assertIn("planner skeleton", content)
        self.assertIn("planner/workflow_spec_planner.py", content)
        self.assertIn("cli/planner_check_cli.py", content)
        self.assertIn("non-authoritative until compiler validation", content)
        self.assertIn("safe_run_cli", content)
        self.assertIn("no real execution", content)
        self.assertIn("no authority subsumption", content)
        self.assertIn("no approval carryover", content)
        self.assertIn("no full TUI framework", content)
        self.assertIn("no LLM-backed planner", content)
        # Real execution threat model is referenced as a design-only checkpoint.
        self.assertIn("REAL_EXECUTION_THREAT_MODEL.md", content)
        self.assertIn("design-only checkpoint and is not", content)
        self.assertIn("V1 remains no-op only", content)
        # Side-effect catalog is referenced as a design-only checkpoint.
        self.assertIn("SIDE_EFFECT_CATALOG_DESIGN.md", content)
        self.assertIn("no real tools or connectors", content)
        # Sandbox/broker interface is referenced as a design-only checkpoint.
        self.assertIn("SANDBOX_BROKER_INTERFACE_DESIGN.md", content)
        # Inspection-only side-effect audit event helpers are mentioned.
        self.assertIn("audit/side_effect_audit_event.py", content)
        self.assertIn("pure audit event builders only", content)
        # Pure standalone side-effect catalog schema-shape validator is mentioned.
        self.assertIn("compiler/side_effect_catalog_schema_validator.py", content)
        self.assertIn("pure standalone", content)
        self.assertIn("schema-shape validator", content)
        self.assertIn("not wired into `validate_static_inputs`", content)
        # Pure sandbox/broker contract shape builders are mentioned.
        self.assertIn("broker/sandbox_broker_contract.py", content)
        self.assertIn("pure data-shape builders", content)
        self.assertIn(
            "does not implement a broker, a sandbox, execution", content
        )
        # Example/future-only side-effect catalog fixture is mentioned.
        self.assertIn(
            "fixtures/future/side-effect-catalog/SideEffectCatalog.json", content
        )
        self.assertIn("example/future-only fixture", content)
        self.assertIn("not active governance input", content)
        # End-to-end safe no-op workflow demo CLI is mentioned.
        self.assertIn("cli/workflow_demo_cli.py", content)
        self.assertIn("effective_repo_root", content)
        self.assertIn('execution_status: "blocked"', content)
        # Opt-in read-only run-status summary surface is mentioned.
        self.assertIn("runtime/run_status_summary.py", content)
        self.assertIn("cli.run_status_cli --summary", content)
        self.assertIn("read-only, fail-soft summary", content)
        self.assertIn("remain existence-only and unchanged", content)
        # Deterministic innovation-agent planner template is mentioned.
        self.assertIn("build_innovation_planner_candidate", content)
        self.assertIn("select_planner_candidate", content)
        self.assertIn("planner_template", content)
        # Candidate workflow graph visibility in the opt-in summary.
        self.assertIn("Candidate Workflow", content)
        self.assertIn("display-only proposal data", content)
        # Safe innovation demo example wrapper.
        self.assertIn("examples/safe_innovation_demo.py", content)
        self.assertIn("tests/test_safe_innovation_demo_example.py", content)
        self.assertIn("authority schema hardening", content)
        self.assertIn("compiler/authority_value_validator.py", content)
        self.assertIn("DISALLOWED_AUTHORITY_VALUE", content)
        self.assertIn("WorkflowSpec static schema validation", content)
        self.assertIn("NodeTypeRegistry static schema validation", content)
        self.assertIn("RequestedAuth static schema validation", content)
        self.assertIn("RequestedAuth.json", content)
        self.assertIn("ApprovalRequests static schema validation", content)
        self.assertIn("ApprovalRequests.json", content)
        self.assertIn("ApprovalDecisions static schema validation", content)
        self.assertIn("ApprovalDecisions.json", content)
        self.assertIn(
            "static schema hardening across control-plane inputs is complete",
            content,
        )
        self.assertIn("INVALID_ARTIFACT_SCHEMA", content)
        self.assertIn("authority-value validation", content)
        self.assertIn("schema validation", content)
        self.assertIn("interpretation validation", content)
        self.assertIn("--summary-only", content)
        self.assertIn("--dry-run", content)
        self.assertIn("--check", content)
        self.assertIn("--text", content)
        self.assertIn("--view", content)
        self.assertNotIn("C:\\Users\\", content)

    def test_security_limits_doc_exists_and_mentions_current_boundary(self) -> None:
        self.assertTrue(SECURITY_LIMITS_PATH.exists())
        content = SECURITY_LIMITS_PATH.read_text(encoding="utf-8")

        self.assertIn("No approval carryover", content)
        self.assertIn("No narrowed-authority reuse", content)
        self.assertIn("ambient credentials", content)
        self.assertIn("Canonical JSON", content)
        self.assertIn("approval_subject_hash", content)
        self.assertIn("re-gating", content)
        self.assertIn("Numeric gap is now closed", content)
        self.assertIn("DISALLOWED_AUTHORITY_VALUE", content)
        self.assertIn("RFC 8785", content)
        self.assertIn("INVALID_ARTIFACT_SCHEMA", content)
        self.assertIn(
            "across the control-plane inputs is complete",
            content,
        )
        self.assertIn("NodeTypeRegistry", content)
        self.assertIn("RequestedAuth.json", content)
        self.assertIn("ApprovalRequests.json", content)
        self.assertIn("ApprovalDecisions.json", content)

    def test_canonical_json_v1_doc_exists_and_mentions_current_contract(self) -> None:
        self.assertTrue(CANONICAL_JSON_PATH.exists())
        content = CANONICAL_JSON_PATH.read_text(encoding="utf-8")

        self.assertIn("canonical_json_text", content)
        self.assertIn("canonical_sha256_hex", content)
        self.assertIn("Sort object keys", content)
        self.assertIn("ensure_ascii=False", content)
        self.assertIn("RFC 8785", content)
        self.assertIn("non-finite", content)
        self.assertIn("approval_subject_hash", content)
        self.assertIn("validation-gated", content)
        self.assertIn("compiler/authority_value_validator.py", content)
        self.assertIn("DISALLOWED_AUTHORITY_VALUE", content)

    def test_planner_skeleton_doc_exists_and_marks_output_non_authoritative(
        self,
    ) -> None:
        self.assertTrue(PLANNER_SKELETON_PATH.exists())
        content = PLANNER_SKELETON_PATH.read_text(encoding="utf-8")

        self.assertIn("Planner Skeleton", content)
        self.assertIn("planner/workflow_spec_planner.py", content)
        self.assertIn("build_stub_planner_candidate", content)
        self.assertIn("write_planner_candidate", content)
        self.assertIn("non-authoritative until compiler validation", content)
        self.assertIn("sole authority boundary", content)
        self.assertIn("does not", content)
        self.assertIn("cli/planner_check_cli.py", content)
        self.assertIn("python -m cli.planner_check_cli", content)
        # Deterministic innovation template and whole-word keyword selection.
        self.assertIn("build_innovation_planner_candidate", content)
        self.assertIn("select_planner_candidate", content)
        self.assertIn("innovation-agent", content)
        self.assertIn("whole-word keyword matching", content)
        self.assertIn("not** LLM planning", content)
        self.assertIn("not** dynamic node creation", content)
        self.assertIn("planner_template", content)

    def test_authority_subsumption_design_doc_exists_and_is_design_only(self) -> None:
        self.assertTrue(AUTHORITY_SUBSUMPTION_PATH.exists())
        content = AUTHORITY_SUBSUMPTION_PATH.read_text(encoding="utf-8")

        # Design-only / not implemented.
        self.assertIn("design only", content.lower())
        self.assertIn("not implemented", content.lower())

        # Exact-match remains current behavior; subsumption required before reuse.
        self.assertIn("Exact-Match Approval", content)
        self.assertIn("approval_subject_hash", content)
        self.assertIn("partial order", content)

        # All nine authority dimensions are listed.
        for dimension in (
            "connector",
            "scope",
            "tool",
            "skill",
            "filesystem",
            "side effect",
            "export",
            "review",
            "approval",
        ):
            self.assertIn(dimension, content)

        # All five relation outcomes are defined.
        for outcome in (
            "equal",
            "narrower",
            "broader",
            "incomparable",
            "ambiguous",
        ):
            self.assertIn(outcome, content)

        # The reuse rule and fail-closed default.
        self.assertIn("equal or strictly narrower", content)
        self.assertIn("fails closed", content)
        self.assertIn("new approval is required", content)

        # Refined per-dimension narrowing rules and examples.
        self.assertIn("Per-Dimension Narrowing Rules", content)
        self.assertIn("Examples", content)
        self.assertIn("ambiguous is never narrower", content)
        self.assertIn("no partial credit", content)
        self.assertIn("explicit governed partial order", content)
        self.assertIn("every dimension", content)
        self.assertIn("exact-match approval remains current behavior", content.lower())

    def test_real_execution_threat_model_doc_exists_and_is_design_only(self) -> None:
        self.assertTrue(REAL_EXECUTION_THREAT_MODEL_PATH.exists())
        content = REAL_EXECUTION_THREAT_MODEL_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        # Design-only / not implemented; V1 remains no-op only.
        self.assertIn("design only", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn("no-op only", lowered)

        # Trust boundary: planner untrusted, compiler sole authority boundary.
        self.assertIn("planner remains untrusted", content)
        self.assertIn("compiler remains the sole authority boundary", content)

        # Ambient authority sources.
        self.assertIn("ambient authority", lowered)
        for ambient_source in (
            "environment variables",
            "shell",
            "filesystem",
            "cloud credentials",
            "OAuth tokens",
            "MCP",
            "connector",
            "browser sessions",
        ):
            self.assertIn(ambient_source, content)

        # Sandbox / broker requirement.
        self.assertIn("broker/sandbox", content)
        self.assertIn("isolated", content)

        # Connector / tool allowlist requirement.
        self.assertIn("allowlist", content)
        for allowlist_property in ("declared", "scoped", "versioned", "compiler-approved"):
            self.assertIn(allowlist_property, content)

        # Side-effect classes.
        for side_effect_class in (
            "read-only",
            "local write",
            "external write",
            "network call",
            "export",
            "deletion",
        ):
            self.assertIn(side_effect_class, content)

        # Post-retrieval re-gating, audit, fail-closed, non-goals.
        self.assertIn("Post-Retrieval Re-Gating", content)
        self.assertIn("proposed and every denied side effect must be logged", content)
        self.assertIn("fail closed", lowered)
        self.assertIn("Non-Goals", content)

    def test_side_effect_catalog_design_doc_exists_and_is_design_only(self) -> None:
        self.assertTrue(SIDE_EFFECT_CATALOG_PATH.exists())
        content = SIDE_EFFECT_CATALOG_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        # Design-only / not implemented; V1 remains no-op only.
        self.assertIn("design only", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn("no-op only", lowered)

        # Trust boundary: planner untrusted, compiler sole authority boundary.
        self.assertIn("planner remains untrusted", content)
        self.assertIn("compiler remains the sole authority boundary", content)

        # Side-effect classes.
        for side_effect_class in (
            "read-only",
            "local write",
            "external write",
            "network call",
            "export",
            "deletion",
        ):
            self.assertIn(side_effect_class, content)

        # Entries must be declared / scoped / versioned / compiler-approved.
        for entry_property in ("declared", "scoped", "versioned", "compiler-approved"):
            self.assertIn(entry_property, content)

        # Deny-by-default / fail-closed behavior.
        self.assertIn("deny-by-default", lowered)
        self.assertIn("fail closed", lowered)
        self.assertIn("registry/SideEffectClasses.json", content)
        self.assertIn("does not enable execution or approval", content)

        # Relationships to the other design checkpoints.
        self.assertIn("REAL_EXECUTION_THREAT_MODEL.md", content)
        self.assertIn("AUTHORITY_SUBSUMPTION_DESIGN.md", content)

        # Non-goals.
        self.assertIn("Non-Goals", content)

    def test_tool_connector_catalog_design_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(TOOL_CONNECTOR_CATALOG_PATH.exists())
        content = TOOL_CONNECTOR_CATALOG_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn("design only", lowered)
        self.assertIn("safe no-op only", lowered)
        self.assertIn("MCP/tool servers are **not authority boundaries**", content)
        self.assertIn("Planner may propose tool use but cannot authorize it", content)
        self.assertIn("sole authority boundary", content)
        self.assertIn("Runtime must **not call tools directly**", content)
        self.assertIn("isolated broker/sandbox", content)
        self.assertIn("connector ID", content)
        self.assertIn("operation", content)
        self.assertIn("side-effect class", content)
        self.assertIn("credential requirement", content)
        self.assertIn("requested scope", content)
        self.assertIn("fail closed", lowered)
        self.assertIn("explicit current-run/request approval", content)
        self.assertIn("no approval carryover", lowered)
        self.assertIn("no authority subsumption", lowered)
        self.assertIn("No real connectors in V1 safe no-op", content)
        self.assertIn("No MCP/network calls in the current milestone", content)
        self.assertIn("rejects workflow-node execution bindings", content)
        self.assertIn("tool_binding", content)
        self.assertIn("tool_access", content)
        self.assertIn("connector_access", content)
        self.assertIn("mcp", content)
        self.assertIn("mcp_binding", content)
        self.assertIn("mcp_server", content)
        self.assertIn("mcp_tool", content)
        self.assertIn("not a final MCP schema", content)
        self.assertIn("V1 fail-closed guard", content)
        self.assertIn("preserves compatibility with future standard MCP integration", content)
        self.assertIn("broker-mediated", content)
        self.assertIn("stdio", content)
        self.assertIn("Streamable HTTP", content)
        self.assertIn("tools/list", content)
        self.assertIn("tools/call", content)
        self.assertIn("No credentials should appear in planner output", content)
        self.assertIn("No credentials should appear in compiled artifacts", content)
        self.assertIn("No credentials should appear in logs", content)
        self.assertIn("No credentials should appear in summaries", content)

        for roadmap_item in (
            "proposal-only connector metadata",
            "compiler rejection diagnostics",
            "display-only proposed tool access",
            "fixture-backed fake connector",
            "brokered local mock MCP",
            "brokered read-only real MCP",
            "approved write-capable connector",
        ):
            self.assertIn(roadmap_item, content)

    def test_capability_envelope_design_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(CAPABILITY_ENVELOPE_PATH.exists())
        content = CAPABILITY_ENVELOPE_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn("design only", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn("no ambient authority", lowered)
        self.assertIn("Planner may propose desired tools, skills, prompt templates, and authority,", content)
        self.assertIn("but cannot authorize them", content)
        self.assertIn("Compiler remains the sole authority boundary", content)
        self.assertIn("A skill does not automatically imply tool access", content)
        self.assertIn("Prompt templates are versioned artifacts", content)
        self.assertIn("Harness governance metadata must remain separate from MCP wire-protocol fields", content)
        self.assertIn("broker-mediated", content)
        self.assertIn("stdio", content)
        self.assertIn("Streamable HTTP", content)
        self.assertIn("No credentials should appear in planner output, compiled artifacts, logs,", content)
        self.assertIn("summaries, or capability envelopes", content)
        self.assertIn("No approval carryover", content)
        self.assertIn("No authority subsumption", content)
        self.assertIn("does not implement", lowered)
        self.assertIn("tools", lowered)
        self.assertIn("connectors", lowered)
        self.assertIn("mcp/network", lowered)
        self.assertIn("sandbox/broker behavior", lowered)

    def test_safe_innovation_demo_doc_exists_and_preserves_safety_claims(
        self,
    ) -> None:
        self.assertTrue(SAFE_INNOVATION_DEMO_PATH.exists())
        content = SAFE_INNOVATION_DEMO_PATH.read_text(encoding="utf-8")

        # The two-command walkthrough.
        self.assertIn("python -m cli.workflow_demo_cli", content)
        self.assertIn("python -m cli.run_status_cli", content)
        self.assertIn("--summary", content)

        # Expected results.
        self.assertIn('planner_template: "innovation"', content)
        self.assertIn("compilation_status: compiled", content)
        self.assertIn("execution_status: blocked", content)
        self.assertIn("blocked is expected", content)

        # Preserved safety claims.
        self.assertIn("no real execution", content)
        self.assertIn("no tools", content)
        self.assertIn("no connectors", content)
        self.assertIn("non-authoritative", content)
        self.assertIn("sole authority boundary", content)
        # Visible candidate workflow graph (display-only).
        self.assertIn("Candidate Workflow:", content)
        self.assertIn("retrieve-1 [retrieve] Load Program Data", content)
        self.assertIn("synthesize-3 [synthesize] Synthesize MVP Plans", content)
        self.assertIn("display only", content)
        # Blocked summary includes display-only Review Gate guidance.
        self.assertIn("Review Gate:", content)
        self.assertIn("blocked_reason: review_required", content)
        self.assertIn("approval_request_count: 1", content)
        self.assertIn("approval_request_id:", content)
        self.assertIn("approval request artifact:", content)
        self.assertIn("candidate/ApprovalRequests.json", content)
        self.assertIn("operator guidance only", content)
        self.assertIn("fail-soft for display", content)
        self.assertIn("does **not** validate", content)
        self.assertIn("does **not** approve anything", content)
        self.assertIn("artifact-existence view", content)
        # Explicit approval-decision path: blocked -> approved -> completed.
        self.assertIn("ApprovalDecisions.json", content)
        self.assertIn("safe_run_cli", content)
        self.assertIn("--approval-decisions", content)
        self.assertIn("execution_status: completed", content)
        self.assertIn("completed safe no-op", content)
        self.assertIn("no approval carryover", content)
        self.assertIn("no authority subsumption", content)
        # One-command example wrapper (kept out of cli/).
        self.assertIn("examples.safe_innovation_demo", content)
        self.assertIn(
            "python -m examples.safe_innovation_demo --run-root runs/manual-demo",
            content,
        )
        self.assertIn("--allow-overwrite", content)
        self.assertIn("--demo-approve-current-request", content)
        self.assertIn("review_required: true", content)
        self.assertIn("blocked_by_review: true", content)
        self.assertIn("review_required: false", content)
        self.assertIn("blocked_by_review: false", content)
        self.assertIn("side_effects == []", content)
        self.assertIn("produced_evidence == []", content)
        self.assertIn("current-request only", content)
        self.assertIn("demo-local", content)
        self.assertIn("not a general auto-approval", content)

    def test_docs_index_exists_and_organizes_docs(self) -> None:
        self.assertTrue(DOCS_INDEX_PATH.exists())
        content = DOCS_INDEX_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        # References all major docs.
        for doc_name in (
            "V1_SAFE_NOOP_HARNESS.md",
            "MILESTONE_STATUS.md",
            "CANONICAL_JSON_V1.md",
            "PLANNER_SKELETON.md",
            "SECURITY_ASSUMPTIONS_AND_LIMITS.md",
            "AUTHORITY_SUBSUMPTION_DESIGN.md",
            "REAL_EXECUTION_THREAT_MODEL.md",
            "SIDE_EFFECT_CATALOG_DESIGN.md",
            "TOOL_CONNECTOR_CATALOG_DESIGN.md",
            "CAPABILITY_ENVELOPE_DESIGN.md",
            "SANDBOX_BROKER_INTERFACE_DESIGN.md",
        ):
            self.assertIn(doc_name, content)

        # No-op only / no real execution.
        self.assertIn("no-op only", lowered)
        self.assertIn("no real execution", lowered)

        # Planner non-authoritative, compiler authority boundary.
        self.assertIn("non-authoritative", lowered)
        self.assertIn("compiler remains the sole authority boundary", content)

        # Mentions the safe code surfaces without implying execution.
        self.assertIn("audit/side_effect_audit_event.py", content)
        self.assertIn("compiler/side_effect_catalog_schema_validator.py", content)
        self.assertIn("broker/sandbox_broker_contract.py", content)
        self.assertIn("execute nothing", lowered)
        # Mentions the example/future-only fixtures.
        self.assertIn("fixtures/future/", content)
        self.assertIn("SideEffectCatalog.json", content)
        self.assertIn("example/future-only artifacts", content)
        # Mentions the end-to-end demo CLI.
        self.assertIn("cli/workflow_demo_cli.py", content)

    def test_sandbox_broker_interface_design_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(SANDBOX_BROKER_INTERFACE_PATH.exists())
        content = SANDBOX_BROKER_INTERFACE_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        # Design-only / not implemented; V1 remains no-op only.
        self.assertIn("design only", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn("no-op only", lowered)

        # Trust boundary: planner untrusted, compiler sole authority boundary.
        self.assertIn("planner remains untrusted", content)
        self.assertIn("compiler remains the sole authority boundary", content)

        # Isolation requirements.
        self.assertIn("Isolation Requirements", content)
        for isolation_property in (
            "no inherited environment secrets",
            "no inherited shell",
            "restricted filesystem",
            "restricted network",
            "run-local storage only",
        ):
            self.assertIn(isolation_property, content)

        # Broker input / decision / result contracts.
        self.assertIn("Broker Input Contract", content)
        self.assertIn("Broker Decision Contract", content)
        self.assertIn("Broker Result Contract", content)
        self.assertIn("execution bindings", content)
        self.assertIn("reason code", content)
        self.assertIn("no hidden authority expansion", content)

        # Attestation / sandbox verification.
        self.assertIn("attestation", lowered)
        self.assertIn("verify sandbox state", content)

        # References to the other design checkpoints.
        self.assertIn("REAL_EXECUTION_THREAT_MODEL.md", content)
        self.assertIn("SIDE_EFFECT_CATALOG_DESIGN.md", content)
        self.assertIn("AUTHORITY_SUBSUMPTION_DESIGN.md", content)

        # Deterministic audit and fail-closed behavior.
        self.assertIn("deterministically auditable", content)
        self.assertIn("fails closed", lowered)

        # Non-goals.
        self.assertIn("Non-Goals", content)


if __name__ == "__main__":
    unittest.main()
