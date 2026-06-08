from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "future" / "safeguard-advisory"
POLICY_PATH = FIXTURE_DIR / "WorkflowHarnessSafeguardPolicy.md"
ADVISORY_PATH = FIXTURE_DIR / "SafeguardAdvisory.example.json"
FUTURE_FIXTURES_README = ROOT / "fixtures" / "future" / "README.md"
FORBIDDEN_FRAGMENTS = (
    "token",
    "secret",
    "password",
    "api_key",
    "private_key",
    "credential",
)


def _walk_strings(value: object) -> list[str]:
    if isinstance(value, dict):
        items: list[str] = []
        for key, nested in value.items():
            items.append(str(key))
            items.extend(_walk_strings(nested))
        return items
    if isinstance(value, list):
        items: list[str] = []
        for nested in value:
            items.extend(_walk_strings(nested))
        return items
    if isinstance(value, str):
        return [value]
    return []


class SafeguardAdvisoryFixtureTests(unittest.TestCase):
    def test_policy_fixture_exists_and_lists_workflow_harness_categories(self) -> None:
        self.assertTrue(POLICY_PATH.exists())
        content = POLICY_PATH.read_text(encoding="utf-8")

        for category in (
            "approval_bypass_attempt",
            "authority_smuggling",
            "credential_or_secret_request",
            "tool_or_connector_execution_request",
            "mcp_or_network_request",
            "approval_reuse_or_carryover",
            "fixture_loading_as_behavior",
            "dynamic_node_creation",
            "broker_or_sandbox_bypass",
        ):
            self.assertIn(category, content)

        for outcome in ("no_issue", "needs_review", "block_or_escalate"):
            self.assertIn(outcome, content)

        self.assertIn("advisory and non-authoritative", content)

    def test_advisory_example_json_is_valid_and_non_authoritative(self) -> None:
        self.assertTrue(ADVISORY_PATH.exists())
        content = json.loads(ADVISORY_PATH.read_text(encoding="utf-8"))

        self.assertTrue(content["display_only"])
        self.assertTrue(content["advisory_only"])
        self.assertTrue(content["not_authority"])
        self.assertTrue(content["cannot_approve"])
        self.assertTrue(content["cannot_grant_capabilities"])
        self.assertTrue(content["cannot_unblock_execution"])
        self.assertEqual(content["result"], "needs_review")

    def test_advisory_example_contains_no_obvious_credential_fragments(self) -> None:
        content = json.loads(ADVISORY_PATH.read_text(encoding="utf-8"))
        lowered_strings = [item.lower() for item in _walk_strings(content)]

        for fragment in FORBIDDEN_FRAGMENTS:
            with self.subTest(fragment=fragment):
                self.assertTrue(
                    all(fragment not in item for item in lowered_strings),
                    fragment,
                )

    def test_future_fixtures_readme_mentions_safeguard_advisory_as_inert(self) -> None:
        content = FUTURE_FIXTURES_README.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn("safeguard-advisory/WorkflowHarnessSafeguardPolicy.md", content)
        self.assertIn("safeguard-advisory/SafeguardAdvisory.example.json", content)
        self.assertIn("advisory-only", lowered)
        self.assertIn("not an approval mechanism", lowered)
        self.assertIn("not an authority source", lowered)


if __name__ == "__main__":
    unittest.main()
