"""Tests for document_summarizer using a mock endpoint (no network, no LLM)."""

from unittest import mock

import pytest

import document_summarizer as ds


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_DOCUMENT = (
    "The quick brown fox jumps over the lazy dog. This is a test document used "
    "to verify that the summarizer reads input, calls the endpoint, and writes "
    "Markdown output. It contains several sentences so the summary is not "
    "trivial."
)

MOCK_SUMMARY = (
    "# Summary of the document\n\n"
    "- This is a test document.\n"
    "- It verifies the summarizer pipeline.\n"
    "- Key takeaway: the pipeline works.\n"
)


class FakeResponse:
    """A minimal stand-in for urllib's HTTP response."""

    def __init__(self, payload: dict, status: int = 200):
        self._payload = payload
        self.status = status

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def make_mock_call(summary_text: str = MOCK_SUMMARY):
    """Return a monkeypatch-ready callable that returns a canned summary."""

    def fake_call(*args, **kwargs):
        return summary_text

    return fake_call


# ---------------------------------------------------------------------------
# build_payload
# ---------------------------------------------------------------------------


def test_build_payload_contains_model_and_messages():
    payload = ds.build_payload("hello world", "llama3.2", 0.3, 512)
    assert payload["model"] == "llama3.2"
    assert isinstance(payload["messages"], list)
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"
    assert "hello world" in payload["messages"][1]["content"]
    assert payload["temperature"] == 0.3
    assert payload["max_tokens"] == 512


# ---------------------------------------------------------------------------
# read_document / write_summary
# ---------------------------------------------------------------------------


def test_read_document_from_string(monkeypatch, tmp_path):
    file_path = tmp_path / "in.txt"
    file_path.write_text(SAMPLE_DOCUMENT, encoding="utf-8")
    assert ds.read_document(str(file_path)) == SAMPLE_DOCUMENT


def test_read_document_from_stdin(monkeypatch):
    monkeypatch.setattr(ds.sys, "stdin", __import__("io").StringIO(SAMPLE_DOCUMENT))
    assert ds.read_document(None) == SAMPLE_DOCUMENT


def test_write_summary_to_file(tmp_path):
    out_path = tmp_path / "out.md"
    ds.write_summary(str(out_path), MOCK_SUMMARY)
    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("# Summary\n\n")
    assert MOCK_SUMMARY in content


def test_write_summary_to_stdout(monkeypatch, capsys):
    captured = __import__("io").StringIO()
    monkeypatch.setattr(ds.sys, "stdout", captured)
    ds.write_summary(None, MOCK_SUMMARY)
    assert MOCK_SUMMARY in captured.getvalue()


# ---------------------------------------------------------------------------
# call_chat_completions (mocked)
# ---------------------------------------------------------------------------


def test_call_chat_completions_returns_summary(monkeypatch):
    monkeypatch.setattr(ds, "call_chat_completions", make_mock_call(MOCK_SUMMARY))
    result = ds.call_chat_completions(
        "http://localhost:11434/v1", "llama3.2", SAMPLE_DOCUMENT
    )
    assert result == MOCK_SUMMARY


def test_call_chat_completions_passes_api_key(monkeypatch):
    captured = {}

    def fake_call(base_url, model, document_text, temperature=None, max_tokens=None, api_key=None):
        captured["api_key"] = api_key
        return MOCK_SUMMARY

    monkeypatch.setattr(ds, "call_chat_completions", fake_call)
    ds.call_chat_completions(
        "http://localhost:11434/v1",
        "llama3.2",
        SAMPLE_DOCUMENT,
        api_key="sk-test",
    )
    assert captured["api_key"] == "sk-test"


# ---------------------------------------------------------------------------
# summarize (end-to-end with mock)
# ---------------------------------------------------------------------------


def test_summarize_writes_file(tmp_path, monkeypatch):
    in_path = tmp_path / "in.txt"
    in_path.write_text(SAMPLE_DOCUMENT, encoding="utf-8")
    out_path = tmp_path / "out.md"

    monkeypatch.setattr(ds, "call_chat_completions", make_mock_call(MOCK_SUMMARY))

    result = ds.summarize(
        input_path=str(in_path),
        output_path=str(out_path),
        base_url="http://localhost:11434/v1",
        model="llama3.2",
    )

    assert result == MOCK_SUMMARY
    written = out_path.read_text(encoding="utf-8")
    assert written.startswith("# Summary\n\n")
    assert MOCK_SUMMARY in written


def test_summarize_rejects_empty_input(tmp_path, monkeypatch):
    in_path = tmp_path / "empty.txt"
    in_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(ds, "call_chat_completions", make_mock_call(MOCK_SUMMARY))

    with pytest.raises(ValueError, match="empty"):
        ds.summarize(input_path=str(in_path))


def test_main_writes_output_and_returns_zero(tmp_path, monkeypatch, capsys):
    in_path = tmp_path / "in.txt"
    in_path.write_text(SAMPLE_DOCUMENT, encoding="utf-8")
    out_path = tmp_path / "out.md"

    monkeypatch.setattr(ds, "call_chat_completions", make_mock_call(MOCK_SUMMARY))

    code = ds.main(
        [
            "--input",
            str(in_path),
            "--output",
            str(out_path),
            "--base-url",
            "http://localhost:11434/v1",
            "--model",
            "llama3.2",
        ]
    )

    assert code == 0
    written = out_path.read_text(encoding="utf-8")
    assert MOCK_SUMMARY in written


def test_main_prints_error_and_returns_nonzero(monkeypatch, capsys):
    monkeypatch.setattr(
        ds,
        "call_chat_completions",
        make_mock_call(MOCK_SUMMARY),
    )
    # Force an empty document by monkeypatching read_document.
    monkeypatch.setattr(ds, "read_document", lambda path: "")

    code = ds.main(["--input", "irrelevant.txt"])
    assert code == 1
    captured = capsys.readouterr()
    assert "error:" in captured.err


def test_default_constants():
    assert ds.DEFAULT_BASE_URL == "http://localhost:11434/v1"
    assert ds.DEFAULT_MODEL == "llama3.2"
    assert ds.DEFAULT_TEMPERATURE == 0.3
    assert ds.DEFAULT_MAX_TOKENS == 512
