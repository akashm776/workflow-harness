"""Dependency digest helpers for deterministic compiled-artifact inputs."""

from __future__ import annotations

from typing import Literal, Mapping, NotRequired, TypedDict

from .canonical_json import canonical_sha256_hex


HASH_ALGORITHM = "sha256"
CANONICALIZATION_VERSION = "canon-json-v1"


DependencyArtifactGroup = Literal[
    "proposal",
    "static_governance",
    "run_scoped_governance",
    "evidence",
    "schema_meta",
    "compiler_meta",
]


class DependencyDigestEntry(TypedDict):
    """Typed shape for one declared input dependency digest entry."""

    artifact_group: DependencyArtifactGroup
    artifact_path: str
    content_digest: str
    hash_algorithm: str
    canonicalization_version: str
    revision_id: NotRequired[str]


def make_dependency_digest_entry(
    *,
    artifact_group: DependencyArtifactGroup,
    artifact_path: str,
    content_digest: str,
    revision_id: str | None = None,
) -> DependencyDigestEntry:
    """Create one normalized dependency digest entry."""

    entry: DependencyDigestEntry = {
        "artifact_group": artifact_group,
        "artifact_path": artifact_path,
        "content_digest": content_digest,
        "hash_algorithm": HASH_ALGORITHM,
        "canonicalization_version": CANONICALIZATION_VERSION,
    }
    if revision_id is not None:
        entry["revision_id"] = revision_id
    return entry


def validate_dependency_digest_entry(entry: Mapping[str, object]) -> None:
    """Validate the required fields for a dependency digest entry."""

    required_fields = (
        "artifact_group",
        "artifact_path",
        "content_digest",
        "hash_algorithm",
        "canonicalization_version",
    )
    for field_name in required_fields:
        value = entry.get(field_name)
        if not isinstance(value, str) or not value:
            raise ValueError(f"dependency digest entry missing required field: {field_name}")

    hash_algorithm = entry["hash_algorithm"]
    if hash_algorithm != HASH_ALGORITHM:
        raise ValueError(f"unsupported hash_algorithm: {hash_algorithm}")

    canonicalization_version = entry["canonicalization_version"]
    if canonicalization_version != CANONICALIZATION_VERSION:
        raise ValueError(
            f"unsupported canonicalization_version: {canonicalization_version}"
        )


def normalize_dependency_digest_entries(
    entries: list[DependencyDigestEntry],
) -> list[DependencyDigestEntry]:
    """Normalize and deterministically order dependency digest entries.

    Ordering is by `(artifact_group, artifact_path, content_digest, revision_id?)`.
    """

    normalized: list[DependencyDigestEntry] = []
    for entry in entries:
        validate_dependency_digest_entry(entry)
        normalized.append(dict(entry))  # type: ignore[arg-type]

    normalized.sort(
        key=lambda item: (
            item["artifact_group"],
            item["artifact_path"],
            item["content_digest"],
            item.get("revision_id", ""),
        )
    )
    return normalized


def compute_dependency_set_digest(entries: list[DependencyDigestEntry]) -> str:
    """Compute one deterministic digest over the normalized dependency set."""

    return canonical_sha256_hex(normalize_dependency_digest_entries(entries))
