from __future__ import annotations

import json
from pathlib import Path
import unittest

from compiler.canonical_json import canonical_json_text
from compiler.effective_policy import build_effective_policy
from compiler.execution_bindings import build_execution_bindings


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)


class ExecutionBindingsBuilderTests(unittest.TestCase):
    def test_valid_fixtures_build_expected_execution_bindings_dicts(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            expected = json.loads(
                (fixture_input / "ExecutionBindings.json").read_text(encoding="utf-8")
            )
            effective_policy = build_effective_policy(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "NodeTypeRegistry.json",
            )

            execution_bindings = build_execution_bindings(effective_policy)

            with self.subTest(fixture=fixture_name):
                self.assertEqual(execution_bindings, expected)

    def test_allowed_authority_is_preserved_in_bindings(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        effective_policy = build_effective_policy(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "NodeTypeRegistry.json",
        )

        execution_bindings = build_execution_bindings(effective_policy)

        self.assertEqual(
            [entry["tool_name"] for entry in execution_bindings["bound_tools"]],
            [entry["tool_name"] for entry in effective_policy["allowed_tools"]],
        )
        self.assertEqual(
            [entry["access_mode"] for entry in execution_bindings["bound_tools"]],
            [entry["access_mode"] for entry in effective_policy["allowed_tools"]],
        )
        self.assertEqual(
            [entry["connector_name"] for entry in execution_bindings["bound_connectors"]],
            [entry["connector_name"] for entry in effective_policy["allowed_connectors"]],
        )
        self.assertEqual(
            [entry["scope"] for entry in execution_bindings["bound_connectors"]],
            [entry["scope"] for entry in effective_policy["allowed_connectors"]],
        )
        self.assertEqual(
            [
                entry["binding_ref"]
                for entry in execution_bindings["bound_connectors"]
            ],
            [
                f"connector-binding:{entry['connector_name']}:{entry['scope']}"
                for entry in effective_policy["allowed_connectors"]
            ],
        )
        self.assertEqual(
            [entry["permission"] for entry in execution_bindings["bound_permissions"]],
            [entry["permission"] for entry in effective_policy["allowed_permissions"]],
        )
        self.assertEqual(
            [entry["target"] for entry in execution_bindings["bound_permissions"]],
            [entry["target"] for entry in effective_policy["allowed_permissions"]],
        )
        self.assertEqual(execution_bindings["env_bindings"], [])

    def test_execution_bindings_canonical_json_is_deterministic(self) -> None:
        fixture_input = (
            ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"
        )
        effective_policy = build_effective_policy(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "NodeTypeRegistry.json",
        )

        left = build_execution_bindings(effective_policy)
        right = build_execution_bindings(effective_policy)

        self.assertEqual(canonical_json_text(left), canonical_json_text(right))


if __name__ == "__main__":
    unittest.main()
