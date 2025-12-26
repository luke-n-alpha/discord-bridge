import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bridge.config import load_config, load_env_file


def write_env(tmp_path: Path, content: str) -> Path:
    env_path = tmp_path / ".env"
    env_path.write_text(content, encoding="utf-8")
    return env_path


def test_load_env_and_config_success(tmp_path, monkeypatch):
    (tmp_path / "in").mkdir()
    (tmp_path / "out").mkdir()
    env_content = f"""\
DISCORD_CLIENT_ID=123
DISCORD_CLIENT_SECRET=secret
DISCORD_PUBLIC_KEY=pub
DISCORD_BOT_TOKEN=bot
DISCORD_GUILD_IDS=1,2
DISCORD_CHANNEL_IDS=10
INPUT_DIR={tmp_path / "in"}
OUTPUT_DIR={tmp_path / "out"}
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=pass
SMTP_USE_TLS=true
FROM_EMAIL=user@example.com
TO_EMAILS=a@example.com,b@example.com
SCHEDULE_CRON=0 9 * * *
LANG=ko
TIMEZONE=Asia/Seoul
"""
    env_path = write_env(tmp_path, env_content)
    # Clear env for test isolation
    for k in list(os.environ):
        if k.startswith("DISCORD_") or k.startswith("LLM_") or k.startswith("SMTP_") or k in {
            "INPUT_DIR",
            "OUTPUT_DIR",
            "SCHEDULE_CRON",
            "LANG",
            "TIMEZONE",
            "TO_EMAILS",
            "SCHEDULE_TYPE",
        }:
            monkeypatch.delenv(k, raising=False)

    load_env_file(env_path)
    cfg = load_config()

    assert cfg.discord.client_id == "123"
    assert len(cfg.discord.servers) == 2
    assert cfg.discord.servers[0].guild_id == "1"
    assert cfg.discord.servers[1].guild_id == "2"
    assert cfg.discord.servers[0].channel_ids == ["10"]
    assert cfg.llm.provider == "openai"
    assert cfg.smtp.host == "smtp.office365.com"
    assert cfg.smtp.port == 587
    assert cfg.smtp.use_tls is True
    assert cfg.smtp.to_emails == ["a@example.com", "b@example.com"]
    assert cfg.input_dir == tmp_path / "in"
    assert cfg.output_dir == tmp_path / "out"
    assert cfg.schedule_cron == "0 9 * * *"
    assert cfg.schedule_type == "daily"


def test_missing_keys_raises(tmp_path, monkeypatch):
    env_content = """\
DISCORD_CLIENT_ID=123
"""
    env_path = write_env(tmp_path, env_content)
    # Clear env for test isolation
    for k in list(os.environ):
        if k.startswith("DISCORD_") or k.startswith("LLM_") or k.startswith("SMTP_") or k in {
            "INPUT_DIR",
            "OUTPUT_DIR",
            "SCHEDULE_CRON",
            "LANG",
            "TIMEZONE",
            "TO_EMAILS",
            "SCHEDULE_TYPE",
        }:
            monkeypatch.delenv(k, raising=False)

    load_env_file(env_path)
    with pytest.raises(ValueError) as excinfo:
        load_config()
    msg = str(excinfo.value)
    assert "discord" in msg
    assert "llm" in msg
    assert "smtp" in msg
    assert "general" in msg


def test_servers_json_parsing(tmp_path, monkeypatch):
    (tmp_path / "in").mkdir()
    (tmp_path / "out").mkdir()
    env_content = f"""\
DISCORD_CLIENT_ID=123
DISCORD_CLIENT_SECRET=secret
DISCORD_PUBLIC_KEY=pub
DISCORD_BOT_TOKEN=bot
INPUT_DIR={tmp_path / "in"}
OUTPUT_DIR={tmp_path / "out"}
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=pass
SMTP_USE_TLS=true
FROM_EMAIL=user@example.com
TO_EMAILS=a@example.com
SCHEDULE_CRON=0 9 * * *
LANG=ko
TIMEZONE=Asia/Seoul
DISCORD_SERVERS=[{{"name":"cline","guild_id":"100","channel_ids":["10","11"]}},{{"name":"airi","guild_id":"200","channel_ids":["20"]}}]
"""
    env_path = write_env(tmp_path, env_content)
    for k in list(os.environ):
        if k.startswith("DISCORD_") or k.startswith("LLM_") or k.startswith("SMTP_") or k in {
            "INPUT_DIR",
            "OUTPUT_DIR",
            "SCHEDULE_CRON",
            "LANG",
            "TIMEZONE",
            "TO_EMAILS",
            "SCHEDULE_TYPE",
        }:
            monkeypatch.delenv(k, raising=False)

    load_env_file(env_path)
    cfg = load_config()
    assert len(cfg.discord.servers) == 2
    assert cfg.discord.servers[0].name == "cline"
    assert cfg.discord.servers[0].channel_ids == ["10", "11"]
    assert cfg.discord.servers[1].guild_id == "200"


def test_servers_missing_channel_ids_defaults_all(tmp_path, monkeypatch):
    (tmp_path / "in").mkdir()
    (tmp_path / "out").mkdir()
    env_content = f"""\
DISCORD_CLIENT_ID=123
DISCORD_CLIENT_SECRET=secret
DISCORD_PUBLIC_KEY=pub
DISCORD_BOT_TOKEN=bot
INPUT_DIR={tmp_path / "in"}
OUTPUT_DIR={tmp_path / "out"}
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=pass
SMTP_USE_TLS=true
FROM_EMAIL=user@example.com
TO_EMAILS=a@example.com
SCHEDULE_CRON=0 9 * * *
LANG=ko
TIMEZONE=Asia/Seoul
DISCORD_SERVERS=[{{"name":"all","guild_id":"1"}}]
"""
    env_path = write_env(tmp_path, env_content)
    for k in list(os.environ):
        if k.startswith("DISCORD_") or k.startswith("LLM_") or k.startswith("SMTP_") or k in {
            "INPUT_DIR",
            "OUTPUT_DIR",
            "SCHEDULE_CRON",
            "LANG",
            "TIMEZONE",
            "TO_EMAILS",
            "SCHEDULE_TYPE",
        }:
            monkeypatch.delenv(k, raising=False)

    load_env_file(env_path)
    cfg = load_config()
    assert cfg.discord.servers[0].channel_ids == ["*"]


def test_schedule_type_env(tmp_path, monkeypatch):
    (tmp_path / "in").mkdir()
    (tmp_path / "out").mkdir()
    env_content = f"""\
DISCORD_CLIENT_ID=123
DISCORD_CLIENT_SECRET=secret
DISCORD_PUBLIC_KEY=pub
DISCORD_BOT_TOKEN=bot
DISCORD_SERVERS=[{{"name":"a","guild_id":"1","channel_ids":["10"]}}]
INPUT_DIR={tmp_path / "in"}
OUTPUT_DIR={tmp_path / "out"}
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=pass
SMTP_USE_TLS=true
FROM_EMAIL=user@example.com
TO_EMAILS=a@example.com
SCHEDULE_CRON=0 9 * * *
LANG=ko
TIMEZONE=Asia/Seoul
SCHEDULE_TYPE=Weekly
"""
    env_path = write_env(tmp_path, env_content)
    for k in list(os.environ):
        if k.startswith("DISCORD_") or k.startswith("LLM_") or k.startswith("SMTP_") or k in {
            "INPUT_DIR",
            "OUTPUT_DIR",
            "SCHEDULE_CRON",
            "LANG",
            "TIMEZONE",
            "TO_EMAILS",
            "SCHEDULE_TYPE",
        }:
            monkeypatch.delenv(k, raising=False)

    load_env_file(env_path)
    cfg = load_config()
    assert cfg.schedule_type == "weekly"


def test_schedule_type_invalid(tmp_path, monkeypatch):
    (tmp_path / "in").mkdir()
    (tmp_path / "out").mkdir()
    env_content = f"""\
DISCORD_CLIENT_ID=123
DISCORD_CLIENT_SECRET=secret
DISCORD_PUBLIC_KEY=pub
DISCORD_BOT_TOKEN=bot
DISCORD_SERVERS=[{{"name":"a","guild_id":"1","channel_ids":["10"]}}]
INPUT_DIR={tmp_path / "in"}
OUTPUT_DIR={tmp_path / "out"}
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=pass
SMTP_USE_TLS=true
FROM_EMAIL=user@example.com
TO_EMAILS=a@example.com
SCHEDULE_CRON=0 9 * * *
LANG=ko
TIMEZONE=Asia/Seoul
SCHEDULE_TYPE=fortnightly
"""
    env_path = write_env(tmp_path, env_content)
    for k in list(os.environ):
        if k.startswith("DISCORD_") or k.startswith("LLM_") or k.startswith("SMTP_") or k in {
            "INPUT_DIR",
            "OUTPUT_DIR",
            "SCHEDULE_CRON",
            "LANG",
            "TIMEZONE",
            "TO_EMAILS",
            "SCHEDULE_TYPE",
        }:
            monkeypatch.delenv(k, raising=False)

    load_env_file(env_path)
    with pytest.raises(ValueError) as excinfo:
        load_config()
    msg = str(excinfo.value)
    assert "SCHEDULE_TYPE" in msg
    assert "custom, daily, monthly, weekly" in msg


def test_llm_api_key_fallbacks(tmp_path, monkeypatch):
    (tmp_path / "in").mkdir()
    (tmp_path / "out").mkdir()
    env_content = f"""\
DISCORD_CLIENT_ID=1
DISCORD_CLIENT_SECRET=2
DISCORD_PUBLIC_KEY=3
DISCORD_BOT_TOKEN=4
DISCORD_SERVERS=[{{"name":"a","guild_id":"1"}}]
INPUT_DIR={tmp_path / "in"}
OUTPUT_DIR={tmp_path / "out"}
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPEN_AI_API_KEY=sk-test
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user
SMTP_PASSWORD=pass
SMTP_USE_TLS=true
FROM_EMAIL=user@example.com
TO_EMAILS=a@example.com
SCHEDULE_CRON=0 9 * * *
LANG=ko
TIMEZONE=Asia/Seoul
"""
    env_path = write_env(tmp_path, env_content)
    for k in list(os.environ):
        if k.startswith("DISCORD_") or k.startswith("LLM_") or k.startswith("SMTP_") or k in {
            "INPUT_DIR",
            "OUTPUT_DIR",
            "SCHEDULE_CRON",
            "LANG",
            "TIMEZONE",
            "TO_EMAILS",
            "SCHEDULE_TYPE",
            "OPEN_AI_API_KEY",
        }:
            monkeypatch.delenv(k, raising=False)

    load_env_file(env_path)
    cfg = load_config()
    assert cfg.llm.api_key == "sk-test"


def test_invalid_lang_raises(tmp_path, monkeypatch):
    (tmp_path / "in").mkdir()
    env_content = f"""\
DISCORD_CLIENT_ID=1
DISCORD_CLIENT_SECRET=2
DISCORD_PUBLIC_KEY=3
DISCORD_BOT_TOKEN=4
DISCORD_SERVERS=[{{"name":"a","guild_id":"1"}}]
INPUT_DIR={tmp_path / "in"}
OUTPUT_DIR={tmp_path / "missing-out"}
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user
SMTP_PASSWORD=pass
SMTP_USE_TLS=true
FROM_EMAIL=user@example.com
TO_EMAILS=a@example.com
SCHEDULE_CRON=0 9 * * *
LANG=fr
TIMEZONE=Asia/Seoul
"""
    env_path = write_env(tmp_path, env_content)
    for k in list(os.environ):
        if k.startswith("DISCORD_") or k.startswith("LLM_") or k.startswith("SMTP_") or k in {
            "INPUT_DIR",
            "OUTPUT_DIR",
            "SCHEDULE_CRON",
            "LANG",
            "TIMEZONE",
            "TO_EMAILS",
            "SCHEDULE_TYPE",
        }:
            monkeypatch.delenv(k, raising=False)

    load_env_file(env_path)
    with pytest.raises(ValueError) as excinfo:
        load_config()
    assert "LANG must be one of" in str(excinfo.value)


def test_missing_input_dir_raises(tmp_path, monkeypatch):
    env_content = f"""\
DISCORD_CLIENT_ID=1
DISCORD_CLIENT_SECRET=2
DISCORD_PUBLIC_KEY=3
DISCORD_BOT_TOKEN=4
DISCORD_SERVERS=[{{"name":"a","guild_id":"1"}}]
INPUT_DIR={tmp_path / "in-missing"}
OUTPUT_DIR={tmp_path / "out"}
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=user
SMTP_PASSWORD=pass
SMTP_USE_TLS=true
FROM_EMAIL=user@example.com
TO_EMAILS=a@example.com
SCHEDULE_CRON=0 9 * * *
LANG=en
TIMEZONE=Asia/Seoul
"""
    env_path = write_env(tmp_path, env_content)
    for k in list(os.environ):
        if k.startswith("DISCORD_") or k.startswith("LLM_") or k.startswith("SMTP_") or k in {
            "INPUT_DIR",
            "OUTPUT_DIR",
            "SCHEDULE_CRON",
            "LANG",
            "TIMEZONE",
            "TO_EMAILS",
            "SCHEDULE_TYPE",
        }:
            monkeypatch.delenv(k, raising=False)

    load_env_file(env_path)
    with pytest.raises(ValueError) as excinfo:
        load_config()
    assert "INPUT_DIR does not exist" in str(excinfo.value)
