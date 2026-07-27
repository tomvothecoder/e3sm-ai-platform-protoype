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

load_dotenv()

livai_llm = OpenAILike(
    model=os.environ["ASSISTANT_LIVAI_MODEL"],
    api_base=os.environ["ASSISTANT_LIVAI_BASE_URL"],
    api_key=os.environ["ASSISTANT_LIVAI_API_KEY"],
    is_chat_model=True,
    is_function_calling_model=True,
)

Settings.llm = livai_llm
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Load the persisted index, or create and save it on the first run.
storage_dir = Path("storage")
if storage_dir.exists():
    storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
    index = load_index_from_storage(storage_context)
else:
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=str(storage_dir))

query_engine = index.as_query_engine()


# Define a simple calculator tool
def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b


async def search_documents(query: str) -> str:
    """Useful for answering natural language questions about an personal essay written by Paul Graham."""
    response = await query_engine.aquery(query)
    return str(response)


# Create an enhanced workflow with both tools
agent = FunctionAgent(
    tools=[multiply, search_documents],
    llm=livai_llm,
    system_prompt="""You are a helpful assistant that can perform calculations
    and search through documents to answer questions.""",
)


# Now we can ask questions about the documents or do calculations
async def main():
    response = await agent.run(
        user_msg="What did the author do in college? Also, what's 7 * 8?"
    )
    print(response)
    response = await agent.run(
        user_msg="How good is my vector embedding model? Can you give me a score from 1 to 10?"
    )
    print(response)


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())
