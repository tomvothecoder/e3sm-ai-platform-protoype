import argparse
import os
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from app.knowledge_sources import load_knowledge_source_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT_ROOT / "data" / "e3sm-knowledge-sources.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "e3sm"


def download_document(source_url: str) -> bytes:
    request = Request(
        source_url,
        headers={
            "User-Agent": "e3sm-ai-platform-prototype-knowledge-sources-sync"
        },
    )
    with urlopen(request, timeout=30) as response:
        content = response.read()
    if not content.strip():
        raise ValueError(f"Downloaded empty document: {source_url}")
    content.decode("utf-8")
    return content


def write_atomic(destination: Path, content: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent, delete=False
        ) as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)
        temporary_path.replace(destination)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def sync_knowledge_sources(manifest_path: Path, output_dir: Path) -> int:
    documents = load_knowledge_source_manifest(manifest_path)
    downloads = [
        (
            output_dir / document["local_path"],
            download_document(document["source_url"]),
            document,
        )
        for document in documents
    ]
    for destination, content, document in downloads:
        write_atomic(destination, content)
        print(f"Synced {document['repository']}:{document['path']}")
    return len(documents)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync the pinned E3SM knowledge sources"
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    document_count = sync_knowledge_sources(args.manifest, args.output_dir)
    print(f"Synced {document_count} documents into {args.output_dir}")


if __name__ == "__main__":
    main()
