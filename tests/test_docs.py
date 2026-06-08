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
CAPABILITY_ENVELOPE_V1_PATH = ROOT / "docs" / "CAPABILITY_ENVELOPE_V1_DESIGN.md"
AUTHORITY_ARTIFACT_OWNERSHIP_PATH = (
    ROOT / "docs" / "AUTHORITY_ARTIFACT_OWNERSHIP.md"
)
COMPILER_AUTHORIZATION_SUMMARY_PATH = (
    ROOT / "docs" / "COMPILER_AUTHORIZATION_SUMMARY_DESIGN.md"
)
STATIC_VALIDATION_HARDENING_MAP_PATH = (
    ROOT / "docs" / "STATIC_VALIDATION_HARDENING_MAP.md"
)
SAFEGUARD_ADVISORY_PATH = ROOT / "docs" / "SAFEGUARD_ADVISORY_DESIGN.md"
SKILL_PROMPT_REGISTRY_PATH = ROOT / "docs" / "SKILL_PROMPT_REGISTRY_DESIGN.md"
NEXT_SAFE_SLICES_PATH = ROOT / "docs" / "NEXT_SAFE_SLICES.md"
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
        self.assertIn("innovation_review", content)
        self.assertIn("--planner-template innovation_review", content)
        self.assertIn("goal-based selection remains unchanged", content)
        self.assertIn("existing `innovation`", content)
        self.assertIn("remains unchanged", content)
        self.assertIn("retrieve` and `synthesize`", content)
        self.assertIn("dedupe against existing work", content)
        self.assertIn("scoring against a rubric", content)
        self.assertIn("critiquing top ideas", content)
        # Optional candidate workflow graph section in the summary.
        self.assertIn("Candidate Workflow", content)
        self.assertIn("display only", content)
        self.assertIn("examples/safe_innovation_demo.py", content)
        self.assertIn("example-only", content)
        self.assertIn("kept out of `cli/`", content)
        self.assertIn("Review Gate:", content)
        self.assertIn("candidate/ApprovalRequests.json", content)
        self.assertIn("fail-soft for operator guidance only", content)
        self.assertIn("ApprovalDecisions.json", content)
        self.assertIn("current run/request only", content)
        self.assertIn("Fixture Lineage:", content)
        self.assertIn("fixtures/future/innovation-context/", content)
        self.assertIn("already-read candidate workflow metadata only", content)
        self.assertIn("does not load fixture", content)
        self.assertIn("does not make fixtures control-plane inputs", content)
        self.assertIn("Proposed Tool Access:", content)
        self.assertIn("RequestedAuth.json", content)
        self.assertIn("proposal-only", content)
        self.assertIn("does not execute tools", content)
        self.assertIn("does not enable connector support", content)
        self.assertIn("does not change", content)
        self.assertIn("approval semantics", content)
        self.assertIn("Operator Review Packet:", content)
        self.assertIn("already-computed summary fields", content)
        self.assertIn("not a new artifact", content)
        self.assertIn("not approval logic", content)
        self.assertIn("not execution behavior", content)
        self.assertIn("UNSUPPORTED_EXECUTION_BINDING", content)
        self.assertIn("No MCP/network calls", content)
        self.assertIn("No sandbox/broker implementation", content)
        self.assertIn("python -m cli.run_status_cli", content)
        self.assertNotIn("C:\\Users\\", content)
        self.assertNotIn("```powershell", content)

    def test_milestone_status_doc_exists_and_mentions_current_snapshot(self) -> None:
        self.assertTrue(MILESTONE_STATUS_PATH.exists())
        content = MILESTONE_STATUS_PATH.read_text(encoding="utf-8")

        self.assertIn("V1 Safe No-Op Harness", content)
        self.assertIn("477 tests", content)
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
        self.assertIn("fixtures/future/innovation-context/", content)
        self.assertIn("fake local", content)
        self.assertIn("not loaded by", content)
        # End-to-end safe no-op workflow demo CLI is mentioned.
        self.assertIn("cli/workflow_demo_cli.py", content)
        self.assertIn("effective_repo_root", content)
        self.assertIn('execution_status: "blocked"', content)
        self.assertIn("examples/safe_innovation_demo.py", content)
        self.assertIn("example script kept out of `cli/`", content)
        # Opt-in read-only run-status summary surface is mentioned.
        self.assertIn("runtime/run_status_summary.py", content)
        self.assertIn("cli.run_status_cli --summary", content)
        self.assertIn("read-only, fail-soft summary", content)
        self.assertIn("remain existence-only and unchanged", content)
        self.assertIn("Review Gate:", content)
        self.assertIn("candidate/ApprovalRequests.json", content)
        self.assertIn("fail-soft for operator guidance", content)
        self.assertIn("ApprovalDecisions.json", content)
        self.assertIn("current run/request only", content)
        self.assertIn("Fixture Lineage:", content)
        self.assertIn("already-read candidate workflow metadata only", content)
        self.assertIn("does not load fixture contents", content)
        self.assertIn("does not make fixtures control-plane", content)
        self.assertIn("Proposed Tool Access:", content)
        self.assertIn("RequestedAuth.json", content)
        self.assertIn("display-only", content)
        self.assertIn("proposal-only operator guidance", content)
        self.assertIn("does not execute tools", content)
        self.assertIn("does not enable connector support", content)
        self.assertIn("does not change", content)
        self.assertIn("approval semantics", content)
        self.assertIn("Operator Review Packet:", content)
        self.assertIn("already-computed summary fields", content)
        self.assertIn("not a new artifact", content)
        self.assertIn("not approval logic", content)
        self.assertIn("not", content)
        self.assertIn("execution behavior", content)
        # Deterministic innovation-agent planner template is mentioned.
        self.assertIn("build_innovation_planner_candidate", content)
        self.assertIn("select_planner_candidate", content)
        self.assertIn("planner_template", content)
        self.assertIn("innovation_review", content)
        self.assertIn("--planner-template innovation_review", content)
        self.assertIn("default goal-based selection remains unchanged", content)
        self.assertIn("existing `innovation`", content)
        self.assertIn("behavior remains unchanged", content)
        self.assertIn("existing `retrieve` and `synthesize` node types", content)
        self.assertIn("dedupe against existing work", content)
        self.assertIn("scoring against a rubric", content)
        self.assertIn("critiquing top ideas", content)
        self.assertIn("synthesizing MVP plans", content)
        self.assertIn("compiles against the existing simple registry", content)
        # Candidate workflow graph visibility in the opt-in summary.
        self.assertIn("Candidate Workflow", content)
        self.assertIn("display-only proposal data", content)
        # Safe innovation demo example wrapper.
        self.assertIn("examples/safe_innovation_demo.py", content)
        self.assertIn("tests/test_safe_innovation_demo_example.py", content)
        self.assertIn("existing safe innovation demo behavior", content)
        self.assertIn("TOOL_CONNECTOR_CATALOG_DESIGN.md", content)
        self.assertIn("standard MCP transports/methods", content)
        self.assertIn("registry/SideEffectClasses.json", content)
        self.assertIn("UNSUPPORTED_EXECUTION_BINDING", content)
        self.assertIn("CAPABILITY_ENVELOPE_DESIGN.md", content)
        self.assertIn("CAPABILITY_ENVELOPE_V1_DESIGN.md", content)
        self.assertIn("AUTHORITY_ARTIFACT_OWNERSHIP.md", content)
        self.assertIn("COMPILER_AUTHORIZATION_SUMMARY_DESIGN.md", content)
        self.assertIn("STATIC_VALIDATION_HARDENING_MAP.md", content)
        self.assertIn("SAFEGUARD_ADVISORY_DESIGN.md", content)
        self.assertIn("CompilerAuthorizationSummary.example.json", content)
        self.assertIn("CompiledCapabilityEnvelope.example.json", content)
        self.assertIn("UNSUPPORTED_CAPABILITY_ENVELOPE", content)
        self.assertIn("UNSUPPORTED_SECRET_FIELD", content)
        self.assertIn("SafeguardAdvisory.example.json", content)
        self.assertIn("UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM", content)
        self.assertIn("UNSUPPORTED_AUTHORITY_ARTIFACT", content)
        self.assertIn("validate_static_inputs(...)", content)
        self.assertIn("deterministic and fail-closed by", content)
        self.assertIn("secret-field validator", content)
        self.assertIn("capability-envelope validator", content)
        self.assertIn("safeguard-authority-claim validator", content)
        self.assertIn("authority-artifact-ownership validator", content)
        self.assertIn("execution-binding validator", content)
        self.assertIn("graph/scope/approval validators", content)
        self.assertIn("secret-field checks", content)
        self.assertIn("authority-artifact-ownership checks", content)
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
        self.assertIn("no MCP/network calls", content)
        self.assertIn("no sandbox/broker implementation", content)
        self.assertIn("no dynamic node creation", content)
        self.assertIn("no skill/prompt registry implementation", content)
        self.assertIn("no fixture input artifact implementation", content)
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

    def test_capability_envelope_v1_design_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(CAPABILITY_ENVELOPE_V1_PATH.exists())
        content = CAPABILITY_ENVELOPE_V1_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn("design only", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn(
            "Planner may request capabilities, but cannot authorize them",
            content,
        )
        self.assertIn(
            "Compiler is the only future authority boundary",
            content,
        )
        self.assertIn(
            "Runtime/broker may eventually execute only against compiler-approved",
            content,
        )
        self.assertIn("V1 currently does not execute envelopes", content)
        self.assertIn("V1 currently does not grant capabilities", content)
        self.assertIn(
            "V1 currently does not call tools, connectors, or MCP",
            content,
        )
        self.assertIn("must not contain credentials", content)
        self.assertIn("must be node-scoped", content)
        self.assertIn("explicit run scope", content)
        self.assertIn("explicit node scope", content)
        self.assertIn("must be approval-bound", content)
        self.assertIn("must be auditable", content)
        self.assertIn("immutable once compiled", content)
        self.assertIn("broker/sandbox enforcement is out of scope", content)
        self.assertIn("UNSUPPORTED_CAPABILITY_ENVELOPE", content)
        self.assertIn("UNSUPPORTED_SECRET_FIELD", content)
        self.assertIn("does not enable", lowered)
        self.assertIn("tool support", lowered)
        self.assertIn("connector support", lowered)
        self.assertIn("mcp support", lowered)

    def test_authority_artifact_ownership_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(AUTHORITY_ARTIFACT_OWNERSHIP_PATH.exists())
        content = AUTHORITY_ARTIFACT_OWNERSHIP_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn("design only", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn(
            "Planner artifacts may request authority, but they cannot grant authority",
            content,
        )
        self.assertIn("The compiler is the authority boundary", content)
        self.assertIn(
            "Runtime may report results, but it does not invent authority",
            content,
        )
        self.assertIn(
            "Operator approval must remain explicit and current-run/request scoped",
            content,
        )
        self.assertIn(
            "V1 safe no-op does not execute real tools, connectors, or MCP calls",
            content,
        )
        self.assertIn(
            "V1 does not generate compiled capability envelopes yet",
            content,
        )
        self.assertIn(
            "V1 does not consume compiled capability envelopes yet",
            content,
        )
        self.assertIn(
            "V1 does not allow planner-supplied compiler-owned or runtime-owned authority artifacts",
            content,
        )
        self.assertIn(
            "V1 does not allow planner-supplied operator approval artifacts",
            content,
        )
        self.assertIn("UNSUPPORTED_AUTHORITY_ARTIFACT", content)
        self.assertIn("authority_artifact_ownership_validator", content)
        self.assertIn("no real execution", lowered)
        self.assertIn("no tools/connectors", lowered)
        self.assertIn("no mcp/network calls", lowered)

    def test_compiler_authorization_summary_design_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(COMPILER_AUTHORIZATION_SUMMARY_PATH.exists())
        content = COMPILER_AUTHORIZATION_SUMMARY_PATH.read_text(
            encoding="utf-8"
        )
        lowered = content.lower()

        self.assertIn("design-only checkpoint", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn("compiler-owned", content)
        self.assertIn("Planner must not supply it.", content)
        self.assertIn(
            "It is derived only from compiler-validated candidate artifacts.",
            content,
        )
        self.assertIn("requested authority", lowered)
        self.assertIn("blocked authority", lowered)
        self.assertIn("approval-required authority", lowered)
        self.assertIn("unsupported authority", lowered)
        self.assertIn("does not grant runtime", lowered)
        self.assertIn("execution by itself", lowered)
        self.assertIn("does not contain credentials or secrets", lowered)
        self.assertIn("does not replace `ApprovalDecisions.json`", content)
        self.assertIn("does not enable approval carryover", lowered)
        self.assertIn("current run, current request, and current artifact", lowered)
        self.assertIn("never planner-supplied ones", content)
        self.assertIn("safe no-op does not generate or consume this", lowered)
        self.assertIn("summary yet", lowered)
        self.assertIn("no runtime execution", lowered)
        self.assertIn("no broker", lowered)
        self.assertIn("no connector, MCP, or tool calls", content)
        self.assertIn("no model inference", lowered)

    def test_safeguard_advisory_design_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(SAFEGUARD_ADVISORY_PATH.exists())
        content = SAFEGUARD_ADVISORY_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn("design only", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn("advisory only", content)
        self.assertIn("not authority", content)
        self.assertIn("cannot approve", content)
        self.assertIn("cannot grant capabilities", content)
        self.assertIn("cannot unblock execution", content)
        self.assertIn("cannot change approval semantics", content)
        self.assertIn("authority boundary", content)
        self.assertIn("Operator/human approval remains explicit", content)
        self.assertIn("compiler-approved", content)
        self.assertIn("V1 does not call any safeguard model", content)
        self.assertIn("V1 does not download any model", content)
        self.assertIn("OpenAI API", content)
        self.assertIn("Ollama", content)
        self.assertIn("vLLM", content)
        self.assertIn("LM Studio", content)
        self.assertIn("Transformers", content)
        self.assertIn("local inference", content)
        self.assertIn("warn, block/escalate, or add review findings", content)
        self.assertIn("may never approve, authorize, grant capabilities, or execute", content)
        self.assertIn("Do not depend on hidden chain-of-thought", content)
        self.assertIn("UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM", content)

    def test_static_validation_hardening_map_doc_exists_and_records_current_order(
        self,
    ) -> None:
        self.assertTrue(STATIC_VALIDATION_HARDENING_MAP_PATH.exists())
        content = STATIC_VALIDATION_HARDENING_MAP_PATH.read_text(
            encoding="utf-8"
        )
        lowered = content.lower()

        self.assertIn("docs-only", lowered)
        self.assertIn("validate_static_inputs(...)", content)
        self.assertIn("not a public API", content)
        self.assertIn("Phase 1: authority-value validation", content)
        self.assertIn(
            "Rejects invalid authority-bearing values before semantic interpretation.",
            content,
        )
        self.assertIn("DISALLOWED_AUTHORITY_VALUE", content)
        self.assertIn("Phase 2: schema validation", content)
        self.assertIn(
            "Rejects malformed control-plane artifacts before graph, scope, or approval",
            content,
        )
        self.assertIn("INVALID_ARTIFACT_SCHEMA", content)
        self.assertIn("Phase 3: interpretation validation", content)
        self.assertIn(
            "1. secret-field validator\n"
            "2. capability-envelope validator\n"
            "3. safeguard-authority-claim validator\n"
            "4. authority-artifact-ownership validator\n"
            "5. execution-binding validator\n"
            "6. graph/scope/approval validators",
            content,
        )

        for diagnostic in (
            "UNSUPPORTED_SECRET_FIELD",
            "UNSUPPORTED_CAPABILITY_ENVELOPE",
            "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
            "UNSUPPORTED_AUTHORITY_ARTIFACT",
            "UNSUPPORTED_EXECUTION_BINDING",
        ):
            self.assertIn(diagnostic, content)

        for rule in (
            "Prefer exact-key rejection for early hardening.",
            "Never grant authority.",
            "Never add execution in a validator.",
            "Never call tools, connectors, MCP, network, or models from validation.",
            "Do not scan arbitrary prose unless explicitly designed and tested.",
            "Place new validators according to ownership and diagnostic order.",
            "Update ordering tests when order changes.",
            "Keep validation deterministic and fail-closed.",
        ):
            self.assertIn(rule, content)

        for non_goal in (
            "no real execution",
            "no connector/MCP/tool calls",
            "no model inference",
            "no broker/sandbox",
            "no approval carryover",
            "no authority subsumption",
            "no canonical JSON/hashing changes",
        ):
            self.assertIn(non_goal, content)

    def test_skill_prompt_registry_design_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(SKILL_PROMPT_REGISTRY_PATH.exists())
        content = SKILL_PROMPT_REGISTRY_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn("design only", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn(
            "Planner may propose desired skills and prompt intent, but cannot authorize",
            content,
        )
        self.assertIn(
            "Arbitrary planner prompts must not become executable prompts",
            content,
        )
        self.assertIn("Prompt templates are versioned, reviewed artifacts", content)
        self.assertIn("Skills are versioned, reviewed artifacts", content)
        self.assertIn("A skill does not automatically imply tool access", content)
        self.assertIn("Tool access remains explicit per node/capability envelope", content)
        self.assertIn("Skill access remains explicit per node/capability envelope", content)
        self.assertIn(
            "Prompt-template access remains explicit per node/capability envelope",
            content,
        )
        self.assertIn("broker/sandbox mediated", content)
        self.assertIn("allowed inputs", content)
        self.assertIn("allowed outputs", content)
        self.assertIn("model policy", content)
        self.assertIn("prompt template", content)
        self.assertIn("tool policy", content)
        self.assertIn("allowed variables", content)
        self.assertIn("output schema", content)
        self.assertIn("version/hash", content)
        self.assertIn("forbidden content", content)
        self.assertIn("No credentials in planner output, prompt templates,", content)
        self.assertIn("compiled artifacts, logs,", content)
        self.assertIn("summaries, or capability envelopes", content)
        self.assertIn("No approval carryover", content)
        self.assertIn("No authority subsumption", content)
        self.assertIn("does not enable", lowered)
        self.assertIn("llm planning", lowered)
        self.assertIn("dynamic skills", lowered)
        self.assertIn("prompt execution", lowered)
        self.assertIn("tools", lowered)
        self.assertIn("connectors", lowered)
        self.assertIn("mcp/network", lowered)
        self.assertIn("sandbox/broker behavior", lowered)
        self.assertIn("real execution", lowered)

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

    def test_next_safe_slices_doc_exists_and_preserves_boundaries(self) -> None:
        self.assertTrue(NEXT_SAFE_SLICES_PATH.exists())
        content = NEXT_SAFE_SLICES_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn(
            "Baseline before this handoff slice: f7de8c4 Update safe noop milestone status",
            content,
        )
        self.assertIn(
            "Implementation checkpoint before this safeguard-advisory slice: 6c81a23 Reject unsupported capability envelopes",
            content,
        )
        self.assertIn(
            "Implementation checkpoint before this authority-artifact slice: 4d9a468 Document static validation diagnostic order",
            content,
        )
        self.assertIn(
            "Implementation checkpoint before this secret-field slice: 51a214f Reject unsupported authority artifacts",
            content,
        )
        self.assertIn(
            "Implementation checkpoint before this hardening-map slice: 0ae585c Reject unsupported secret fields",
            content,
        )
        self.assertIn(
            "Implementation checkpoint before this authorization-summary slice: 2bac7e4 Document static validation hardening map",
            content,
        )
        self.assertIn("V1 remains safe no-op only", content)
        self.assertIn("477 tests passing", content)
        self.assertIn("proposal-only skill/prompt registry design", content)
        self.assertIn("explicit deterministic `innovation_review` template", content)
        self.assertIn("inert future-only innovation context fixtures", content)
        self.assertIn("display-only fixture lineage for `innovation_review` summary", content)
        self.assertIn("display-only proposed tool access for `innovation_review` summary", content)
        self.assertIn("display-only Operator Review Packet for blocked summaries", content)
        self.assertIn("capability envelope V1 design checkpoint", content)
        self.assertIn("inert future-only capability envelope example fixture", content)
        self.assertIn("fail-closed unsupported capability envelope rejection", content)
        self.assertIn("safeguard advisory design checkpoint", content)
        self.assertIn("inert future-only safeguard advisory fixtures", content)
        self.assertIn("fail-closed unsupported safeguard authority-claim rejection", content)
        self.assertIn("authority artifact ownership contract", content)
        self.assertIn("fail-closed unsupported authority artifact rejection", content)
        self.assertIn("fail-closed unsupported secret field rejection", content)
        self.assertIn("static validation hardening map", content)
        self.assertIn("compiler authorization summary design", content)
        self.assertIn("inert future-only compiler authorization summary fixture", content)
        self.assertIn("fixtures/future/innovation-context/", content)
        self.assertIn(
            "fixtures/future/capability-envelope/CompiledCapabilityEnvelope.example.json",
            content,
        )
        self.assertIn(
            "fixtures/future/compiler-authorization-summary/CompilerAuthorizationSummary.example.json",
            content,
        )
        self.assertIn(
            "fixtures/future/safeguard-advisory/SafeguardAdvisory.example.json",
            content,
        )
        self.assertIn("does not load them", content)
        self.assertIn("connect to tools/connectors/MCP", content)
        self.assertIn("--planner-template innovation_review", content)
        self.assertIn("Default goal-based", content)
        self.assertIn("existing `innovation`", content)
        self.assertIn("behavior remains unchanged", content)
        self.assertIn("existing safe innovation demo", content)
        self.assertIn("behavior", content)

        self.assertIn(
            "No new next safe slice is recorded in this handoff", content
        )

        for boundary in (
            "Display-only fixture lineage is now implemented",
            "`cli.run_status_cli --summary` now shows known future fixture paths as",
            "Display-only proposed tool access is now implemented",
            "Display-only Operator Review Packet is now implemented",
            "Capability envelope V1 design is now documented",
            "planner requests remain",
            "only the compiler may eventually produce compiled envelopes",
            "display-only, not executable, compiler-owned example data only",
            "UNSUPPORTED_SECRET_FIELD",
            "UNSUPPORTED_CAPABILITY_ENVELOPE",
            "does not generate",
            "does not consume",
            "Fail-closed unsupported secret-field rejection is now implemented",
            "exact secret-like key names",
            "does not scan arbitrary",
            "does not add credential storage",
            "Safeguard advisory design is now documented",
            "advisory only",
            "cannot approve",
            "cannot grant capabilities",
            "cannot unblock execution",
            "V1 does not call, download, or run any safeguard model",
            "WorkflowHarnessSafeguardPolicy.md",
            "SafeguardAdvisory.example.json",
            "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
            "does not add API/network behavior",
            "Authority artifact ownership is now documented",
            "AUTHORITY_ARTIFACT_OWNERSHIP.md",
            "planner proposals only",
            "compiler-owned and runtime-owned authority artifacts",
            "current-run/request scoped",
            "UNSUPPORTED_AUTHORITY_ARTIFACT",
            "compiled plans/manifests",
            "runtime results",
            "audit or evidence artifacts",
            "approval-decision artifacts",
            "does not create",
            "does not consume compiled artifacts",
            "RequestedAuth.json",
            "shows proposed tools and connector metadata as display-only",
            "blocked safe no-op runs",
            "derived only from already-computed summary fields",
            "does not change approval logic",
            "does not change execution",
            "fixtures/future/innovation-context/ProgramContext.json",
            "fixtures/future/innovation-context/RepoContextSummary.json",
            "fixtures/future/innovation-context/ConfluenceContextSummary.json",
            "fixtures/future/innovation-context/IssueTrackerContextSummary.json",
            "fixtures/future/innovation-context/Rubric.json",
            "no fixture loading",
            "no fixture content loading",
            "not control-plane inputs",
            "no planner/compiler/runtime behavior",
            "no connector/MCP/tools",
            "no authority or approval changes",
            "no fixture-driven planning",
            "fail-soft and operator-facing only",
            "proposal-only",
            "no tool execution",
            "no connector support",
            "no approval semantics changes",
            "it is not a new artifact",
            "it is not approval logic",
            "it is not execution behavior",
            "no authority is granted",
            "STATIC_VALIDATION_HARDENING_MAP.md",
            "Phase 1 authority-value",
            "Phase 2 schema validation",
            "Phase 3 interpretation",
            "secret-field, capability-envelope, safeguard-authority-claim",
            "UNSUPPORTED_EXECUTION_BINDING",
            "deterministic and fail-closed",
            "changes no compiler",
            "COMPILER_AUTHORIZATION_SUMMARY_DESIGN.md",
            "compiler-owned authorization summary",
            "requested authority, blocked authority, approval-required authority",
            "does not replace `ApprovalDecisions.json`",
            "current run/request/artifact revision",
            "safe no-op does not generate or consume it yet",
            "CompilerAuthorizationSummary.example.json",
            "not consumed by V1",
            "grants no runtime authority",
        ):
            self.assertIn(boundary, content)

        for non_goal in (
            "no real execution",
            "no tools/connectors",
            "no MCP/network calls",
            "no sandbox/broker implementation",
            "no LLM planning",
            "no dynamic node creation",
            "no approval carryover",
            "no authority subsumption",
            "no approval matching semantics changes",
            "no canonical JSON/hashing changes",
            "compiler/canonical_json.py",
        ):
            self.assertIn(non_goal, content)

        self.assertIn(
            "Every risky future capability should first appear as a design doc",
            content,
        )
        self.assertIn("before any execution path exists", content)
        self.assertIn("changes no behavior and enables nothing", lowered)

    def test_docs_index_exists_and_organizes_docs(self) -> None:
        self.assertTrue(DOCS_INDEX_PATH.exists())
        content = DOCS_INDEX_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        # References all major docs.
        for doc_name in (
            "V1_SAFE_NOOP_HARNESS.md",
            "MILESTONE_STATUS.md",
            "NEXT_SAFE_SLICES.md",
            "CANONICAL_JSON_V1.md",
            "PLANNER_SKELETON.md",
            "SECURITY_ASSUMPTIONS_AND_LIMITS.md",
            "AUTHORITY_SUBSUMPTION_DESIGN.md",
            "REAL_EXECUTION_THREAT_MODEL.md",
            "SIDE_EFFECT_CATALOG_DESIGN.md",
            "TOOL_CONNECTOR_CATALOG_DESIGN.md",
            "CAPABILITY_ENVELOPE_DESIGN.md",
            "CAPABILITY_ENVELOPE_V1_DESIGN.md",
            "AUTHORITY_ARTIFACT_OWNERSHIP.md",
            "COMPILER_AUTHORIZATION_SUMMARY_DESIGN.md",
            "STATIC_VALIDATION_HARDENING_MAP.md",
            "SAFEGUARD_ADVISORY_DESIGN.md",
            "SKILL_PROMPT_REGISTRY_DESIGN.md",
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
        self.assertIn("CompiledCapabilityEnvelope.example.json", content)
        self.assertIn("CompilerAuthorizationSummary.example.json", content)
        self.assertIn("SafeguardAdvisory.example.json", content)
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
