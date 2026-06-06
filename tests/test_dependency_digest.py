from __future__ import annotations

import unittest

from compiler.dependency_digest import (
    CANONICALIZATION_VERSION,
    HASH_ALGORITHM,
    compute_dependency_set_digest,
    make_dependency_digest_entry,
    normalize_dependency_digest_entries,
    validate_dependency_digest_entry,
)


class DependencyDigestTests(unittest.TestCase):
    def test_dependency_set_digest_is_deterministic_for_reordered_entries(self) -> None:
        left = [
            make_dependency_digest_entry(
                artifact_group="proposal",
                artifact_path="nodes/retrieve-1/Task.json",
                content_digest="aaa",
                revision_id="node-rev-1",
            ),
            make_dependency_digest_entry(
                artifact_group="static_governance",
                artifact_path="policy/global-policy.json",
                content_digest="bbb",
            ),
        ]
        right = list(reversed(left))

        self.assertEqual(compute_dependency_set_digest(left), compute_dependency_set_digest(right))

    def test_normalization_orders_entries_by_stable_key(self) -> None:
        entries = [
            make_dependency_digest_entry(
                artifact_group="static_governance",
                artifact_path="policy/z.json",
                content_digest="bbb",
            ),
            make_dependency_digest_entry(
                artifact_group="proposal",
                artifact_path="workflow/WorkflowSpec.json",
                content_digest="aaa",
            ),
        ]

        normalized = normalize_dependency_digest_entries(entries)
        self.assertEqual(normalized[0]["artifact_group"], "proposal")
        self.assertEqual(normalized[0]["artifact_path"], "workflow/WorkflowSpec.json")

    def test_required_fields_are_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "artifact_path"):
            validate_dependency_digest_entry(
                {
                    "artifact_group": "proposal",
                    "content_digest": "abc",
                    "hash_algorithm": HASH_ALGORITHM,
                    "canonicalization_version": CANONICALIZATION_VERSION,
                }
            )

        with self.assertRaisesRegex(ValueError, "artifact_group"):
            validate_dependency_digest_entry(
                {
                    "artifact_path": "workflow/WorkflowSpec.json",
                    "content_digest": "abc",
                    "hash_algorithm": HASH_ALGORITHM,
                    "canonicalization_version": CANONICALIZATION_VERSION,
                }
            )

        with self.assertRaisesRegex(ValueError, "content_digest"):
            validate_dependency_digest_entry(
                {
                    "artifact_group": "proposal",
                    "artifact_path": "workflow/WorkflowSpec.json",
                    "hash_algorithm": HASH_ALGORITHM,
                    "canonicalization_version": CANONICALIZATION_VERSION,
                }
            )

    def test_builder_populates_fixed_hash_metadata(self) -> None:
        entry = make_dependency_digest_entry(
            artifact_group="proposal",
            artifact_path="workflow/WorkflowSpec.json",
            content_digest="abc",
        )

        self.assertEqual(entry["hash_algorithm"], HASH_ALGORITHM)
        self.assertEqual(entry["canonicalization_version"], CANONICALIZATION_VERSION)

    def test_unsupported_hash_algorithm_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported hash_algorithm"):
            validate_dependency_digest_entry(
                {
                    "artifact_group": "proposal",
                    "artifact_path": "workflow/WorkflowSpec.json",
                    "content_digest": "abc",
                    "hash_algorithm": "sha512",
                    "canonicalization_version": CANONICALIZATION_VERSION,
                }
            )

    def test_unsupported_canonicalization_version_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported canonicalization_version"):
            validate_dependency_digest_entry(
                {
                    "artifact_group": "proposal",
                    "artifact_path": "workflow/WorkflowSpec.json",
                    "content_digest": "abc",
                    "hash_algorithm": HASH_ALGORITHM,
                    "canonicalization_version": "canon-json-v999",
                }
            )


if __name__ == "__main__":
    unittest.main()
