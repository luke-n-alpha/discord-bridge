import json
import sys
from pathlib import Path

from bridge.llm import LLMAnalysis, ChatQuestion, ChatHelp, ActionItem


class RecordingProvider:
    def __init__(self):
        self.called = False

    def analyze(self, transcript, metadata=None):
        self.called = True
        return LLMAnalysis(
            summary="cli summary",
            faq=[ChatQuestion(question="q", asker="a")],
            help_interactions=[],
            action_items=[ActionItem(description="task", mentioned_by="u", type="Technical Tasks")],
        )


def test_cli_dry_run(tmp_path, monkeypatch):
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()
    monkeypatch.delenv("LANG", raising=False)  # allow .env LANG to be applied
    env = tmp_path / ".env"
    env.write_text(
        f"""\
DISCORD_CLIENT_ID=1
DISCORD_CLIENT_SECRET=2
DISCORD_PUBLIC_KEY=3
DISCORD_BOT_TOKEN=4
DISCORD_GUILD_IDS=1
DISCORD_CHANNEL_IDS=10
DISCORD_SERVERS=[{{"name":"cli","guild_id":"1","channel_ids":["10"]}}]
INPUT_DIR={in_dir}
OUTPUT_DIR={out_dir}
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user
SMTP_PASSWORD=pass
FROM_EMAIL=user@example.com
TO_EMAILS=a@example.com
SCHEDULE_CRON=0 9 * * *
LANG=ko
TIMEZONE=Asia/Seoul
SMTP_USE_TLS=true
""",
        encoding="utf-8",
    )

    chat = {
        "channel": {"name": "general"},
        "date": "2024-11-13",
        "users": {"u1": {"name": "A"}},
        "messages": [{"uid": "u1", "ts": "2024-11-13T00:00:00Z", "content": "hi"}],
    }
    inp = tmp_path / "chat.json"
    inp.write_text(json.dumps(chat), encoding="utf-8")

    import importlib
    import bridge.cli as cli_module
    cli_module = importlib.reload(cli_module)

    provider = RecordingProvider()
    monkeypatch.setattr(cli_module, "create_provider", lambda cfg: provider)
    monkeypatch.setattr(cli_module, "send_email", lambda *args, **kwargs: None)

    monkeypatch.setattr("sys.argv", ["bridge.cli", "-i", str(inp), "--config", str(env), "--dry-run"])
    cli_module.main()

    assert provider.called
