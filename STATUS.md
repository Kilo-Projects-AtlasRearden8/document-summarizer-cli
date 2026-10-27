# STATUS.md — document-summarizer CLI

## What was built

A beginner-friendly, local-first Python CLI that summarizes documents using a
configurable OpenAI-compatible endpoint (default Ollama) and saves Markdown
output. No API keys, no cloud accounts, no personal data, no secrets.

Files in this folder:

- `document_summarizer.py` — the CLI and summarization logic
- `pyproject.toml` — packaging; exposes the `document-summarizer` entry point
- `README.md` — usage docs, credits Asdale Dynamics, LLC
- `LICENSE` — MIT License, copyright line exactly
  `Copyright (c) 2026 Asdale Dynamics, LLC`
- `tests/test_summarizer.py` — 12 tests, all using a mock endpoint
- `tests/__init__.py` — test package marker
- `.gitignore` — standard Python ignore rules

## How to run

Install (creates the `document-summarizer` command):

```bash
pip install .
```

Or run directly:

```bash
python3 document_summarizer.py --help
```

Summarize a file to Markdown:

```bash
document-summarizer --input notes.txt --output summary.md
```

Summarize stdin to stdout:

```bash
cat notes.txt | document-summarizer
```

Point at a different OpenAI-compatible endpoint:

```bash
document-summarizer --input notes.txt --output summary.md \
  --base-url http://localhost:11434/v1 \
  --model llama3.2 \
  --temperature 0.3
```

Default endpoint: `http://localhost:11434/v1` (Ollama). Default model:
`llama3.2`. No API key needed for Ollama; pass `--api-key` only if your
endpoint requires one.

## Verification results

- `python3 -m pytest` — **12 passed** (mock endpoint, no network/LLM needed)
- `python3 document_summarizer.py --help` — runs, prints usage
- `pip install .` into a fresh venv — builds and installs successfully
- `document-summarizer --help` (installed entry point) — works
- LICENSE copyright line verified exactly:
  `Copyright (c) 2026 Asdale Dynamics, LLC`
- README credits Asdale Dynamics, LLC
- No `.github/workflows` files added
- No secrets, API keys, or personal data in any file
- Git initialized and committed as `Dylan Asdale`
  (`dylanasdale@users.noreply.github.com`); plain commit message, no
  co-author trailers; not pushed, no remote created

## Known gaps

- Requires a running OpenAI-compatible endpoint (Ollama default) to actually
  generate summaries; tests use a mock so no LLM is needed to verify.
- Ollama must be installed separately and a model pulled (e.g.
  `ollama pull llama3.2`) before live use.
- Only one summary format (Markdown) is supported; no JSON/plain-text output
  option yet.
- Temperature/clamping is not validated at the CLI (passed through to the
  endpoint).
- No retry/backoff for transient endpoint failures.
- Tested with Python 3.13; pyproject declares `>=3.8` but not verified on
  older Pythons.

Credit: Asdale Dynamics, LLC.
