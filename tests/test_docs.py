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
SANDBOX_BROKER_INTERFACE_PATH = ROOT / "docs" / "SANDBOX_BROKER_INTERFACE_DESIGN.md"
DOCS_INDEX_PATH = ROOT / "docs" / "README.md"


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
        self.assertIn("python -m cli.run_status_cli", content)
        self.assertNotIn("C:\\Users\\", content)
        self.assertNotIn("```powershell", content)

    def test_milestone_status_doc_exists_and_mentions_current_snapshot(self) -> None:
        self.assertTrue(MILESTONE_STATUS_PATH.exists())
        content = MILESTONE_STATUS_PATH.read_text(encoding="utf-8")

        self.assertIn("V1 Safe No-Op Harness", content)
        self.assertIn("387 tests", content)
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

        # Relationships to the other design checkpoints.
        self.assertIn("REAL_EXECUTION_THREAT_MODEL.md", content)
        self.assertIn("AUTHORITY_SUBSUMPTION_DESIGN.md", content)

        # Non-goals.
        self.assertIn("Non-Goals", content)

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
