from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT / "fixtures" / "future" / "innovation-context"
README_PATH = FIXTURE_DIR / "README.md"
JSON_FIXTURES = {
    "ProgramContext.json": {
        "program_name",
        "mission_context",
        "constraints",
        "stakeholders",
        "current_capabilities",
    },
    "RepoContextSummary.json": {
        "portfolio_name",
        "repositories",
        "cross_repo_themes",
    },
    "ConfluenceContextSummary.json": {
        "knowledge_spaces",
        "common_guidance",
    },
    "IssueTrackerContextSummary.json": {
        "project_summaries",
        "recurring_request_patterns",
    },
    "Rubric.json": {
        "rubric_name",
        "scoring_scale",
        "dimensions",
    },
}
FORBIDDEN_FRAGMENTS = ("token", "secret", "password", "api_key", "credential")


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


class InnovationContextFixturesTests(unittest.TestCase):
    def test_fixture_files_exist(self) -> None:
        self.assertTrue(FIXTURE_DIR.exists())
        for file_name in (*JSON_FIXTURES.keys(), "README.md"):
            self.assertTrue((FIXTURE_DIR / file_name).exists(), file_name)

    def test_json_fixtures_are_valid_and_non_sensitive(self) -> None:
        for file_name, required_keys in JSON_FIXTURES.items():
            with self.subTest(file_name=file_name):
                content = json.loads((FIXTURE_DIR / file_name).read_text(encoding="utf-8"))
                self.assertTrue(required_keys.issubset(content.keys()))
                for fragment in FORBIDDEN_FRAGMENTS:
                    lowered_strings = [item.lower() for item in _walk_strings(content)]
                    self.assertTrue(
                        all(fragment not in item for item in lowered_strings),
                        fragment,
                    )

    def test_readme_marks_fixtures_as_local_fake_and_inert(self) -> None:
        content = README_PATH.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn("local fake data only", lowered)
        self.assertIn("future-only example inputs", lowered)
        self.assertIn("v1 does **not** load these fixtures", lowered)
        self.assertIn("v1 does **not** execute anything", lowered)
        self.assertIn("v1 does **not** connect to tools, connectors, or mcp", lowered)
        self.assertIn("control-plane inputs", lowered)
        self.assertIn("grant no authority", lowered)
        self.assertIn("no real program data", lowered)
        self.assertIn("no external reads", lowered)
        self.assertIn("no credentials", lowered)


if __name__ == "__main__":
    unittest.main()
