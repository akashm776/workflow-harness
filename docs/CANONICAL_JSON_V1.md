# Canonical JSON v1 Contract

This document describes the **currently implemented** canonical JSON contract. It
is descriptive, not aspirational: it records what `compiler/canonical_json.py`
does today so the behavior can be relied on and reviewed as part of the trust
boundary. It does not propose new behavior and does not change hashing.

See also `docs/SECURITY_ASSUMPTIONS_AND_LIMITS.md` for why canonical JSON is part
of the trust boundary.

## Entry Points

- `canonical_json_text(value)` is the project serializer. It renders a value to
  canonical JSON text.
- `canonical_json_bytes(value)` returns that same text encoded as UTF-8 bytes.
- `canonical_sha256_hex(value)` hashes the canonical JSON text (via its UTF-8
  bytes) with SHA-256 and returns lowercase hex.

All authority-bearing identities that depend on canonicalization — content
digests, dependency digests, revision ids, and `approval_subject_hash` — derive
from these functions.

## Implemented Contract

The v1 contract is exactly the behavior of `canonical_json_text(...)`:

- **UTF-8 text.** Canonical output is UTF-8 (bytes are produced by encoding the
  canonical text as UTF-8).
- **Sort object keys.** Object keys are emitted in sorted order
  (`sort_keys=True`).
- **Compact separators.** Items are separated by `,` and key/value pairs by `:`
  with no extra whitespace (`separators=(",", ":")`).
- **`ensure_ascii=False`.** Non-ASCII characters are emitted as literal UTF-8
  rather than `\uXXXX` escapes. For example `"é"` is emitted as `é`.
- **Preserve JSON value structure.** Arrays keep their existing order (they are
  not reordered), and the value tree is otherwise preserved as given. Only object
  key ordering and whitespace are normalized.

A small worked example:

```text
canonical_json_text({"b": 1, "a": 2, "nested": {"z": [3, 2, 1], "y": "é"}})
=> {"a":2,"b":1,"nested":{"y":"é","z":[3,2,1]}}
```

## Current Limitations

These are limitations of the v1 contract as implemented. They are recorded so
that callers do not assume guarantees that are not present.

- **Not RFC 8785 / JCS.** Do not claim RFC 8785 (JSON Canonicalization Scheme)
  compliance unless and until it is actually implemented. The current contract is
  "sorted keys, compact separators, non-escaped UTF-8" — it is not the JCS number
  canonicalization or full JCS rule set.
- **Floats and non-finite numbers.** Float formatting is not normalized by this
  contract, and non-finite values serialize to the literal tokens `NaN` /
  `Infinity` / `-Infinity`, which are not valid JSON and are not guaranteed to be
  stable or interoperable. Authority-bearing fields should use strings or
  integers.

## Authority-Bearing Artifacts Are Validation-Gated

The serializer in `compiler/canonical_json.py` is unchanged: it still emits `NaN`
/ `Infinity` / `-Infinity` if asked to, and that behavior remains characterized
in `tests/test_canonical_json.py`. The mitigation is a separate validation gate,
not a change to canonicalization.

Authority-bearing artifacts are now validation-gated against floats and
non-finite values **before they become load-bearing** (before they feed canonical
hashing, content digests, `approval_subject_hash`, or runtime verification). The
gate is `compiler/authority_value_validator.py`, applied during compile to the
loaded input artifacts and to the compiler-emitted authority artifacts. A
disallowed value fails the compile with a `DISALLOWED_AUTHORITY_VALUE`
diagnostic. See `docs/SECURITY_ASSUMPTIONS_AND_LIMITS.md`.

In short: `NaN` serialization remains characterized at the serializer level, but
authority-bearing artifacts must not admit floats or non-finite values, and the
compiler now enforces that.

## Why This Is Stability-Sensitive

Changing this contract changes content digests and `approval_subject_hash`
behavior. Any change to key ordering, separators, escaping, encoding, or number
handling silently changes every derived hash and revision id, which can
invalidate existing compiled artifacts and approval matches. The contract should
therefore remain stable and documented before real authority reuse or external
interoperability depends on it.
