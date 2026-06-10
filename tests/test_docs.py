from __future__ import annotations

import json
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
SANDBOX_BACKEND_STRATEGY_PATH = ROOT / "docs" / "SANDBOX_BACKEND_STRATEGY.md"
WORKFLOW_PATTERN_SELECTION_PATH = (
    ROOT / "docs" / "WORKFLOW_PATTERN_SELECTION_DESIGN.md"
)
REPO_TERMINOLOGY_MAP_PATH = ROOT / "docs" / "REPO_TERMINOLOGY_MAP.md"
CAPABILITY_ENVELOPE_PATH = ROOT / "docs" / "CAPABILITY_ENVELOPE_DESIGN.md"
CAPABILITY_ENVELOPE_V1_PATH = ROOT / "docs" / "CAPABILITY_ENVELOPE_V1_DESIGN.md"
AUTHORITY_ARTIFACT_OWNERSHIP_PATH = (
    ROOT / "docs" / "AUTHORITY_ARTIFACT_OWNERSHIP.md"
)
COMPILER_AUTHORIZATION_SUMMARY_PATH = (
    ROOT / "docs" / "COMPILER_AUTHORIZATION_SUMMARY_DESIGN.md"
)
COMPILER_AUTHORIZATION_SUMMARY_PROJECTION_PATH = (
    ROOT / "docs" / "COMPILER_AUTHORIZATION_SUMMARY_PROJECTION.md"
)
STATIC_VALIDATION_HARDENING_MAP_PATH = (
    ROOT / "docs" / "STATIC_VALIDATION_HARDENING_MAP.md"
)
SAFEGUARD_ADVISORY_PATH = ROOT / "docs" / "SAFEGUARD_ADVISORY_DESIGN.md"
SKILL_PROMPT_REGISTRY_PATH = ROOT / "docs" / "SKILL_PROMPT_REGISTRY_DESIGN.md"
APPROVAL_BINDING_CONTRACT_PATH = ROOT / "docs" / "APPROVAL_BINDING_CONTRACT.md"
APPROVAL_BINDING_FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "future"
    / "approval-binding"
    / "ApprovalBinding.example.json"
)
EVIDENCE_LINEAGE_VERIFIER_OUTPUT_CONTRACT_PATH = (
    ROOT / "docs" / "EVIDENCE_LINEAGE_VERIFIER_OUTPUT_CONTRACT.md"
)
EVIDENCE_LINEAGE_FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "future"
    / "evidence-lineage"
    / "EvidenceLineage.example.json"
)
VERIFIER_OUTPUT_FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "future"
    / "verifier-output"
    / "VerifierOutput.example.json"
)
NOOP_BROKER_BOUNDARY_CONTRACT_PATH = (
    ROOT / "docs" / "NOOP_BROKER_BOUNDARY_CONTRACT.md"
)
BROKER_REQUEST_FIXTURE_PATH = (
    ROOT / "fixtures" / "future" / "noop-broker" / "BrokerRequest.example.json"
)
BROKER_DECISION_FIXTURE_PATH = (
    ROOT / "fixtures" / "future" / "noop-broker" / "BrokerDecision.example.json"
)
BROKER_RESULT_FIXTURE_PATH = (
    ROOT / "fixtures" / "future" / "noop-broker" / "BrokerResult.example.json"
)
OPERATOR_COCKPIT_CONTRACT_PATH = (
    ROOT / "docs" / "OPERATOR_COCKPIT_CONTRACT.md"
)
STATIC_VALIDATION_ORDERING_CONTRACT_PATH = (
    ROOT / "docs" / "STATIC_VALIDATION_ORDERING_CONTRACT.md"
)
V1_GOVERNANCE_COCKPIT_CHECKPOINT_PATH = (
    ROOT / "docs" / "V1_SAFE_NOOP_GOVERNANCE_COCKPIT_CHECKPOINT.md"
)
POST_TAG_APPROVAL_HARDENING_LINE_PATH = (
    ROOT / "docs" / "POST_TAG_APPROVAL_HARDENING_LINE.md"
)
PHASE3_VALIDATOR_OWNERSHIP_MAP_PATH = (
    ROOT / "docs" / "PHASE3_VALIDATOR_OWNERSHIP_MAP.md"
)
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
        self.assertIn("Approval Binding Summary:", content)
        self.assertIn("not reusable authority", content)
        self.assertIn("no approval carryover", content)
        self.assertIn("UNSUPPORTED_APPROVAL_BINDING", content)
        self.assertIn("Verifier / Evidence Status:", content)
        self.assertIn("reporting-only", content)
        self.assertIn("verification_status: not_implemented", content)
        self.assertIn("EvidenceLineage.json", content)
        self.assertIn("VerifierOutput.json", content)
        self.assertIn("Broker Boundary Status:", content)
        self.assertIn("no broker implementation", content)
        self.assertIn("no sandbox implementation", content)
        self.assertIn("BrokerRequest.json", content)
        self.assertIn("BrokerDecision.json", content)
        self.assertIn("BrokerResult.json", content)
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
        self.assertIn("569 tests", content)
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
        self.assertIn("Compiler Authorization Projection:", content)
        self.assertIn("already-read `EffectivePolicy.json`", content)
        self.assertIn("CompilationReport.json", content)
        self.assertIn("compiler-owned summary metadata only", content)
        self.assertIn("not persisted as an artifact", content)
        self.assertIn("does not load future fixtures", content)
        self.assertIn("does not write artifacts", content)
        self.assertIn("change approval resolution", content)
        self.assertIn("display-only summary contract only", content)
        self.assertIn("not an artifact-generation milestone", content)
        self.assertIn("Approval Binding Summary:", content)
        self.assertIn("approval_binding_summary", content)
        self.assertIn("UNSUPPORTED_APPROVAL_BINDING", content)
        self.assertIn("Verifier / Evidence Status:", content)
        self.assertIn("verifier_evidence_status", content)
        self.assertIn("verification_status: not_implemented", content)
        self.assertIn("Broker Boundary Status:", content)
        self.assertIn("broker_boundary_status", content)
        self.assertIn("sandbox_status: not_implemented", content)
        self.assertIn("Operator Review Packet:", content)
        self.assertIn("already-computed summary fields", content)
        self.assertIn("compiler_authorization_projection", content)
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
        self.assertIn("COMPILER_AUTHORIZATION_SUMMARY_PROJECTION.md", content)
        self.assertIn("STATIC_VALIDATION_HARDENING_MAP.md", content)
        self.assertIn("SAFEGUARD_ADVISORY_DESIGN.md", content)
        self.assertIn("CompilerAuthorizationSummary.example.json", content)
        self.assertIn("CompilerAuthorizationSummaryProjection.example.json", content)
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

    def test_compiler_authorization_summary_projection_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(COMPILER_AUTHORIZATION_SUMMARY_PROJECTION_PATH.exists())
        content = COMPILER_AUTHORIZATION_SUMMARY_PROJECTION_PATH.read_text(
            encoding="utf-8"
        )
        lowered = content.lower()

        self.assertIn("design-only checkpoint", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn("compiler-validated `RequestedAuth.json`", content)
        self.assertIn("compiler-validated `ApprovalRequests.json`", content)
        self.assertIn("static validation diagnostics", lowered)
        self.assertIn("current run, request, and artifact revision context", lowered)
        self.assertIn("`requested_authority`", content)
        self.assertIn("`approval_required`", content)
        self.assertIn("`blocked_authority`", content)
        self.assertIn("`unsupported_authority`", content)
        self.assertIn("validated requested scopes or", lowered)
        self.assertIn("capabilities only", lowered)
        self.assertIn("explicit approval requests only", lowered)
        self.assertIn("missing approvals", lowered)
        self.assertIn("policy rejection", lowered)
        for diagnostic in (
            "UNSUPPORTED_SECRET_FIELD",
            "UNSUPPORTED_CAPABILITY_ENVELOPE",
            "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
            "UNSUPPORTED_AUTHORITY_ARTIFACT",
            "UNSUPPORTED_EXECUTION_BINDING",
        ):
            self.assertIn(diagnostic, content)
        self.assertIn("Projection is deterministic.", content)
        self.assertIn("Projection does not grant authority.", content)
        self.assertIn("Projection does not execute.", content)
        self.assertIn(
            "Projection does not call tools, connectors, MCP, network, or models.",
            content,
        )
        self.assertIn("Projection does not read secrets.", content)
        self.assertIn("Projection does not replace `ApprovalDecisions.json`.", content)
        self.assertIn("Projection does not enable approval carryover.", content)
        self.assertIn("current run, current request, and current", lowered)
        self.assertIn("artifact revision only", lowered)
        self.assertIn("does not generate or consume this projection", lowered)
        self.assertIn("no compiler generation yet", lowered)
        self.assertIn("no runtime consumption", lowered)
        self.assertIn("no planner behavior changes", lowered)
        self.assertIn("no cli rendering", lowered)
        self.assertIn("no execution", lowered)
        self.assertIn("no tool, connector, mcp, or network behavior", lowered)
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
            "5. approval-binding validator\n"
            "6. execution-binding validator\n"
            "7. runtime-reporting-boundary validator\n"
            "8. audit-evidence-authority validator\n"
            "9. approval-scope validator\n"
            "10. approval-identity validator\n"
            "11. graph/scope/approval validators",
            content,
        )

        for diagnostic in (
            "UNSUPPORTED_SECRET_FIELD",
            "UNSUPPORTED_CAPABILITY_ENVELOPE",
            "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
            "UNSUPPORTED_AUTHORITY_ARTIFACT",
            "UNSUPPORTED_APPROVAL_BINDING",
            "UNSUPPORTED_EXECUTION_BINDING",
            "UNSUPPORTED_RUNTIME_REPORTING_CLAIM",
            "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
            "UNSUPPORTED_APPROVAL_SCOPE_CLAIM",
            "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM",
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
        self.assertIn(
            "Implementation checkpoint before this projection slice: 07c100e Document compiler authorization summary design",
            content,
        )
        self.assertIn(
            "Implementation checkpoint before this display-only compiler-authorization-projection slice: af7ca95 Document compiler authorization summary projection",
            content,
        )
        self.assertIn("V1 remains safe no-op only", content)
        self.assertIn("569 tests passing", content)
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
        self.assertIn("compiler authorization summary projection design", content)
        self.assertIn("inert future-only compiler authorization summary projection fixture", content)
        self.assertIn(
            "display-only compiler authorization projection for blocked `innovation_review` summaries",
            content,
        )
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
            "fixtures/future/compiler-authorization-summary/CompilerAuthorizationSummaryProjection.example.json",
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

        self.assertIn("post-tag approval hardening-line checkpoint", content)
        self.assertIn("POST_TAG_APPROVAL_HARDENING_LINE.md", content)
        self.assertIn(
            "recommended direction is consolidation", content
        )
        self.assertIn(
            "do not add new validators\nunless an explicit, reviewed safety "
            "need is identified",
            content,
        )

        for boundary in (
            "Display-only fixture lineage is now implemented",
            "`cli.run_status_cli --summary` now shows known future fixture paths as",
            "Display-only proposed tool access is now implemented",
            "Display-only compiler authorization projection is now implemented",
            "already-read `EffectivePolicy.json`",
            "existing `CompilationReport.json` diagnostics",
            "compiler-owned summary metadata only",
            "not persisted as an artifact",
            "does not load future fixtures",
            "does not write artifacts",
            "does not change approval resolution",
            "display-only summary contract only",
            "artifact-generation",
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
            "COMPILER_AUTHORIZATION_SUMMARY_PROJECTION.md",
            "compiler-validated `RequestedAuth.json`",
            "compiler-validated `ApprovalRequests.json`",
            "static validation diagnostics",
            "`requested_authority`, `approval_required`, `blocked_authority`, and",
            "`unsupported_authority`",
            "projection is deterministic",
            "projection is deterministic and non-authoritative",
            "does not generate or consume the projection yet",
            "CompilerAuthorizationSummaryProjection.example.json",
            "not generated by V1",
            "Compiler Authorization Projection:",
            "display-only compiler authorization projection",
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

    def test_approval_binding_contract_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(APPROVAL_BINDING_CONTRACT_PATH.exists())
        content = APPROVAL_BINDING_CONTRACT_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        # Status: design/contract documentation only; V1 does not use approvals
        # for real execution.
        self.assertIn(
            "design/contract documentation only unless otherwise stated", lowered
        )
        self.assertIn(
            "v1 safe no-op does not use approvals for real execution", lowered
        )

        # Ownership and form.
        self.assertIn("Approvals are operator-owned.", content)
        self.assertIn("Approvals are explicit.", content)
        self.assertIn("Approvals are current-run scoped.", content)
        self.assertIn("Approvals are current-request scoped.", content)

        # Binding rules.
        self.assertIn("Approvals bind to the approval subject.", content)
        self.assertIn(
            "Approvals should bind to candidate artifact revision/digest where "
            "available.",
            content,
        )
        self.assertIn(
            "Approvals should bind to requested authority shape where available.",
            content,
        )

        # Authority boundaries.
        self.assertIn(
            "Approvals do not grant authority outside the current request.", content
        )
        self.assertIn("Approvals do not carry over across runs.", content)
        self.assertIn("Approvals are not reusable ambient authority.", content)
        self.assertIn(
            "Approvals do not authorize planner-supplied compiled artifacts.",
            content,
        )
        self.assertIn(
            "Approvals do not authorize runtime/broker behavior unless future",
            content,
        )
        self.assertIn(
            "Future broker/sandbox execution must require compiler-owned "
            "authority plus",
            content,
        )

        # Authority boundary roles remain unchanged.
        self.assertIn("Planner remains non-authoritative.", content)
        self.assertIn("Compiler remains the sole authority boundary.", content)
        self.assertIn("Runtime remains safe no-op in V1.", content)

        # V1 non-goals: explicitly not implemented here.
        for non_goal in (
            "approval carryover",
            "authority subsumption",
            "broker execution",
            "MCP/tool calls",
            "model inference",
            "credential/secret handling",
        ):
            self.assertIn(non_goal, content)

    def test_approval_binding_example_fixture_is_inert_future_only(self) -> None:
        self.assertTrue(APPROVAL_BINDING_FIXTURE_PATH.exists())
        data = json.loads(
            APPROVAL_BINDING_FIXTURE_PATH.read_text(encoding="utf-8")
        )

        # Inert, future-only, operator-owned, and not consumed by V1.
        self.assertEqual(data["schema_version"], "approval-binding.v1.example")
        self.assertTrue(data["display_only"])
        self.assertTrue(data["future_only_example"])
        self.assertTrue(data["operator_owned"])
        self.assertTrue(data["not_consumed_by_v1"])
        self.assertTrue(data["not_reusable_authority"])
        self.assertTrue(data["no_runtime_authority"])
        self.assertTrue(data["no_execution"])

        # Scoped to the current run/request/subject/revision only.
        self.assertEqual(data["run_scope"], "example-current-run-only")
        self.assertEqual(data["request_scope"], "example-current-request-only")
        self.assertEqual(
            data["approval_subject"], "example-current-approval-subject-only"
        )
        self.assertEqual(
            data["artifact_revision_scope"],
            "example-current-artifact-revision-only",
        )

        # Grants no ambient/requested authority.
        self.assertEqual(data["requested_authority_scope"], [])

    def test_evidence_lineage_verifier_output_contract_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(EVIDENCE_LINEAGE_VERIFIER_OUTPUT_CONTRACT_PATH.exists())
        content = EVIDENCE_LINEAGE_VERIFIER_OUTPUT_CONTRACT_PATH.read_text(
            encoding="utf-8"
        )
        lowered = content.lower()

        # Status/scope: design/contract only; reporting only; runtime safe no-op.
        self.assertIn(
            "design/contract documentation only unless otherwise stated", lowered
        )
        self.assertIn(
            "does not generate or consume future evidence lineage artifacts yet",
            lowered,
        )
        self.assertIn("Runtime remains safe no-op.", content)
        self.assertIn("Verifier output is reporting only.", content)
        self.assertIn("Evidence lineage is reporting only.", content)

        # Ownership: planner cannot supply as authority; compiler is the boundary.
        self.assertIn(
            "Planner may not supply verifier output as authority.", content
        )
        self.assertIn(
            "Planner may not supply evidence lineage as authority.", content
        )
        self.assertIn("Compiler remains the authority boundary.", content)
        self.assertIn(
            "Runtime/verifier may report observations but cannot invent authority.",
            content,
        )
        self.assertIn(
            "Operator approval remains explicit and current-run/request scoped.",
            content,
        )

        # Authority boundaries: cannot authorize/approve/grant/override/carryover.
        self.assertIn("Verifier output does not authorize execution.", content)
        self.assertIn("Evidence lineage does not authorize execution.", content)
        self.assertIn("Verifier output does not approve anything.", content)
        self.assertIn("Evidence lineage does not approve anything.", content)
        self.assertIn("Verifier output does not grant capabilities.", content)
        self.assertIn("Evidence lineage does not grant capabilities.", content)
        self.assertIn("Neither can override compiler diagnostics.", content)
        self.assertIn("Neither can override operator approval.", content)
        self.assertIn("Neither enables approval carryover.", content)
        self.assertIn("Neither enables authority subsumption.", content)
        self.assertIn("Neither creates reusable authority.", content)
        self.assertIn(
            "Future broker/sandbox execution still requires compiler-owned "
            "authority plus",
            content,
        )

        # V1 non-goals.
        for non_goal in (
            "no real execution",
            "no broker/sandbox",
            "no MCP/tool/connector calls",
            "no model inference",
            "no credentials/secrets",
            "no network behavior",
            "no new run artifact writes",
            "no verifier implementation",
            "no evidence generation implementation",
        ):
            self.assertIn(non_goal, content)

    def test_evidence_lineage_example_fixture_is_inert_future_only(self) -> None:
        self.assertTrue(EVIDENCE_LINEAGE_FIXTURE_PATH.exists())
        data = json.loads(
            EVIDENCE_LINEAGE_FIXTURE_PATH.read_text(encoding="utf-8")
        )

        self.assertEqual(data["schema_version"], "evidence-lineage.v1.example")
        for flag in (
            "display_only",
            "future_only_example",
            "not_consumed_by_v1",
            "not_control_plane_input",
            "not_authority",
            "no_runtime_authority",
            "no_execution",
            "no_approval",
        ):
            self.assertTrue(data[flag])

        self.assertEqual(data["run_scope"], "example-current-run-only")

    def test_verifier_output_example_fixture_is_inert_future_only(self) -> None:
        self.assertTrue(VERIFIER_OUTPUT_FIXTURE_PATH.exists())
        data = json.loads(
            VERIFIER_OUTPUT_FIXTURE_PATH.read_text(encoding="utf-8")
        )

        self.assertEqual(data["schema_version"], "verifier-output.v1.example")
        for flag in (
            "display_only",
            "future_only_example",
            "not_consumed_by_v1",
            "not_control_plane_input",
            "not_authority",
            "no_runtime_authority",
            "no_execution",
            "no_approval",
        ):
            self.assertTrue(data[flag])

        self.assertEqual(data["run_scope"], "example-current-run-only")
        self.assertEqual(data["fail_closed_findings"], [])

    def test_noop_broker_boundary_contract_doc_exists_and_is_design_only(
        self,
    ) -> None:
        self.assertTrue(NOOP_BROKER_BOUNDARY_CONTRACT_PATH.exists())
        content = NOOP_BROKER_BOUNDARY_CONTRACT_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        # Status/scope: design/contract only; no broker/sandbox/execution; no
        # fake/no-op broker interface implemented by this slice.
        self.assertIn(
            "design/contract documentation only unless otherwise stated", lowered
        )
        self.assertIn("V1 safe no-op has no broker implementation.", content)
        self.assertIn("V1 safe no-op has no sandbox implementation.", content)
        self.assertIn("V1 safe no-op performs no real execution.", content)
        self.assertIn(
            "No fake/no-op broker interface is implemented by this slice.", content
        )
        self.assertIn(
            "No real broker or sandbox behavior is implemented by this slice.",
            content,
        )

        # Future broker role: isolated execution boundary, not authority.
        self.assertIn(
            "The broker is a future isolated execution boundary.", content
        )
        self.assertIn("The broker is not an authority boundary.", content)
        self.assertIn("The broker must not trust planner output.", content)
        self.assertIn(
            "The broker must not consume planner-supplied compiled artifacts.",
            content,
        )
        self.assertIn(
            "The broker may eventually execute only compiler-approved capabilities.",
            content,
        )
        self.assertIn(
            "The broker must require explicit approval where required.", content
        )

        # Authority boundaries.
        self.assertIn("A broker decision does not approve anything.", content)
        self.assertIn("A broker result does not approve anything.", content)
        self.assertIn(
            "A broker decision/result does not override compiler diagnostics.",
            content,
        )
        self.assertIn(
            "A broker decision/result does not override operator approval.", content
        )
        self.assertIn(
            "A broker decision/result does not enable approval carryover.", content
        )
        self.assertIn(
            "A broker decision/result does not enable authority subsumption.",
            content,
        )
        self.assertIn(
            "A broker decision/result does not create reusable authority.", content
        )
        self.assertIn(
            "Future real execution still requires compiler-owned authority plus "
            "explicit",
            content,
        )

        # V1 non-goals.
        for non_goal in (
            "no broker",
            "no sandbox",
            "no fake/no-op broker interface",
            "no real execution",
            "no MCP/tool/connector calls",
            "no model inference",
            "no credentials/secrets",
            "no network behavior",
            "no new run artifact writes",
            "no verifier/evidence generation implementation",
        ):
            self.assertIn(non_goal, content)

    def _assert_inert_broker_fixture(self, path: Path, schema_version: str) -> dict:
        self.assertTrue(path.exists())
        data = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(data["schema_version"], schema_version)
        for flag in (
            "display_only",
            "future_only_example",
            "not_consumed_by_v1",
            "not_control_plane_input",
            "not_authority",
            "no_runtime_authority",
            "no_execution",
            "no_approval",
        ):
            self.assertTrue(data[flag])

        self.assertEqual(data["run_scope"], "example-current-run-only")
        return data

    def test_broker_request_example_fixture_is_inert_future_only(self) -> None:
        data = self._assert_inert_broker_fixture(
            BROKER_REQUEST_FIXTURE_PATH, "broker-request.v1.example"
        )
        self.assertTrue(data["denied_by_default"])
        self.assertEqual(data["allowed_inputs"], [])
        self.assertEqual(data["allowed_outputs"], [])

    def test_broker_decision_example_fixture_is_inert_future_only(self) -> None:
        data = self._assert_inert_broker_fixture(
            BROKER_DECISION_FIXTURE_PATH, "broker-decision.v1.example"
        )
        self.assertEqual(data["decision"], "denied")
        self.assertEqual(data["sandbox_attestation_status"], "not_implemented")
        self.assertEqual(data["effective_allowed_capabilities"], [])

    def test_broker_result_example_fixture_is_inert_future_only(self) -> None:
        data = self._assert_inert_broker_fixture(
            BROKER_RESULT_FIXTURE_PATH, "broker-result.v1.example"
        )
        self.assertEqual(data["status"], "not_executed")
        self.assertEqual(data["side_effects_completed"], [])
        self.assertEqual(data["fail_closed_findings"], [])

    def test_operator_cockpit_contract_doc_exists_and_records_current_order(
        self,
    ) -> None:
        self.assertTrue(OPERATOR_COCKPIT_CONTRACT_PATH.exists())
        content = OPERATOR_COCKPIT_CONTRACT_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        # Status/scope: V1 safe no-op only; display-only/read-only; no artifacts.
        self.assertIn("V1 remains safe no-op only.", content)
        self.assertIn("No real execution.", content)
        self.assertIn(
            "Display-only / read-only reporting unless otherwise stated.", content
        )
        self.assertIn(
            "No new artifacts are written by the rich summary.", content
        )

        # Applicability.
        self.assertIn(
            "Applies to blocked explicit `innovation_review` rich summaries.",
            content,
        )
        self.assertIn(
            "Governance Readiness Checklist may also appear when existing "
            "summary fields",
            content,
        )
        self.assertIn(
            "Default / non-rich / generic summaries are not required to show the "
            "full",
            content,
        )
        self.assertIn(
            "Approved runs do not show blocked-review cockpit sections", content
        )

        # Exact current section order.
        self.assertIn(
            "```text\n"
            "Review Gate:\n"
            "Governance Lifecycle Stage:\n"
            "Governance Readiness Checklist:\n"
            "Candidate Workflow:\n"
            "Fixture Lineage:\n"
            "Proposed Tool Access:\n"
            "Compiler Authorization Projection:\n"
            "Approval Binding Summary:\n"
            "Verifier / Evidence Status:\n"
            "Broker Boundary Status:\n"
            "Operator Review Packet:\n"
            "```",
            content,
        )

        # Authority boundary.
        self.assertIn("Planner remains non-authoritative.", content)
        self.assertIn(
            "Compiler remains the sole authority boundary.", content
        )
        self.assertIn("Runtime remains safe no-op.", content)
        self.assertIn("do not authorize, approve, grant", content)
        self.assertIn("capabilities, or execute.", content)
        self.assertIn(
            "Summary sections do not override compiler diagnostics.", content
        )
        self.assertIn(
            "Summary sections do not override operator approval.", content
        )
        self.assertIn(
            "Governance Readiness Checklist is display-only.", content
        )
        self.assertIn(
            "Governance Readiness Checklist is derived from existing run-status "
            "summary",
            content,
        )
        self.assertIn(
            "Governance Readiness Checklist grants no authority.", content
        )
        self.assertIn(
            "Governance Readiness Checklist creates no approvals.", content
        )
        self.assertIn(
            "Governance Readiness Checklist does not bind approvals.", content
        )
        self.assertIn(
            "Governance Readiness Checklist does not authorize execution.",
            content,
        )
        self.assertIn(
            "Governance Readiness Checklist does not implement broker, sandbox, "
            "verifier,",
            content,
        )
        self.assertIn(
            "Summary sections do not enable approval carryover.", content
        )
        self.assertIn(
            "Summary sections do not enable authority subsumption.", content
        )
        self.assertIn(
            "Summary sections do not create reusable authority.", content
        )

        # Input/read boundary: no future fixtures, no control-plane inputs.
        self.assertIn("No future fixtures are read.", content)
        self.assertIn(
            "No future fixtures become control-plane inputs.", content
        )
        self.assertIn("No credentials/secrets are read.", content)

        # V1 non-goals.
        for non_goal in (
            "no real execution",
            "no broker/sandbox",
            "no fake/no-op broker interface",
            "no verifier implementation",
            "no evidence generation implementation",
            "no canonical JSON/hashing changes",
        ):
            self.assertIn(non_goal, content)

    def test_static_validation_ordering_contract_doc_exists_and_records_order(
        self,
    ) -> None:
        self.assertTrue(STATIC_VALIDATION_ORDERING_CONTRACT_PATH.exists())
        content = STATIC_VALIDATION_ORDERING_CONTRACT_PATH.read_text(
            encoding="utf-8"
        )
        lowered = content.lower()

        # Status/scope: docs/tests only; no behavior/canonical/runtime change.
        self.assertIn("Docs/tests only.", content)
        self.assertIn("No behavior change.", content)
        self.assertIn("No canonical JSON/hashing change.", content)
        self.assertIn("No runtime/execution change.", content)

        # Exact 9-step Phase 3 order.
        self.assertIn(
            "```text\n"
            "1. secret-field\n"
            "2. capability-envelope\n"
            "3. safeguard-authority-claim\n"
            "4. authority-artifact-ownership\n"
            "5. approval-binding\n"
            "6. execution-binding\n"
            "7. runtime-reporting-boundary\n"
            "8. audit-evidence-authority\n"
            "9. approval-scope\n"
            "10. approval-identity\n"
            "11. graph/scope/approval\n"
            "```",
            content,
        )

        # Ownership boundaries: each diagnostic listed.
        for diagnostic in (
            "UNSUPPORTED_SECRET_FIELD",
            "UNSUPPORTED_CAPABILITY_ENVELOPE",
            "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
            "UNSUPPORTED_AUTHORITY_ARTIFACT",
            "UNSUPPORTED_APPROVAL_BINDING",
            "UNSUPPORTED_EXECUTION_BINDING",
            "UNSUPPORTED_RUNTIME_REPORTING_CLAIM",
            "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
            "UNSUPPORTED_APPROVAL_SCOPE_CLAIM",
            "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM",
        ):
            self.assertIn(diagnostic, content)
        self.assertIn("evidence_lineage", content)
        self.assertIn("verifier_output", content)
        self.assertIn("audit_log", content)
        self.assertIn("approval_decisions", content)
        self.assertIn("structural graph/scope/approval", content)

        # Scanner scope: planner-controlled artifacts only; not ApprovalDecisions.
        self.assertIn("WorkflowSpec.json", content)
        self.assertIn("RequestedAuth.json", content)
        self.assertIn("ApprovalRequests.json", content)
        self.assertIn(
            "must not scan `ApprovalDecisions.json` unless a validator is "
            "explicitly",
            content,
        )
        self.assertIn(
            "Operator approval decisions are not planner-authored proposals.",
            content,
        )

        # Matching rule: exact object keys, no fuzzy string matching.
        self.assertIn(
            "Unsupported claim validators reject exact object keys.", content
        )
        self.assertIn("must not fuzzy-match arbitrary string values", content)
        self.assertIn(
            "Benign strings are not rejected merely because they contain a "
            "reserved term.",
            content,
        )

        # Fail-closed guarantees.
        self.assertIn("Unsupported planner claims fail closed.", content)
        self.assertIn("Planner remains non-authoritative.", content)
        self.assertIn("Compiler remains the authority boundary.", content)
        self.assertIn("Runtime remains safe no-op.", content)
        self.assertIn("Diagnostics do not grant authority.", content)
        self.assertIn("do not approve, authorize,", content)
        self.assertIn("enable authority subsumption", content)
        self.assertIn("create reusable authority.", content)

        # Non-goals.
        for non_goal in (
            "no real execution",
            "no broker/sandbox",
            "no fake/no-op broker interface",
            "no verifier implementation",
            "no evidence generation implementation",
            "no canonical JSON/hashing changes",
        ):
            self.assertIn(non_goal, content)

    def test_v1_governance_cockpit_checkpoint_doc_exists_and_records_milestone(
        self,
    ) -> None:
        self.assertTrue(V1_GOVERNANCE_COCKPIT_CHECKPOINT_PATH.exists())
        content = V1_GOVERNANCE_COCKPIT_CHECKPOINT_PATH.read_text(
            encoding="utf-8"
        )

        # Milestone status: named checkpoint, docs/tests only, no behavior change.
        self.assertIn("V1 Safe No-Op Governance Cockpit", content)
        self.assertIn(
            "Named checkpoint, not a release tag unless separately tagged in git.",
            content,
        )
        self.assertIn("Docs/tests only.", content)
        self.assertIn("No behavior change in this slice.", content)
        self.assertIn("measured, not guessed", content)

        # Exact cockpit order block.
        self.assertIn(
            "```text\n"
            "Review Gate:\n"
            "Candidate Workflow:\n"
            "Fixture Lineage:\n"
            "Proposed Tool Access:\n"
            "Compiler Authorization Projection:\n"
            "Approval Binding Summary:\n"
            "Verifier / Evidence Status:\n"
            "Broker Boundary Status:\n"
            "Operator Review Packet:\n"
            "```",
            content,
        )

        # Exact Phase 3 validator order block.
        self.assertIn(
            "```text\n"
            "1. secret-field\n"
            "2. capability-envelope\n"
            "3. safeguard-authority-claim\n"
            "4. authority-artifact-ownership\n"
            "5. approval-binding\n"
            "6. execution-binding\n"
            "7. runtime-reporting-boundary\n"
            "8. audit-evidence-authority\n"
            "9. approval-scope\n"
            "10. approval-identity\n"
            "11. graph/scope/approval\n"
            "```",
            content,
        )

        # Trust boundary.
        self.assertIn("Planner proposes only.", content)
        self.assertIn("Planner is non-authoritative.", content)
        self.assertIn(
            "Compiler validates and owns the authority boundary.", content
        )
        self.assertIn(
            "Operator approval is explicit and current-run/request scoped.",
            content,
        )
        self.assertIn("Runtime is safe no-op.", content)
        self.assertIn(
            "do not authorize, approve, grant, execute, or", content
        )
        self.assertIn("Diagnostics fail closed.", content)

        # Included pieces.
        for included in (
            "safe no-op runtime",
            "operator cockpit contract",
            "compiler authorization projection",
            "approval binding contract/summary",
            "evidence/verifier reporting contract/status",
            "broker boundary contract/status",
            "static validation ordering contract",
            "unsupported-claim hardening validators",
        ):
            self.assertIn(included, content)

        # Non-goals.
        for non_goal in (
            "real execution",
            "broker implementation",
            "fake/no-op broker interface",
            "sandbox implementation",
            "model inference",
            "verifier implementation",
            "evidence generation implementation",
            "approval carryover",
            "reusable approvals",
            "authority subsumption",
            "real approval binding",
        ):
            self.assertIn(non_goal, content)

        # Boundary protection lists each unsupported-claim rejection.
        for rejection in (
            "unsupported secret fields rejected",
            "unsupported capability envelopes rejected",
            "unsupported safeguard authority claims rejected",
            "unsupported authority artifacts rejected",
            "unsupported approval-binding claims rejected",
            "unsupported execution-binding claims rejected",
            "unsupported runtime-reporting/broker/sandbox claims rejected",
            "unsupported audit/evidence authority claims rejected",
            "unsupported approval scope/reuse/cross-run claims rejected",
            "unsupported approval identity/proof/receipt/signature/subject claims rejected",
        ):
            self.assertIn(rejection, content)

        # Next safe directions.
        self.assertIn("milestone tag or release note", content)
        self.assertIn("final V1 no-op threat-model review", content)
        self.assertIn(
            "current-run approval scope invariant tightening", content
        )
        self.assertIn(
            "do not add broker execution or fake broker interface yet", content
        )

    def test_post_tag_approval_hardening_line_doc_exists_and_records_checkpoint(
        self,
    ) -> None:
        self.assertTrue(POST_TAG_APPROVAL_HARDENING_LINE_PATH.exists())
        content = POST_TAG_APPROVAL_HARDENING_LINE_PATH.read_text(
            encoding="utf-8"
        )

        # Status/scope: docs/tests only; no behavior/canonical/runtime change.
        self.assertIn("Docs/tests only.", content)
        self.assertIn("No behavior change.", content)
        self.assertIn("No canonical JSON/hashing change.", content)
        self.assertIn("No runtime/execution change.", content)
        self.assertIn("No new validator added in this slice.", content)

        # Milestone tag stays pinned to 0131572; HEAD intentionally ahead.
        self.assertIn("v0.1.0-safe-noop-governance-cockpit", content)
        self.assertIn("V1 Safe\n  No-Op Governance Cockpit", content)
        self.assertIn("0131572", content)
        self.assertIn("It must not be moved.", content)
        self.assertIn("intentionally ahead", content)

        # The two post-tag commits.
        self.assertIn(
            "```text\n"
            "4f98ced Reject unsupported approval scope claims\n"
            "927bb7d Reject unsupported approval identity claims\n"
            "```",
            content,
        )

        # Hardened approval invariants.
        self.assertIn("Approval-scope invariant.", content)
        self.assertIn(
            "reusable, persistent, global, inherited, valid across runs, or "
            "valid across\n  requests",
            content,
        )
        self.assertIn("Approval-identity invariant.", content)
        self.assertIn(
            "identity, proof, receipt, signature, subject, run, or request "
            "identifiers",
            content,
        )
        self.assertIn(
            "fail-closed static validation hardening changes only", content
        )

        # Explicit non-implementations.
        for non_goal in (
            "reusable approval",
            "approval carryover",
            "authority subsumption",
            "real approval binding",
            "real execution",
            "broker behavior",
            "fake/no-op broker interface",
            "sandbox behavior",
            "verifier behavior",
            "evidence generation",
            "tool/MCP/model/network/credential behavior",
        ):
            self.assertIn(non_goal, content)

        # Trust boundary unchanged.
        self.assertIn("The planner remains non-authoritative.", content)
        self.assertIn(
            "The compiler remains the sole authority boundary.", content
        )
        self.assertIn(
            "Operator approval remains explicit and current-run/request scoped.",
            content,
        )
        self.assertIn("The runtime remains safe no-op.", content)

    def test_phase3_validator_ownership_map_doc_exists_and_records_contract(
        self,
    ) -> None:
        self.assertTrue(PHASE3_VALIDATOR_OWNERSHIP_MAP_PATH.exists())
        content = PHASE3_VALIDATOR_OWNERSHIP_MAP_PATH.read_text(
            encoding="utf-8"
        )

        # Status/scope: docs/tests only; no behavior/validator/canonical change.
        self.assertIn("Docs/tests only.", content)
        self.assertIn("No behavior change.", content)
        self.assertIn("No new validator.", content)
        self.assertIn("No canonical JSON/hashing change.", content)
        self.assertIn("No runtime/execution change.", content)

        # Core framing: fail-closed guards that create no authority.
        self.assertIn("fail-closed governance guards", content)
        self.assertIn(
            "do not create** authority, approvals, evidence, execution",
            content,
        )

        # Product framing preserved.
        self.assertIn("non-authoritative", content)
        self.assertIn("sole authority boundary", content)
        self.assertIn(
            "Operator approval is **explicit and current-run/request scoped**.",
            content,
        )
        self.assertIn("cannot create authority", content)
        self.assertIn(
            "No real execution, broker, sandbox, verifier, evidence generation, "
            "approval",
            content,
        )

        # Exact 11-step Phase 3 order block.
        self.assertIn(
            "```text\n"
            "1. secret-field\n"
            "2. capability-envelope\n"
            "3. safeguard-authority-claim\n"
            "4. authority-artifact-ownership\n"
            "5. approval-binding\n"
            "6. execution-binding\n"
            "7. runtime-reporting-boundary\n"
            "8. audit-evidence-authority\n"
            "9. approval-scope\n"
            "10. approval-identity\n"
            "11. graph/scope/approval\n"
            "```",
            content,
        )

        # Planner-input scanner scope block (scans only the three planner
        # artifacts, never ApprovalDecisions.json).
        self.assertIn(
            "```text\n"
            "WorkflowSpec.json\n"
            "RequestedAuth.json\n"
            "ApprovalRequests.json\n"
            "```",
            content,
        )
        self.assertIn("must **not** scan `ApprovalDecisions.json`", content)

        # Every validator's diagnostic code and component name is present.
        for diagnostic in (
            "UNSUPPORTED_SECRET_FIELD",
            "UNSUPPORTED_CAPABILITY_ENVELOPE",
            "UNSUPPORTED_SAFEGUARD_AUTHORITY_CLAIM",
            "UNSUPPORTED_AUTHORITY_ARTIFACT",
            "UNSUPPORTED_APPROVAL_BINDING",
            "UNSUPPORTED_EXECUTION_BINDING",
            "UNSUPPORTED_RUNTIME_REPORTING_CLAIM",
            "UNSUPPORTED_AUDIT_EVIDENCE_AUTHORITY_CLAIM",
            "UNSUPPORTED_APPROVAL_SCOPE_CLAIM",
            "UNSUPPORTED_APPROVAL_IDENTITY_CLAIM",
        ):
            self.assertIn(diagnostic, content)
        for component in (
            "secret_field_validator",
            "capability_envelope_validator",
            "safeguard_authority_claim_validator",
            "authority_artifact_ownership_validator",
            "approval_binding_validator",
            "execution_binding_validator",
            "runtime_reporting_boundary_validator",
            "audit_evidence_authority_validator",
            "approval_scope_validator",
            "approval_identity_validator",
            "graph_validator",
            "scope_validator",
            "approval_validator",
        ):
            self.assertIn(component, content)

        # Approval-scope validator precision.
        for scope_term in (
            "reusable",
            "persistent",
            "global",
            "inherited",
            "cross-run",
            "cross-request",
        ):
            self.assertIn(scope_term, content)
        self.assertIn(
            "`approval_carryover`, `reusable_approval`,\n  `standing_approval`, "
            "and `standing_approvals` remain owned by\n  "
            "`UNSUPPORTED_APPROVAL_BINDING`",
            content,
        )

        # Approval-identity validator precision.
        for identity_term in (
            "approval identity",
            "approval proof",
            "approval receipt",
            "approval signature",
            "approval subject",
            "approval run identifiers",
            "approval request identifiers",
        ):
            self.assertIn(identity_term, content)
        self.assertIn(
            "`approval_token` and `approval_tokens` remain owned by\n  "
            "`UNSUPPORTED_APPROVAL_BINDING`",
            content,
        )
        # Legitimate schema fields must remain valid.
        for legit in (
            "`request_id`",
            "`approval_subject_hash`",
            "`workflow_revision_id`",
        ):
            self.assertIn(legit, content)

        # Exact-key matching rule.
        self.assertIn("reject **exact object keys**", content)
        self.assertIn("do not fuzzy-match arbitrary string values", content)

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
            "COMPILER_AUTHORIZATION_SUMMARY_PROJECTION.md",
            "STATIC_VALIDATION_HARDENING_MAP.md",
            "SAFEGUARD_ADVISORY_DESIGN.md",
            "SKILL_PROMPT_REGISTRY_DESIGN.md",
            "SANDBOX_BROKER_INTERFACE_DESIGN.md",
            "APPROVAL_BINDING_CONTRACT.md",
            "EVIDENCE_LINEAGE_VERIFIER_OUTPUT_CONTRACT.md",
            "NOOP_BROKER_BOUNDARY_CONTRACT.md",
            "OPERATOR_COCKPIT_CONTRACT.md",
            "STATIC_VALIDATION_ORDERING_CONTRACT.md",
            "V1_SAFE_NOOP_GOVERNANCE_COCKPIT_CHECKPOINT.md",
            "POST_TAG_APPROVAL_HARDENING_LINE.md",
            "PHASE3_VALIDATOR_OWNERSHIP_MAP.md",
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
        self.assertIn("CompilerAuthorizationSummaryProjection.example.json", content)
        self.assertIn("SafeguardAdvisory.example.json", content)
        self.assertIn("ApprovalBinding.example.json", content)
        self.assertIn("EvidenceLineage.example.json", content)
        self.assertIn("VerifierOutput.example.json", content)
        self.assertIn("BrokerRequest.example.json", content)
        self.assertIn("BrokerDecision.example.json", content)
        self.assertIn("BrokerResult.example.json", content)
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

    def test_sandbox_backend_strategy_doc_exists_and_preserves_boundaries(
        self,
    ) -> None:
        self.assertTrue(SANDBOX_BACKEND_STRATEGY_PATH.exists())
        content = SANDBOX_BACKEND_STRATEGY_PATH.read_text(encoding="utf-8")
        lowered = content.lower()
        normalized = " ".join(content.split())
        lowered_normalized = normalized.lower()

        self.assertIn("design only", lowered)
        self.assertIn(
            "will not implement sandbox isolation from scratch",
            lowered_normalized,
        )
        self.assertIn(
            "will not implement a full agent runtime from scratch",
            lowered_normalized,
        )
        self.assertIn(
            "will not implement Kubernetes agent orchestration from scratch",
            normalized,
        )
        self.assertIn("not trying to replace these systems", lowered_normalized)
        self.assertIn("governance/control-plane boundary", normalized)
        self.assertIn("pluggable sandbox backend", lowered_normalized)
        self.assertIn("Hermes Agent", content)
        self.assertIn("kagent/kagents", content)
        self.assertIn("Kubernetes", content)
        self.assertIn(
            "NemoClaw/OpenShell is a candidate backend", normalized
        )
        self.assertIn("candidate backend, not a replacement", lowered_normalized)
        self.assertIn("workflow-harness compiler", normalized)
        self.assertIn("Hermes Agent is not authoritative", normalized)
        self.assertIn("kagent/kagents are not authoritative", normalized)
        self.assertIn("Kubernetes is not authoritative", normalized)
        self.assertIn("NemoClaw/OpenShell is not authoritative", normalized)
        self.assertIn("compiler remains the authority boundary", lowered_normalized)
        self.assertIn(
            "operator approval remains explicit and current-run/request scoped",
            lowered_normalized,
        )
        self.assertIn(
            "sandbox having policy does not replace compiler authorization",
            lowered_normalized,
        )
        self.assertIn(
            "sandbox having policy does not replace artifact identity",
            lowered_normalized,
        )
        self.assertIn(
            "sandbox having policy does not replace current-run/request approval scope",
            lowered_normalized,
        )
        self.assertIn(
            "sandbox having policy does not replace audit/verifier/status semantics",
            lowered_normalized,
        )
        self.assertIn("sandbox/backend cannot create authority", lowered_normalized)
        self.assertIn(
            "runtime/broker/verifier cannot create authority",
            lowered_normalized,
        )
        self.assertIn("does not introduce a broker api", lowered_normalized)
        self.assertIn("does not introduce a sandbox api", lowered_normalized)
        self.assertIn("does not introduce an execution api", lowered_normalized)
        self.assertIn(
            "does not introduce kubernetes integration", lowered_normalized
        )
        self.assertIn(
            "does not introduce hermes agent integration", lowered_normalized
        )
        self.assertIn(
            "does not introduce kagent/kagents integration", lowered_normalized
        )
        self.assertIn(
            "does not introduce nemoclaw/openshell integration",
            lowered_normalized,
        )
        self.assertIn("does not implement real execution", lowered_normalized)
        self.assertIn(
            "does not implement credentials behavior", lowered_normalized
        )
        self.assertIn("does not implement network behavior", lowered_normalized)
        self.assertIn("does not implement tool/mcp behavior", lowered_normalized)

    def test_workflow_pattern_selection_doc_exists_and_preserves_boundaries(
        self,
    ) -> None:
        self.assertTrue(WORKFLOW_PATTERN_SELECTION_PATH.exists())
        content = WORKFLOW_PATTERN_SELECTION_PATH.read_text(encoding="utf-8")
        lowered = content.lower()
        normalized = " ".join(content.split())
        lowered_normalized = normalized.lower()

        self.assertIn("design only", lowered)
        self.assertIn("not implemented", lowered)
        self.assertIn(
            "workflow pattern selection is non-authoritative",
            lowered_normalized,
        )
        self.assertIn("Planner suggests.", normalized)
        self.assertIn("Compiler authorizes.", normalized)
        self.assertIn("Operator approves.", normalized)
        self.assertIn(
            "Runtime executes only what was compiler-authorized and operator-approved.",
            normalized,
        )
        self.assertIn("Verifier reports.", normalized)
        self.assertIn("Audit preserves lineage.", normalized)
        self.assertIn("Hermes Agent is not authoritative", normalized)
        self.assertIn(
            "planner-selected pattern does not authorize tools",
            lowered_normalized,
        )
        self.assertIn(
            "planner-selected pattern does not authorize execution",
            lowered_normalized,
        )
        self.assertIn(
            "planner-selected pattern does not create approvals",
            lowered_normalized,
        )
        self.assertIn(
            "planner-selected pattern does not bind approvals",
            lowered_normalized,
        )
        self.assertIn("compiler remains the authority boundary", lowered_normalized)
        self.assertIn(
            "operator approval remains explicit and current-run/request scoped",
            lowered_normalized,
        )
        self.assertIn(
            "replanning must not inherit approval automatically",
            lowered_normalized,
        )
        self.assertIn(
            "dynamic patterns require recompile/reapproval when requested scope changes",
            lowered_normalized,
        )
        self.assertIn("Plan-Solve", content)
        self.assertIn("ReAct, bounded only", content)
        self.assertIn("REWOO", content)
        self.assertIn("LLMCompiler-style parallel DAG", content)
        self.assertIn("Reflection", content)
        self.assertIn("Storm-like research synthesis", content)
        self.assertIn("Handoff / multi-agent", content)
        self.assertIn("Orchestration Form vs Pattern Family", content)
        self.assertIn("Planner/Hermes may propose workflows", normalized)
        self.assertIn(
            "workflow script may also hold or propose orchestration",
            lowered_normalized,
        )
        self.assertIn("saved workflow template", lowered_normalized)
        self.assertIn("none of these are authoritative", lowered_normalized)
        self.assertIn(
            "only `workflow-harness` compiler validation",
            lowered_normalized,
        )
        self.assertIn(
            "current planner is a deterministic skeleton",
            lowered_normalized,
        )
        self.assertIn(
            "current planner does not call an llm",
            lowered_normalized,
        )
        self.assertIn(
            "current planner does not execute anything",
            lowered_normalized,
        )
        self.assertIn(
            "current planner does not write compiled artifacts",
            lowered_normalized,
        )
        self.assertIn("current runtime remains safe no-op", lowered_normalized)
        self.assertIn("view raw proposed orchestration", lowered_normalized)
        self.assertIn("token budget", lowered_normalized)
        self.assertIn("concurrency limits", lowered_normalized)
        self.assertIn("loop stop condition", lowered_normalized)
        self.assertIn("model/intelligence routing", lowered_normalized)
        self.assertIn(
            "reusable workflow definitions may be allowed",
            lowered_normalized,
        )
        self.assertIn("reusable approvals are not allowed", lowered_normalized)
        self.assertIn(
            "do not ask again approval semantics are not allowed",
            lowered_normalized,
        )
        self.assertIn(
            "workflow script execution does not authorize tools",
            lowered_normalized,
        )
        self.assertIn(
            "subagent fan-out does not authorize new capabilities",
            lowered_normalized,
        )
        self.assertIn("does not change WorkflowSpec", normalized)
        self.assertIn("does not change schemas", lowered_normalized)
        self.assertIn("does not change canonical JSON", normalized)
        self.assertIn("does not implement planner behavior", lowered_normalized)
        self.assertIn(
            "does not implement hermes agent integration",
            lowered_normalized,
        )
        self.assertIn("does not implement real execution", lowered_normalized)

    def test_repo_terminology_map_doc_exists_and_preserves_boundaries(
        self,
    ) -> None:
        self.assertTrue(REPO_TERMINOLOGY_MAP_PATH.exists())
        content = REPO_TERMINOLOGY_MAP_PATH.read_text(encoding="utf-8")
        lowered = content.lower()
        normalized = " ".join(content.split())
        lowered_normalized = normalized.lower()
        normalized_no_ticks = normalized.replace("`", "")
        lowered_normalized_no_ticks = lowered_normalized.replace("`", "")

        self.assertIn("Repo Terminology Map", content)
        self.assertIn("documentation only", lowered)
        self.assertIn(
            "schemas/ is the control-plane artifact contract layer",
            lowered_normalized_no_ticks,
        )
        self.assertIn("schemas/ is not execution", lowered_normalized_no_ticks)
        self.assertIn(
            "planner/ currently contains a deterministic planner skeleton",
            lowered_normalized_no_ticks,
        )
        self.assertIn(
            "planner output is non-authoritative until compiler validation",
            lowered_normalized,
        )
        self.assertIn(
            "compiler/ is the authority boundary",
            lowered_normalized_no_ticks,
        )
        self.assertIn(
            "orchestrator/ currently means the safe-noop local harness coordinator",
            lowered_normalized_no_ticks,
        )
        self.assertIn(
            "orchestrator/ is not claude-style workflow orchestration",
            lowered_normalized_no_ticks,
        )
        self.assertIn(
            "orchestrator/ is not hermes agent integration",
            lowered_normalized_no_ticks,
        )
        self.assertIn(
            "orchestrator/ is not kubernetes orchestration",
            lowered_normalized_no_ticks,
        )
        self.assertIn(
            "broker/ currently contains future sandbox/broker data-shape helpers only",
            lowered_normalized_no_ticks,
        )
        self.assertIn("broker helpers are build-only", lowered_normalized)
        self.assertIn("broker helpers execute nothing", lowered_normalized)
        self.assertIn("broker helpers authorize nothing", lowered_normalized)
        self.assertIn(
            "broker helpers are not a broker implementation",
            lowered_normalized,
        )
        self.assertIn(
            "runtime/ currently owns safe-noop runtime surfaces",
            lowered_normalized_no_ticks,
        )
        self.assertIn(
            "run-status summary never writes anything",
            lowered_normalized,
        )
        self.assertIn(
            "run-status summary reads only known local run artifacts",
            lowered_normalized,
        )
        self.assertIn(
            "tui/ renders display/operator status",
            lowered_normalized_no_ticks,
        )
        self.assertIn(
            "design docs must not be interpreted as implemented behavior",
            lowered_normalized,
        )
        self.assertIn("view raw proposed orchestration", lowered_normalized)
        self.assertIn("token budget", lowered_normalized)
        self.assertIn("concurrency limits", lowered_normalized)
        self.assertIn("loop stop condition", lowered_normalized)
        self.assertIn(
            "trust nothing / verify everything / assume breach",
            lowered_normalized,
        )
        self.assertIn("current-run/request approval scope", normalized_no_ticks)
        self.assertIn("canonical artifact identity", lowered_normalized)
        self.assertIn(
            "compiler-owned capability requests",
            lowered_normalized,
        )
        self.assertIn(
            "this document does not implement runtime behavior",
            lowered_normalized,
        )
        self.assertIn(
            "this document does not implement compiler behavior",
            lowered_normalized,
        )
        self.assertIn(
            "this document does not implement schema behavior",
            lowered_normalized,
        )
        self.assertIn(
            "this document does not implement broker behavior",
            lowered_normalized,
        )
        self.assertIn(
            "this document does not implement sandbox behavior",
            lowered_normalized,
        )
        self.assertIn(
            "this document does not implement kubernetes integration",
            lowered_normalized,
        )
        self.assertIn(
            "this document does not implement hermes agent integration",
            lowered_normalized,
        )
        self.assertIn(
            "this document does not change canonical json",
            lowered_normalized,
        )
        self.assertIn("this document does not change hashing", lowered_normalized)


if __name__ == "__main__":
    unittest.main()
