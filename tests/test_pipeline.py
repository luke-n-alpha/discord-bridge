from pathlib import Path
from typing import Any, Dict, Optional

from bridge import pipeline
from bridge.llm import LLMAnalysis, ChatQuestion, ChatHelp, ActionItem, LLMProvider


class FakeProvider(LLMProvider):
    def __init__(self):
        self.last_transcript = None
        self.last_metadata = None

    def analyze(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> LLMAnalysis:
        self.last_transcript = transcript
        self.last_metadata = metadata
        return LLMAnalysis(
            summary="Summary text",
            faq=[ChatQuestion(question="Q1?", asker="Alice")],
            help_interactions=[
                ChatHelp(
                    helper="Bob",
                    recipient="Charlie",
                    task="Setup",
                    assistance="Shared steps",
                )
            ],
            action_items=[
                ActionItem(description="Do thing", mentioned_by="Dana", type="Technical Tasks")
            ],
        )


def sample_chat():
    return {
        "channel": {"name": "general"},
        "date": "2024-11-13",
        "users": {
            "u1": {"name": "Alice"},
            "u2": {"name": "Bob"},
        },
        "messages": [
            {"uid": "u1", "ts": "2024-11-13T00:00:00Z", "content": "Hello"},
            {"uid": "u2", "ts": "2024-11-13T00:05:00Z", "content": "Reply"},
        ],
    }


def test_pipeline_formats_and_writes(tmp_path):
    provider = FakeProvider()
    chat = sample_chat()
    out = tmp_path / "out.md"

    markdown = pipeline.run_pipeline(chat, provider, output_path=out)

    assert "Summary text" in markdown
    assert "- Q1? (asked by Alice)" in markdown
    assert "- Bob helped Charlie with Setup by providing Shared steps" in markdown
    assert "- [Technical Tasks] Do thing (by Dana)" in markdown
    assert out.exists()
    saved = out.read_text(encoding="utf-8")
    assert "general 2024-11-13" in saved
    assert provider.last_metadata["channel"]["name"] == "general"


def test_pipeline_forward_lang_metadata(tmp_path):
    provider = FakeProvider()
    chat = sample_chat()
    pipeline.run_pipeline(chat, provider, metadata={"lang": "ko"})
    assert provider.last_metadata["lang"] == "ko"
