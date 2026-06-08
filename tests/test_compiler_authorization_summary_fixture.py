from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "future"
    / "compiler-authorization-summary"
    / "CompilerAuthorizationSummary.example.json"
)
PROJECTION_FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "future"
    / "compiler-authorization-summary"
    / "CompilerAuthorizationSummaryProjection.example.json"
)
FUTURE_FIXTURES_README = ROOT / "fixtures" / "future" / "README.md"
FORBIDDEN_FRAGMENTS = (
    "secret",
    "password",
    "api_key",
    "private_key",
    "credential",
)


def _walk_strings(value: object) -> list[str]:
    if isinstance(value, dict):
        items: list[str] = []
        for _, nested in value.items():
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


class CompilerAuthorizationSummaryFixtureTests(unittest.TestCase):
    def test_example_fixture_is_valid_json_and_marks_inert_status(self) -> None:
        self.assertTrue(FIXTURE_PATH.exists())
        content = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        self.assertTrue(content["compiler_owned"])
        self.assertTrue(content["display_only"])
        self.assertTrue(content["not_executable"])
        self.assertTrue(content["not_consumed_by_v1"])
        self.assertTrue(content["no_runtime_authority"])
        self.assertTrue(content["no_credentials"])
        self.assertEqual(content["requested_authority"], [])
        self.assertEqual(content["approval_required"], [])
        self.assertEqual(content["blocked_authority"], [])
        self.assertEqual(content["unsupported_authority"], [])

    def test_example_fixture_contains_no_obvious_secret_values(self) -> None:
        content = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        lowered_strings = [item.lower() for item in _walk_strings(content)]

        for fragment in FORBIDDEN_FRAGMENTS:
            with self.subTest(fragment=fragment):
                self.assertTrue(
                    all(fragment not in item for item in lowered_strings),
                    fragment,
                )

    def test_future_fixtures_readme_mentions_authorization_summary_as_inert(
        self,
    ) -> None:
        content = FUTURE_FIXTURES_README.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn(
            "compiler-authorization-summary/CompilerAuthorizationSummary.example.json",
            content,
        )
        self.assertIn("compiler-owned", lowered)
        self.assertIn("not executable", lowered)
        self.assertIn("not consumed by compile or runtime behavior", lowered)
        self.assertIn("nothing here grants authority", lowered)

    def test_projection_fixture_is_valid_json_and_marks_inert_status(self) -> None:
        self.assertTrue(PROJECTION_FIXTURE_PATH.exists())
        content = json.loads(PROJECTION_FIXTURE_PATH.read_text(encoding="utf-8"))

        self.assertTrue(content["display_only"])
        self.assertTrue(content["future_only_example"])
        self.assertTrue(content["not_generated_by_v1"])
        self.assertTrue(content["not_consumed_by_v1"])
        self.assertTrue(content["no_runtime_authority"])
        self.assertTrue(content["no_execution"])
        self.assertTrue(content["no_credentials"])
        self.assertEqual(content["requested_authority"], [])
        self.assertEqual(content["approval_required"], [])
        self.assertEqual(content["blocked_authority"], [])
        self.assertEqual(content["unsupported_authority"], [])
        self.assertEqual(
            content["source_artifacts"],
            [
                "RequestedAuth.json",
                "ApprovalRequests.json",
                "static_validation_diagnostics",
            ],
        )
        lowered_strings = [item.lower() for item in _walk_strings(content)]
        self.assertTrue(all("read_text" not in item for item in lowered_strings))
        self.assertTrue(all("open(" not in item for item in lowered_strings))
        self.assertTrue(all("load file" not in item for item in lowered_strings))

    def test_projection_fixture_contains_no_obvious_secret_values(self) -> None:
        content = json.loads(PROJECTION_FIXTURE_PATH.read_text(encoding="utf-8"))
        lowered_strings = [item.lower() for item in _walk_strings(content)]

        for fragment in FORBIDDEN_FRAGMENTS:
            with self.subTest(fragment=fragment):
                self.assertTrue(
                    all(fragment not in item for item in lowered_strings),
                    fragment,
                )

    def test_future_fixtures_readme_mentions_projection_as_inert(self) -> None:
        content = FUTURE_FIXTURES_README.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn(
            "compiler-authorization-summary/CompilerAuthorizationSummaryProjection.example.json",
            content,
        )
        self.assertIn("generated by v1", lowered)
        self.assertIn("not consumed by compile or runtime behavior", lowered)
        self.assertIn("not executable", lowered)
        self.assertIn("grants no runtime authority", lowered)


if __name__ == "__main__":
    unittest.main()
