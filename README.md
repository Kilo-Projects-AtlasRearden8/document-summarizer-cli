# document-summarizer

A beginner-friendly command-line tool that summarizes documents using a local,
OpenAI-compatible LLM endpoint (default: Ollama). It saves its output as
Markdown. No API keys, no cloud accounts, no personal data.

Built by **Asdale Dynamics, LLC** — beginner-friendly AI education, books, and
practical tools you can publish or sell. Learn more at
[dylanasdale.github.io](https://dylanasdale.github.io).

## What it does

`document-summarizer` reads a text document (or standard input), sends it to a
local LLM through an OpenAI-compatible chat endpoint, and writes a concise
Markdown summary to a file (or standard output).

It is designed for local-first, privacy-friendly summarizing — perfect for
authors, small-business owners, healthcare workers (education only, never
medical advice), and anyone who wants to keep their documents on their own
machine.

## Requirements

- Python 3.8 or newer
- A running OpenAI-compatible endpoint. By default this is **Ollama**
  (`http://localhost:11434/v1`). You can point it at any compatible server with
  `--base-url`.

Ollama is free and runs locally. Install it from [ollama.com](https://ollama.com),
then pull a model, for example:

```bash
ollama pull llama3.2
```

No API key is needed for Ollama. If your endpoint requires one, pass it with
`--api-key` (it is never written to disk or logged).

## Install

From this folder:

```bash
pip install .
```

Or run directly without installing:

```bash
python document_summarizer.py --help
```

## Usage

Summarize a file and save Markdown output:

```bash
document-summarizer --input notes.txt --output summary.md
```

Summarize standard input and print to standard output:

```bash
cat notes.txt | document-summarizer
```

Change the endpoint, model, or temperature:

```bash
document-summarizer --input notes.txt --output summary.md \
  --base-url http://localhost:11434/v1 \
  --model llama3.2 \
  --temperature 0.3
```

Options:

| Option | Default | Meaning |
|--------|---------|---------|
| `--input` | (stdin) | Document file to summarize |
| `--output` | (stdout) | Markdown file to write |
| `--base-url` | http://localhost:11434/v1 | OpenAI-compatible endpoint base URL |
| `--model` | llama3.2 | Model name to use |
| `--api-key` | (none) | API key, if your endpoint requires one |
| `--temperature` | 0.3 | Creativity (0.0 = most deterministic) |
| `--max-tokens` | 512 | Max tokens in the summary |

## Example output (`summary.md`)

```markdown
# Summary of notes.txt

- The document covers three main topics: local AI, summarization, and privacy.
- Key takeaway: keep your documents on your own machine.
- Recommended next step: try Ollama with a small model.

_Summarized by document-summarizer (Asdale Dynamics, LLC)_
```

## Tests

Run the test suite (uses a mock endpoint — no network or LLM required):

```bash
pip install pytest
pytest
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

## About

Created by Dylan Asdale, registered nurse turned AI author and founder of
Asdale Dynamics, LLC (Indiana, formed October 2026). His book *The Massive AI
Manual* and hub site [dylanasdale.github.io](https://dylanasdale.github.io)
explain AI "like a friend would": plain English, step by step, never
condescending.

Credit: Asdale Dynamics, LLC.
