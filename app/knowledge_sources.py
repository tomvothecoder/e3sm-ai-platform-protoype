import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

REQUIRED_FIELDS = {
    "repository",
    "path",
    "commit_sha",
    "document_type",
    "source_url",
    "local_path",
}
COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def load_knowledge_source_manifest(manifest_path: Path) -> list[dict[str, str]]:
    manifest: Any = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(
        manifest.get("documents"), list
    ):
        raise TypeError("Knowledge-source manifest must contain a documents list")

    documents: list[dict[str, str]] = []
    local_paths: set[str] = set()
    for position, raw_document in enumerate(manifest["documents"], start=1):
        if not isinstance(raw_document, dict):
            raise TypeError(f"Document {position} must be an object")

        missing_fields = REQUIRED_FIELDS - raw_document.keys()
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Document {position} is missing fields: {missing}")

        document = {field: raw_document[field] for field in REQUIRED_FIELDS}
        if not all(isinstance(value, str) and value for value in document.values()):
            raise ValueError(f"Document {position} fields must be non-empty strings")
        if not COMMIT_SHA_PATTERN.fullmatch(document["commit_sha"]):
            raise ValueError(f"Document {position} has an invalid commit SHA")

        local_path = PurePosixPath(document["local_path"])
        if local_path.is_absolute() or ".." in local_path.parts:
            raise ValueError(f"Document {position} has an unsafe local path")
        if document["local_path"] in local_paths:
            raise ValueError(f"Duplicate local path: {document['local_path']}")
        local_paths.add(document["local_path"])

        expected_url = (
            "https://raw.githubusercontent.com/"
            f"{document['repository']}/{document['commit_sha']}/{document['path']}"
        )
        if document["source_url"] != expected_url:
            raise ValueError(f"Document {position} source URL is not SHA-pinned")

        documents.append(document)

    if not documents:
        raise ValueError(
            "Knowledge-source manifest must contain at least one document"
        )
    return documents


def build_metadata_by_file(
    documents: list[dict[str, str]], knowledge_sources_dir: Path
) -> dict[Path, dict[str, str]]:
    return {
        (knowledge_sources_dir / document["local_path"]).resolve(): {
            field: document[field]
            for field in (
                "repository",
                "path",
                "commit_sha",
                "document_type",
                "source_url",
            )
        }
        for document in documents
    }


def build_knowledge_source_files(
    documents: list[dict[str, str]], knowledge_sources_dir: Path
) -> list[Path]:
    return [
        (knowledge_sources_dir / document["local_path"]).resolve()
        for document in documents
    ]


def compute_index_version(
    manifest_path: Path, embedding_model: str, knowledge_source_files: list[Path]
) -> str:
    digest = hashlib.sha256()
    digest.update(manifest_path.read_bytes())
    digest.update(b"\0")
    digest.update(embedding_model.encode())
    for knowledge_source_file in knowledge_source_files:
        digest.update(b"\0")
        digest.update(knowledge_source_file.read_bytes())
    return digest.hexdigest()
