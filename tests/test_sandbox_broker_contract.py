from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from broker.sandbox_broker_contract import (
    build_broker_decision,
    build_broker_request,
    build_broker_result,
)


def _request_kwargs() -> dict:
    return {
        "request_id": "req-001",
        "workflow_revision_id": "workflow-rev-001",
        "node_id": "execute-1",
        "node_revision_id": "node-rev-1",
        "compiled_artifact_refs": ["EffectivePolicy.json", "ExecutionBindings.json"],
        "execution_binding_ref": "ExecutionBindings.json#execute-1",
        "side_effect_class": "external write",
        "tool_or_connector_version": "1.0.0",
        "scope": {"project_key": "ABC"},
        "audit_correlation_id": "corr-001",
    }


class BrokerRequestTests(unittest.TestCase):
    def test_exact_request_shape_with_tool(self) -> None:
        request = build_broker_request(tool_name="ticket-creator", **_request_kwargs())
        self.assertEqual(
            request,
            {
                "schema_version": "m1",
                "request_id": "req-001",
                "workflow_revision_id": "workflow-rev-001",
                "node_id": "execute-1",
                "node_revision_id": "node-rev-1",
                "compiled_artifact_refs": [
                    "EffectivePolicy.json",
                    "ExecutionBindings.json",
                ],
                "execution_binding_ref": "ExecutionBindings.json#execute-1",
                "side_effect_class": "external write",
                "tool_name": "ticket-creator",
                "tool_or_connector_version": "1.0.0",
                "scope": {"project_key": "ABC"},
                "audit_correlation_id": "corr-001",
            },
        )

    def test_request_shape_with_connector(self) -> None:
        request = build_broker_request(connector_name="jira", **_request_kwargs())
        self.assertEqual(request["connector_name"], "jira")
        self.assertNotIn("tool_name", request)

    def test_request_requires_exactly_one_of_tool_or_connector_neither(self) -> None:
        with self.assertRaises(ValueError) as caught:
            build_broker_request(**_request_kwargs())
        self.assertIn("exactly one of tool_name or connector_name", str(caught.exception))

    def test_request_requires_exactly_one_of_tool_or_connector_both(self) -> None:
        with self.assertRaises(ValueError) as caught:
            build_broker_request(
                tool_name="ticket-creator", connector_name="jira", **_request_kwargs()
            )
        self.assertIn("exactly one of tool_name or connector_name", str(caught.exception))

    def test_request_list_inputs_are_defensively_copied(self) -> None:
        refs = ["EffectivePolicy.json"]
        kwargs = _request_kwargs()
        kwargs["compiled_artifact_refs"] = refs
        request = build_broker_request(tool_name="t", **kwargs)
        refs.append("mutated")
        self.assertEqual(request["compiled_artifact_refs"], ["EffectivePolicy.json"])


class BrokerDecisionTests(unittest.TestCase):
    def test_exact_permitted_decision_shape_omits_reason_code(self) -> None:
        decision = build_broker_decision(
            request_id="req-001",
            decision="permitted",
            checked_authority_ref="EffectivePolicy.json#execute-1",
            sandbox_attestation_ref="attestation-001",
            side_effect_class="external write",
            audit_correlation_id="corr-001",
        )
        self.assertEqual(
            decision,
            {
                "schema_version": "m1",
                "request_id": "req-001",
                "decision": "permitted",
                "checked_authority_ref": "EffectivePolicy.json#execute-1",
                "sandbox_attestation_ref": "attestation-001",
                "side_effect_class": "external write",
                "audit_correlation_id": "corr-001",
            },
        )
        self.assertNotIn("reason_code", decision)

    def test_denied_decision_includes_reason_code(self) -> None:
        decision = build_broker_decision(
            request_id="req-001",
            decision="denied",
            checked_authority_ref="EffectivePolicy.json#execute-1",
            sandbox_attestation_ref="attestation-001",
            side_effect_class="external write",
            audit_correlation_id="corr-001",
            reason_code="BROADER_THAN_APPROVED",
        )
        self.assertEqual(decision["decision"], "denied")
        self.assertEqual(decision["reason_code"], "BROADER_THAN_APPROVED")

    def test_denied_decision_requires_reason_code(self) -> None:
        with self.assertRaises(ValueError) as caught:
            build_broker_decision(
                request_id="req-001",
                decision="denied",
                checked_authority_ref="ref",
                sandbox_attestation_ref="attestation-001",
                side_effect_class="external write",
                audit_correlation_id="corr-001",
            )
        self.assertIn("'denied' requires reason_code", str(caught.exception))

    def test_unknown_decision_value_fails(self) -> None:
        with self.assertRaises(ValueError) as caught:
            build_broker_decision(
                request_id="req-001",
                decision="maybe",
                checked_authority_ref="ref",
                sandbox_attestation_ref="attestation-001",
                side_effect_class="external write",
                audit_correlation_id="corr-001",
            )
        self.assertIn("must be one of", str(caught.exception))


class BrokerResultTests(unittest.TestCase):
    def test_exact_success_result_shape_omits_reason_code(self) -> None:
        result = build_broker_result(
            request_id="req-001",
            status="success",
            output_refs=["ExecutionResult.json"],
            observed_side_effects=[{"class": "external write", "target": "ABC-1"}],
            audit_correlation_id="corr-001",
        )
        self.assertEqual(
            result,
            {
                "schema_version": "m1",
                "request_id": "req-001",
                "status": "success",
                "output_refs": ["ExecutionResult.json"],
                "observed_side_effects": [
                    {"class": "external write", "target": "ABC-1"}
                ],
                "audit_correlation_id": "corr-001",
            },
        )
        self.assertNotIn("reason_code", result)

    def test_failure_result_requires_reason_code(self) -> None:
        with self.assertRaises(ValueError) as caught:
            build_broker_result(
                request_id="req-001",
                status="failure",
                output_refs=[],
                observed_side_effects=[],
                audit_correlation_id="corr-001",
            )
        self.assertIn("'failure' requires reason_code", str(caught.exception))

    def test_denied_result_requires_reason_code(self) -> None:
        with self.assertRaises(ValueError) as caught:
            build_broker_result(
                request_id="req-001",
                status="denied",
                output_refs=[],
                observed_side_effects=[],
                audit_correlation_id="corr-001",
            )
        self.assertIn("'denied' requires reason_code", str(caught.exception))

    def test_failure_result_includes_reason_code(self) -> None:
        result = build_broker_result(
            request_id="req-001",
            status="failure",
            output_refs=[],
            observed_side_effects=[],
            audit_correlation_id="corr-001",
            reason_code="SANDBOX_UNVERIFIABLE",
        )
        self.assertEqual(result["status"], "failure")
        self.assertEqual(result["reason_code"], "SANDBOX_UNVERIFIABLE")

    def test_unknown_status_value_fails(self) -> None:
        with self.assertRaises(ValueError) as caught:
            build_broker_result(
                request_id="req-001",
                status="exploded",
                output_refs=[],
                observed_side_effects=[],
                audit_correlation_id="corr-001",
            )
        self.assertIn("must be one of", str(caught.exception))

    def test_result_list_inputs_are_defensively_copied(self) -> None:
        outputs: list = []
        effects: list = []
        result = build_broker_result(
            request_id="req-001",
            status="success",
            output_refs=outputs,
            observed_side_effects=effects,
            audit_correlation_id="corr-001",
        )
        outputs.append("mutated")
        effects.append("mutated")
        self.assertEqual(result["output_refs"], [])
        self.assertEqual(result["observed_side_effects"], [])


class BrokerContractPurityAndPlacementTests(unittest.TestCase):
    def test_builders_do_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            build_broker_request(tool_name="t", **_request_kwargs())
            build_broker_decision(
                request_id="req-001",
                decision="permitted",
                checked_authority_ref="ref",
                sandbox_attestation_ref="attestation-001",
                side_effect_class="external write",
                audit_correlation_id="corr-001",
            )
            build_broker_result(
                request_id="req-001",
                status="success",
                output_refs=[],
                observed_side_effects=[],
                audit_correlation_id="corr-001",
            )
            self.assertEqual(list(tmp_path.iterdir()), [])

    def test_module_is_importable_from_broker_package(self) -> None:
        import broker.sandbox_broker_contract as module

        for name in (
            "build_broker_request",
            "build_broker_decision",
            "build_broker_result",
        ):
            self.assertTrue(hasattr(module, name))

    def test_runtime_and_compiler_do_not_reference_broker_contract(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for package in ("runtime", "compiler", "orchestrator"):
            for source in (root / package).rglob("*.py"):
                with self.subTest(source=str(source)):
                    self.assertNotIn(
                        "sandbox_broker_contract",
                        source.read_text(encoding="utf-8"),
                    )


if __name__ == "__main__":
    unittest.main()
