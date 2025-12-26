from pathlib import Path
from typing import Dict, Any, List, Optional
import dateutil.parser

from bridge.llm import LLMProvider, LLMAnalysis


def format_messages(messages: List[Dict[str, Any]], users: Dict[str, Any]) -> str:
    """Turn message list into readable transcript."""
    lines = []
    for msg in messages:
        user = users.get(msg.get("uid"), {})
        username = user.get("nickname") or user.get("name") or "Unknown User"
        ts_raw = msg.get("ts")
        try:
            ts = dateutil.parser.parse(ts_raw).strftime("%H:%M")
        except Exception:
            ts = ts_raw or ""
        content = msg.get("content", "")
        lines.append(f"{username} ({ts}): {content}")
    return "\n".join(lines)


def analysis_to_markdown(analysis: LLMAnalysis, channel_name: str, date_label: str) -> str:
    parts = [
        f"# {channel_name} {date_label}",
        "## Summary",
        analysis.summary,
        "## FAQ",
        "\n".join(f"- {q.question} (asked by {q.asker})" for q in analysis.faq) or "- None",
        "## Who Helped Who",
        "\n".join(
            f"- {h.helper} helped {h.recipient} with {h.task} by providing {h.assistance}"
            for h in analysis.help_interactions
        ) or "- None",
        "## Action Items",
    ]
    if analysis.action_items:
        for ai in analysis.action_items:
            parts.append(f"- [{ai.type}] {ai.description} (by {ai.mentioned_by})")
    else:
        parts.append("- None")
    return "\n".join(parts) + "\n"


def run_pipeline(
    chat_data: Dict[str, Any],
    provider: LLMProvider,
    output_path: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Core orchestration: format transcript -> LLM analyze -> markdown -> optional save.
    """
    transcript = format_messages(chat_data.get("messages", []), chat_data.get("users", {}))
    base_metadata = {"channel": chat_data.get("channel"), "date": chat_data.get("date")}
    if metadata:
        base_metadata.update(metadata)
    analysis = provider.analyze(transcript, metadata=base_metadata)
    markdown = analysis_to_markdown(analysis, chat_data.get("channel", {}).get("name", "Unknown"), chat_data.get("date", ""))

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    return markdown
