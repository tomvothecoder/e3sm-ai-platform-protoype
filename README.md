# E3SM AI Platform Prototype

Minimal retrieval-augmented generation (RAG) prototype for exploring
[E3SM](https://e3sm.org/) documentation with
[LlamaIndex](https://developers.llamaindex.ai/python/framework/).

The prototype:

- indexes a small, curated E3SM, CIME, and SimBoard documentation corpus;
- generates embeddings locally with `BAAI/bge-small-en-v1.5`;
- uses the LivAI OpenAI-compatible API for GPT responses;
- persists the LlamaIndex vector index under `storage/e3sm`; and
- rebuilds the index when the corpus, manifest, or embedding model changes.

## Repository layout

```text
app/
  corpus.py                 Corpus validation, metadata, and index versioning
  starter.py                LlamaIndex RAG example
data/
  e3sm-corpus.json          SHA-pinned source manifest
  e3sm/                     Curated documentation snapshot
  min-viable-corpus.md      Initial corpus source list
scripts/
  sync_corpus.py            Downloads manifest-listed documents
tests/
  test_corpus.py            Corpus and synchronization tests
Makefile                    Common development commands
requirements.txt            Minimal Python dependencies
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- `make`
- access to LivAI and a valid API key
- network access during initial dependency and Hugging Face model downloads

## Setup

Clone the repository, then create the virtual environment and install
dependencies:

```bash
make install
```

Create a local environment file from the example:

```bash
cp .env.example .env
```

Set your LivAI API key in `.env`:

```dotenv
ASSISTANT_LIVAI_API_KEY=your-api-key
ASSISTANT_LIVAI_MODEL=gpt-5.5
ASSISTANT_LIVAI_BASE_URL=https://livai-api.llnl.gov/
```

The `.env` file and generated `storage/` directory are ignored by Git.

To open an interactive shell with the virtual environment activated:

```bash
make activate
```

Exit that shell to return to your original environment.

## Getting started

The curated corpus is committed under `data/e3sm`, so the starter can run
immediately after setup:

```bash
make run
```

On the first run, LlamaIndex downloads the Hugging Face embedding model, builds
the vector index, and persists it under `storage/e3sm`. Later runs restore that
index when its version matches the current manifest, corpus contents, and
embedding model.

The starter currently asks:

> How do I create, configure, and run an E3SM case with CIME, and where does
> SimBoard fit into that workflow?

Edit `main()` in `app/starter.py` to experiment with another question.

## Corpus management

`data/e3sm-corpus.json` is the authoritative document list. Every source URL is
pinned to a full Git commit SHA so the local corpus can be reproduced.

To download all manifest-listed documents:

```bash
make corpus-sync
```

Downloads complete and validate before any local corpus file is replaced. Files
not listed in the manifest are not indexed.

To add or update material:

1. Add or update its entry in `data/e3sm-corpus.json`.
2. Use a full 40-character commit SHA and matching raw GitHub URL.
3. Run `make corpus-sync`.
4. Run `make test`.

The next `make run` rebuilds the persisted index when document bytes change.

## Development commands

```bash
make help          # List available commands
make venv          # Create .venv with uv
make install       # Install requirements with uv
make activate      # Open an activated interactive shell
make corpus-sync   # Re-download the pinned corpus
make run           # Run the RAG starter
make test          # Run unit tests
make lint          # Run Ruff checks
make format        # Format Python files with Ruff
```

Equivalent installation commands without `make`:

```bash
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

## How it works

1. `app/starter.py` loads `.env` and configures the LivAI
   OpenAI-compatible LLM.
2. The manifest is validated and resolved into an explicit list of local
   corpus files.
3. LlamaIndex embeds those files locally with the Hugging Face model.
4. The index is created or restored from `storage/e3sm`.
5. A LlamaIndex `FunctionAgent` calls the document query engine and sends the
   retrieved context to LivAI for the final response.

## Resources

- [Understanding RAG](https://developers.llamaindex.ai/python/framework/understanding/rag/)
- [Starter example](https://developers.llamaindex.ai/python/framework/getting_started/starter_example/)

## Troubleshooting

- **`KeyError: 'ASSISTANT_LIVAI_MODEL'` or another missing variable:** Confirm
  `.env` exists at the repository root and contains all three
  `ASSISTANT_LIVAI_*` values.

- **Hugging Face model download fails:** Confirm the machine can reach Hugging
  Face during the first run. The model is reused from the local cache afterward.

- **Corpus files are missing or stale:** Run `make corpus-sync`, then
  `make run`.

- **Persisted index appears stale:** Remove `storage/e3sm` and run `make run`.
  The index is normally invalidated automatically when the manifest, corpus
  bytes, or embedding model changes.
