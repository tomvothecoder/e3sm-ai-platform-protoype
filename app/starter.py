import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

from app.corpus import (
    build_corpus_files,
    build_metadata_by_file,
    compute_index_version,
    load_corpus_manifest,
)

load_dotenv()

project_root = Path(__file__).resolve().parents[1]
manifest_path = project_root / "data" / "e3sm-corpus.json"
corpus_dir = project_root / "data" / "e3sm"
storage_dir = project_root / "storage" / "e3sm"
index_version_path = storage_dir / "index-version"
embedding_model = "BAAI/bge-small-en-v1.5"

livai_llm = OpenAILike(
    model=os.environ["ASSISTANT_LIVAI_MODEL"],
    api_base=os.environ["ASSISTANT_LIVAI_BASE_URL"],
    api_key=os.environ["ASSISTANT_LIVAI_API_KEY"],
    is_chat_model=True,
    is_function_calling_model=True,
)

Settings.llm = livai_llm
Settings.embed_model = HuggingFaceEmbedding(model_name=embedding_model)

documents_manifest = load_corpus_manifest(manifest_path)
corpus_files = build_corpus_files(documents_manifest, corpus_dir)
metadata_by_file = build_metadata_by_file(documents_manifest, corpus_dir)
index_version = compute_index_version(manifest_path, embedding_model, corpus_files)


def file_metadata(file_path: str) -> dict[str, str]:
    path = Path(file_path).resolve()
    return {**metadata_by_file[path], "file_path": file_path}


if (
    index_version_path.exists()
    and index_version_path.read_text(encoding="utf-8").strip() == index_version
):
    storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
    index = load_index_from_storage(storage_context)
else:
    documents = SimpleDirectoryReader(
        input_files=corpus_files,
        file_metadata=file_metadata,
    ).load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=str(storage_dir))
    index_version_path.write_text(index_version, encoding="utf-8")

query_engine = index.as_query_engine()


async def search_documents(query: str) -> str:
    """Answer questions about E3SM, CIME case workflows, and SimBoard."""
    response = await query_engine.aquery(query)
    return str(response)


agent = FunctionAgent(
    tools=[search_documents],
    llm=livai_llm,
    system_prompt=(
        "You are an E3SM assistant. Use the document search tool for questions "
        "about E3SM, CIME case workflows, and SimBoard. Base answers on the "
        "indexed corpus and identify source documents when possible."
    ),
)


async def main() -> None:
    response = await agent.run(
        user_msg=(
            "How do I create, configure, and run an E3SM case with CIME, and "
            "where does SimBoard fit into that workflow?"
        )
    )
    print(response)


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())
