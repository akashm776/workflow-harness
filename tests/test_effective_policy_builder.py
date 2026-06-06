from __future__ import annotations

import json
from pathlib import Path
import unittest

from compiler.canonical_json import canonical_json_text
from compiler.effective_policy import build_effective_policy


ROOT = Path(__file__).resolve().parent.parent
VALID_FIXTURES = (
    "simple-workflow",
    "approval-required-workflow",
)


class EffectivePolicyBuilderTests(unittest.TestCase):
    def test_valid_fixtures_build_expected_effective_policy_dicts(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            expected = json.loads(
                (fixture_input / "EffectivePolicy.json").read_text(encoding="utf-8")
            )

            effective_policy = build_effective_policy(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "NodeTypeRegistry.json",
            )

            with self.subTest(fixture=fixture_name):
                self.assertEqual(effective_policy, expected)

    def test_requested_authority_is_preserved_without_policy_evaluation(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"
        requested_auth = json.loads(
            (fixture_input / "RequestedAuth.json").read_text(encoding="utf-8")
        )

        effective_policy = build_effective_policy(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "NodeTypeRegistry.json",
        )

        self.assertEqual(
            effective_policy["allowed_tools"], requested_auth["requested_tools"]
        )
        self.assertEqual(
            effective_policy["allowed_connectors"],
            requested_auth["requested_connectors"],
        )
        self.assertEqual(
            effective_policy["allowed_permissions"],
            requested_auth["requested_permissions"],
        )
        self.assertTrue(effective_policy["review_required"])
        self.assertEqual(effective_policy["artifact_lifecycle_state"], "compiled")

    def test_review_required_is_true_when_any_requested_authority_exists(self) -> None:
        for fixture_name in VALID_FIXTURES:
            fixture_input = ROOT / "fixtures" / "valid" / fixture_name / "input"
            requested_auth = json.loads(
                (fixture_input / "RequestedAuth.json").read_text(encoding="utf-8")
            )

            effective_policy = build_effective_policy(
                fixture_input / "WorkflowSpec.json",
                fixture_input / "RequestedAuth.json",
                fixture_input / "NodeTypeRegistry.json",
            )

            with self.subTest(fixture=fixture_name):
                self.assertTrue(
                    bool(
                        requested_auth.get("requested_tools")
                        or requested_auth.get("requested_connectors")
                        or requested_auth.get("requested_permissions")
                    )
                )
                self.assertTrue(effective_policy["review_required"])

    def test_matching_approved_decision_can_make_review_not_required(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "simple-workflow" / "input"

        effective_policy = build_effective_policy(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "NodeTypeRegistry.json",
            fixture_input / "ApprovalDecisions.json",
            fixture_input / "ApprovalRequests.json",
        )

        self.assertFalse(effective_policy["review_required"])

    def test_effective_policy_canonical_json_is_deterministic(self) -> None:
        fixture_input = ROOT / "fixtures" / "valid" / "approval-required-workflow" / "input"

        left = build_effective_policy(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "NodeTypeRegistry.json",
        )
        right = build_effective_policy(
            fixture_input / "WorkflowSpec.json",
            fixture_input / "RequestedAuth.json",
            fixture_input / "NodeTypeRegistry.json",
        )

        self.assertEqual(canonical_json_text(left), canonical_json_text(right))


if __name__ == "__main__":
    unittest.main()
