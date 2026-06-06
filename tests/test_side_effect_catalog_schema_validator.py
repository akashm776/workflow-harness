from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from compiler.side_effect_catalog_schema_validator import (
    validate_side_effect_catalog_schema,
)


def _valid_entry() -> dict:
    return {
        "tool_name": "local-file-reader",
        "version": "1.0.0",
        "side_effect_class": "read-only",
        "allowed_scopes": ["read:fixtures/simple"],
        "authority_dimensions": ["tool", "scope"],
        "sandbox_requirements": {"network": "none"},
        "audit_requirements": {"log": "always"},
        "review_or_approval_requirements": {"review": "auto"},
    }


def _valid_catalog() -> dict:
    return {
        "catalog_version": "catalog-001",
        "entries": [_valid_entry()],
    }


class SideEffectCatalogSchemaValidatorTests(unittest.TestCase):
    def _validate(self, catalog: object) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SideEffectCatalog.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")
            result = validate_side_effect_catalog_schema(path)
            # The validator must not write any extra files.
            self.assertEqual(
                {p.name for p in Path(tmp).iterdir()}, {"SideEffectCatalog.json"}
            )
        return result

    def _assert_schema_failure(self, result: dict, *, path_fragment: str) -> None:
        self.assertFalse(result["ok"])
        diagnostic = result["diagnostic"]
        self.assertEqual(diagnostic["error_code"], "INVALID_ARTIFACT_SCHEMA")
        self.assertEqual(diagnostic["component"], "static_schema_validator")
        self.assertEqual(diagnostic["artifact"], "SideEffectCatalog.json")
        self.assertIn(path_fragment, diagnostic["message"])

    def _mutate_entry(self, mutate) -> dict:
        catalog = _valid_catalog()
        mutate(catalog["entries"][0])
        return self._validate(catalog)

    def test_valid_catalog_passes(self) -> None:
        result = self._validate(_valid_catalog())
        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_valid_catalog_with_connector_entry_passes(self) -> None:
        catalog = _valid_catalog()
        entry = catalog["entries"][0]
        del entry["tool_name"]
        entry["connector_name"] = "fixture-catalog"
        result = self._validate(catalog)
        self.assertTrue(result["ok"])

    def test_committed_example_future_fixture_passes(self) -> None:
        root = Path(__file__).resolve().parent.parent
        fixture_path = (
            root / "fixtures" / "future" / "side-effect-catalog"
            / "SideEffectCatalog.json"
        )
        result = validate_side_effect_catalog_schema(fixture_path)
        self.assertTrue(result["ok"])
        self.assertIsNone(result["diagnostic"])

    def test_root_non_object_fails(self) -> None:
        self._assert_schema_failure(self._validate(["not", "an", "object"]),
                                    path_fragment="root $")

    def test_missing_catalog_version_fails(self) -> None:
        catalog = _valid_catalog()
        del catalog["catalog_version"]
        self._assert_schema_failure(self._validate(catalog),
                                    path_fragment="$.catalog_version")

    def test_non_string_catalog_version_fails(self) -> None:
        catalog = _valid_catalog()
        catalog["catalog_version"] = 1
        self._assert_schema_failure(self._validate(catalog),
                                    path_fragment="$.catalog_version")

    def test_missing_entries_fails(self) -> None:
        catalog = _valid_catalog()
        del catalog["entries"]
        self._assert_schema_failure(self._validate(catalog),
                                    path_fragment="$.entries")

    def test_non_list_entries_fails(self) -> None:
        catalog = _valid_catalog()
        catalog["entries"] = {"tool_name": "x"}
        self._assert_schema_failure(self._validate(catalog),
                                    path_fragment="$.entries")

    def test_non_object_entry_fails(self) -> None:
        catalog = _valid_catalog()
        catalog["entries"] = ["not-an-object"]
        self._assert_schema_failure(self._validate(catalog),
                                    path_fragment="$.entries[0]")

    def test_neither_tool_nor_connector_fails(self) -> None:
        def mutate(entry: dict) -> None:
            del entry["tool_name"]
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="exactly one of tool_name or connector_name",
        )

    def test_both_tool_and_connector_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["connector_name"] = "fixture-catalog"
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="exactly one of tool_name or connector_name",
        )

    def test_non_string_tool_name_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["tool_name"] = 5
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].tool_name",
        )

    def test_non_string_connector_name_fails(self) -> None:
        def mutate(entry: dict) -> None:
            del entry["tool_name"]
            entry["connector_name"] = 5
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].connector_name",
        )

    def test_missing_version_fails(self) -> None:
        def mutate(entry: dict) -> None:
            del entry["version"]
        self._assert_schema_failure(
            self._mutate_entry(mutate), path_fragment="$.entries[0].version"
        )

    def test_non_string_version_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["version"] = 1
        self._assert_schema_failure(
            self._mutate_entry(mutate), path_fragment="$.entries[0].version"
        )

    def test_missing_side_effect_class_fails(self) -> None:
        def mutate(entry: dict) -> None:
            del entry["side_effect_class"]
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].side_effect_class",
        )

    def test_non_string_side_effect_class_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["side_effect_class"] = 3
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].side_effect_class",
        )

    def test_unknown_side_effect_class_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["side_effect_class"] = "teleport"
        result = self._mutate_entry(mutate)
        self._assert_schema_failure(
            result, path_fragment="$.entries[0].side_effect_class"
        )
        self.assertIn("must be one of", result["diagnostic"]["message"])

    def test_all_allowed_side_effect_classes_pass(self) -> None:
        for side_effect_class in (
            "read-only",
            "local write",
            "external write",
            "network call",
            "export",
            "deletion / destructive action",
        ):
            with self.subTest(side_effect_class=side_effect_class):
                catalog = _valid_catalog()
                catalog["entries"][0]["side_effect_class"] = side_effect_class
                self.assertTrue(self._validate(catalog)["ok"])

    def test_non_list_allowed_scopes_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["allowed_scopes"] = "read:all"
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].allowed_scopes",
        )

    def test_non_list_authority_dimensions_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["authority_dimensions"] = "tool"
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].authority_dimensions",
        )

    def test_missing_sandbox_requirements_fails(self) -> None:
        def mutate(entry: dict) -> None:
            del entry["sandbox_requirements"]
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].sandbox_requirements",
        )

    def test_non_object_sandbox_requirements_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["sandbox_requirements"] = ["none"]
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].sandbox_requirements",
        )

    def test_missing_audit_requirements_fails(self) -> None:
        def mutate(entry: dict) -> None:
            del entry["audit_requirements"]
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].audit_requirements",
        )

    def test_non_object_audit_requirements_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["audit_requirements"] = "always"
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].audit_requirements",
        )

    def test_missing_review_or_approval_requirements_fails(self) -> None:
        def mutate(entry: dict) -> None:
            del entry["review_or_approval_requirements"]
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].review_or_approval_requirements",
        )

    def test_non_object_review_or_approval_requirements_fails(self) -> None:
        def mutate(entry: dict) -> None:
            entry["review_or_approval_requirements"] = "auto"
        self._assert_schema_failure(
            self._mutate_entry(mutate),
            path_fragment="$.entries[0].review_or_approval_requirements",
        )

    def test_validator_is_standalone_and_not_wired_into_static_validation(self) -> None:
        # The validator is imported directly from its own module, independent of
        # compiler.static_validation. It is not referenced by static_validation.
        import compiler.side_effect_catalog_schema_validator as module
        from compiler import static_validation

        self.assertTrue(hasattr(module, "validate_side_effect_catalog_schema"))
        self.assertFalse(
            hasattr(static_validation, "validate_side_effect_catalog_schema")
        )
        static_validation_source = Path(static_validation.__file__).read_text(
            encoding="utf-8"
        )
        self.assertNotIn(
            "side_effect_catalog_schema_validator", static_validation_source
        )


if __name__ == "__main__":
    unittest.main()
