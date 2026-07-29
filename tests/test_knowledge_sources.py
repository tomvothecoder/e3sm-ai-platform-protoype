import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.knowledge_sources import (
    build_knowledge_source_files,
    build_metadata_by_file,
    compute_index_version,
    load_knowledge_source_manifest,
)
from scripts.sync_knowledge_sources import sync_knowledge_sources

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "data" / "e3sm-knowledge-sources.json"
KNOWLEDGE_SOURCES_DIR = PROJECT_ROOT / "data" / "e3sm"


class KnowledgeSourceManifestTests(unittest.TestCase):
    def test_repository_manifest_is_valid_and_complete(self) -> None:
        documents = load_knowledge_source_manifest(MANIFEST_PATH)

        self.assertEqual(len(documents), 9)
        self.assertEqual(len({doc["local_path"] for doc in documents}), 9)
        for document in documents:
            document_path = KNOWLEDGE_SOURCES_DIR / document["local_path"]
            self.assertTrue(document_path.is_file(), document_path)
            self.assertGreater(document_path.stat().st_size, 0)

    def test_metadata_is_keyed_by_resolved_local_file(self) -> None:
        documents = load_knowledge_source_manifest(MANIFEST_PATH)

        metadata_by_file = build_metadata_by_file(
            documents, KNOWLEDGE_SOURCES_DIR
        )

        first_document = documents[0]
        first_path = (
            KNOWLEDGE_SOURCES_DIR / first_document["local_path"]
        ).resolve()
        self.assertEqual(
            metadata_by_file[first_path]["commit_sha"],
            first_document["commit_sha"],
        )
        self.assertEqual(
            metadata_by_file[first_path]["source_url"],
            first_document["source_url"],
        )

    def test_manifest_rejects_unpinned_source_url(self) -> None:
        manifest = {
            "documents": [
                {
                    "repository": "example/repository",
                    "path": "README.md",
                    "commit_sha": "a" * 40,
                    "document_type": "markdown",
                    "source_url": (
                        "https://raw.githubusercontent.com/"
                        "example/repository/main/README.md"
                    ),
                    "local_path": "example/README.md",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as temporary_dir:
            manifest_path = Path(temporary_dir) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "not SHA-pinned"):
                load_knowledge_source_manifest(manifest_path)

    def test_index_version_changes_with_embedding_model(self) -> None:
        documents = load_knowledge_source_manifest(MANIFEST_PATH)
        knowledge_source_files = build_knowledge_source_files(
            documents, KNOWLEDGE_SOURCES_DIR
        )
        first_version = compute_index_version(
            MANIFEST_PATH, "model-a", knowledge_source_files
        )
        second_version = compute_index_version(
            MANIFEST_PATH, "model-b", knowledge_source_files
        )

        self.assertNotEqual(first_version, second_version)

    def test_manifest_files_exclude_unlisted_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            knowledge_sources_dir = Path(temporary_dir)
            listed_file = knowledge_sources_dir / "listed.md"
            extra_file = knowledge_sources_dir / "extra.md"
            listed_file.write_text("listed", encoding="utf-8")
            extra_file.write_text("extra", encoding="utf-8")

            knowledge_source_files = build_knowledge_source_files(
                [{"local_path": "listed.md"}],
                knowledge_sources_dir,
            )

            self.assertEqual(knowledge_source_files, [listed_file.resolve()])
            self.assertNotIn(extra_file.resolve(), knowledge_source_files)

    def test_index_version_changes_with_knowledge_source_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            knowledge_source_file = Path(temporary_dir) / "document.md"
            knowledge_source_file.write_text("first version", encoding="utf-8")
            first_version = compute_index_version(
                MANIFEST_PATH, "model", [knowledge_source_file]
            )

            knowledge_source_file.write_text("second version", encoding="utf-8")
            second_version = compute_index_version(
                MANIFEST_PATH, "model", [knowledge_source_file]
            )

            self.assertNotEqual(first_version, second_version)

    def test_download_failure_writes_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            output_dir = Path(temporary_dir) / "knowledge-sources"
            with (
                patch(
                    "scripts.sync_knowledge_sources.download_document",
                    side_effect=[b"first document", RuntimeError("network failure")],
                ),
                self.assertRaisesRegex(RuntimeError, "network failure"),
            ):
                sync_knowledge_sources(MANIFEST_PATH, output_dir)

            self.assertFalse(output_dir.exists())


if __name__ == "__main__":
    unittest.main()
