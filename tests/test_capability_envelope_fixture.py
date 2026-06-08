from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = (
    ROOT
    / "fixtures"
    / "future"
    / "capability-envelope"
    / "CompiledCapabilityEnvelope.example.json"
)
FUTURE_FIXTURES_README = ROOT / "fixtures" / "future" / "README.md"
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


class CapabilityEnvelopeFixtureTests(unittest.TestCase):
    def test_example_fixture_is_valid_json_and_marks_inert_status(self) -> None:
        self.assertTrue(FIXTURE_PATH.exists())
        content = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        self.assertTrue(content["display_only"])
        self.assertTrue(content["not_executable"])
        self.assertTrue(content["compiler_owned"])
        self.assertIn("run_scope", content)
        self.assertIn("node_scope", content)
        self.assertIn("approval_binding", content)

    def test_example_fixture_contains_no_obvious_credential_fragments(self) -> None:
        content = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        lowered_strings = [item.lower() for item in _walk_strings(content)]

        for fragment in FORBIDDEN_FRAGMENTS:
            with self.subTest(fragment=fragment):
                self.assertTrue(
                    all(fragment not in item for item in lowered_strings),
                    fragment,
                )

    def test_future_fixtures_readme_mentions_capability_envelope_example_as_inert(
        self,
    ) -> None:
        content = FUTURE_FIXTURES_README.read_text(encoding="utf-8")
        lowered = content.lower()

        self.assertIn(
            "capability-envelope/CompiledCapabilityEnvelope.example.json",
            content,
        )
        self.assertIn("display-only", lowered)
        self.assertIn("not executable", lowered)
        self.assertIn("not consumed by compile or runtime behavior", lowered)
        self.assertIn("nothing here grants authority", lowered)


if __name__ == "__main__":
    unittest.main()
