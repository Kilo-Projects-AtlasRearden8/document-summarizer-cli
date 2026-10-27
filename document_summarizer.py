"""document_summarizer: summarize documents with a local OpenAI-compatible LLM.

Reads a document (file or stdin), sends it to a chat-completions endpoint
(default Ollama at http://localhost:11434/v1), and writes a Markdown summary
to a file (or stdout). No API keys or cloud accounts required.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Optional

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.2"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 512
REQUEST_TIMEOUT_SECONDS = 120

SUMMARY_SYSTEM_PROMPT = (
    "You are a helpful, friendly writing assistant. Summarize the following "
    "document in clear, plain English. Use Markdown. Include a short title, "
    "a few bullet points of the key ideas, and a one-sentence takeaway. "
    "Never invent facts that are not in the document. Keep it concise and "
    "beginner-friendly."
)


def build_payload(
    document_text: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> dict:
    """Build the OpenAI-compatible chat-completions request body."""
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": document_text},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def call_chat_completions(
    base_url: str,
    model: str,
    document_text: str,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    api_key: Optional[str] = None,
) -> str:
    """Call an OpenAI-compatible chat-completions endpoint and return the text.

    This is a thin wrapper around urllib so the tool runs with no external
    dependencies. The function is a module-level name so tests can monkeypatch
    it with a mock endpoint.
    """
    url = base_url.rstrip("/") + "/chat/completions"
    payload = build_payload(document_text, model, temperature, max_tokens)
    body = json.dumps(payload).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:  # pragma: no cover - network path
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Endpoint returned HTTP {exc.code}: {detail}"
        ) from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network path
        raise RuntimeError(f"Could not reach endpoint {base_url}: {exc}") from exc

    try:
        data = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - malformed response
        raise RuntimeError(f"Endpoint returned invalid JSON: {exc}") from exc

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:  # pragma: no cover - unexpected shape
        raise RuntimeError(f"Unexpected endpoint response shape: {data!r}") from exc


def read_document(input_path: Optional[str]) -> str:
    """Read document text from a file path or standard input."""
    if input_path:
        with open(input_path, "r", encoding="utf-8") as handle:
            return handle.read()
    return sys.stdin.read()


def write_summary(output_path: Optional[str], summary: str) -> None:
    """Write the summary to a file path or standard output."""
    markdown = f"# Summary\n\n{summary}\n"
    if output_path:
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(markdown)
    else:
        sys.stdout.write(markdown)
        if not markdown.endswith("\n"):
            sys.stdout.write("\n")


def summarize(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    api_key: Optional[str] = None,
) -> str:
    """Read, summarize, and write a document. Returns the summary text."""
    document_text = read_document(input_path)
    if not document_text.strip():
        raise ValueError("Input document is empty. Nothing to summarize.")

    summary = call_chat_completions(
        base_url=base_url,
        model=model,
        document_text=document_text,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
    )

    write_summary(output_path, summary)
    return summary


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="document-summarizer",
        description=(
            "Summarize a document using a local OpenAI-compatible LLM "
            "(default Ollama). Saves Markdown output."
        ),
    )
    parser.add_argument(
        "--input",
        help="Document file to summarize (default: standard input)",
    )
    parser.add_argument(
        "--output",
        help="Markdown file to write (default: standard output)",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"OpenAI-compatible endpoint base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model name to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key, if your endpoint requires one (never logged or saved)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Sampling temperature, 0.0 to 1.0 (default: {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"Max tokens in the summary (default: {DEFAULT_MAX_TOKENS})",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        summarize(
            input_path=args.input,
            output_path=args.output,
            base_url=args.base_url,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            api_key=args.api_key,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
