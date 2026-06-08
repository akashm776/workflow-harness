from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
SIDE_EFFECT_CLASS_REGISTRY = ROOT / "registry" / "SideEffectClasses.json"

REQUIRED_CLASS_IDS = {
    "none",
    "read_local_fixture",
    "read_external",
    "write_external",
    "credentialed_read",
    "credentialed_write",
    "network",
    "human_review",
}


def load_registry() -> dict:
    return json.loads(SIDE_EFFECT_CLASS_REGISTRY.read_text(encoding="utf-8"))


class SideEffectClassRegistryTests(unittest.TestCase):
    def test_side_effect_class_registry_exists_and_is_inert_only(self) -> None:
        self.assertTrue(SIDE_EFFECT_CLASS_REGISTRY.exists())
        payload = load_registry()

        self.assertEqual(payload["field_name"], "side_effect_class")
        self.assertIn("inert governance data only", payload["note"])
        self.assertIn("does not enable execution", payload["note"].lower())
        self.assertIn("approve anything", payload["note"].lower())

        non_goals = " ".join(payload["non_goals"]).lower()
        self.assertIn("does not enable execution", non_goals)
        self.assertIn("does not approve anything", non_goals)

    def test_side_effect_classes_have_stable_string_ids_and_descriptions(self) -> None:
        payload = load_registry()
        classes = payload["classes"]
        self.assertIsInstance(classes, list)
        self.assertGreater(len(classes), 0)

        ids = []
        for entry in classes:
            with self.subTest(entry=entry):
                self.assertIsInstance(entry, dict)
                self.assertIsInstance(entry.get("id"), str)
                self.assertTrue(entry["id"])
                self.assertIsInstance(entry.get("description"), str)
                self.assertTrue(entry["description"].strip())
                ids.append(entry["id"])

        self.assertEqual(len(ids), len(set(ids)))

    def test_required_side_effect_classes_are_present(self) -> None:
        payload = load_registry()
        class_ids = {entry["id"] for entry in payload["classes"]}
        self.assertTrue(REQUIRED_CLASS_IDS.issubset(class_ids))


if __name__ == "__main__":
    unittest.main()
