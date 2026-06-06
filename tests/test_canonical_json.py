from __future__ import annotations

import unittest

from compiler.canonical_json import canonical_json_text, canonical_sha256_hex


class CanonicalJsonTests(unittest.TestCase):
    def test_object_key_order_does_not_change_canonical_text(self) -> None:
        left = {"b": 2, "a": 1}
        right = {"a": 1, "b": 2}

        self.assertEqual(canonical_json_text(left), canonical_json_text(right))
        self.assertEqual(canonical_sha256_hex(left), canonical_sha256_hex(right))

    def test_array_order_is_sensitive_by_default(self) -> None:
        left = {"items": ["a", "b", "c"]}
        right = {"items": ["c", "b", "a"]}

        self.assertNotEqual(canonical_json_text(left), canonical_json_text(right))
        self.assertNotEqual(canonical_sha256_hex(left), canonical_sha256_hex(right))

    def test_object_keys_are_emitted_in_sorted_order(self) -> None:
        self.assertEqual(
            canonical_json_text({"b": 1, "a": 2, "c": 3}),
            '{"a":2,"b":1,"c":3}',
        )

    def test_arrays_preserve_their_given_order(self) -> None:
        self.assertEqual(
            canonical_json_text([3, 1, 2]),
            "[3,1,2]",
        )

    def test_separators_are_compact_with_no_spaces(self) -> None:
        text = canonical_json_text({"a": 1, "b": [2, 3]})

        self.assertEqual(text, '{"a":1,"b":[2,3]}')
        self.assertNotIn(", ", text)
        self.assertNotIn(": ", text)

    def test_ensure_ascii_false_keeps_non_ascii_literal(self) -> None:
        text = canonical_json_text({"name": "café é"})

        self.assertIn("é", text)
        self.assertNotIn("\\u00e9", text)

    def test_canonical_sha256_hex_is_stable_for_known_simple_value(self) -> None:
        # Pinned digest of the canonical text {"a":1}. If this changes, the
        # canonical contract changed and content digests / approval_subject_hash
        # behavior changed with it.
        self.assertEqual(
            canonical_sha256_hex({"a": 1}),
            "015abd7f5cc57a2dd94b7590f04ad8084273905ee33ec5cebeae62276a97f862",
        )

    def test_nan_currently_serializes_as_nan_documented_limitation_not_strict_json(
        self,
    ) -> None:
        # Characterization only. NaN serializing to the literal `NaN` is invalid
        # strict JSON and is a documented v1 limitation (see docs/CANONICAL_JSON_V1.md),
        # not desired behavior. This test pins current behavior; it does not bless it.
        self.assertEqual(canonical_json_text(float("nan")), "NaN")

    def test_int_and_float_serialize_differently_for_equal_values(self) -> None:
        # Characterization of current behavior: 1 and 1.0 are not interchangeable
        # in canonical text, which is why authority-bearing fields should avoid
        # floats (see docs/CANONICAL_JSON_V1.md).
        self.assertEqual(canonical_json_text(1), "1")
        self.assertEqual(canonical_json_text(1.0), "1.0")
        self.assertNotEqual(canonical_json_text(1), canonical_json_text(1.0))


if __name__ == "__main__":
    unittest.main()
