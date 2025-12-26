import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DiscordServerConfig:
    name: str
    guild_id: str
    channel_ids: List[str]


@dataclass
class DiscordConfig:
    client_id: str
    client_secret: str
    public_key: str
    bot_token: str
    servers: List[DiscordServerConfig]


@dataclass
class LLMConfig:
    provider: str  # openai | gemini | ollama
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None


@dataclass
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    use_tls: bool
    from_email: str
    to_emails: List[str]


@dataclass
class ScheduleConfig:
    cron: str
    schedule_type: str


@dataclass
class AppConfig:
    discord: DiscordConfig
    llm: LLMConfig
    smtp: SMTPConfig
    input_dir: Path
    output_dir: Path
    schedule_cron: str
    lang: str
    timezone: str
    schedule_type: str


VALID_SCHEDULE_TYPES = {"daily", "weekly", "monthly", "custom"}


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


def load_env_file(path: Path) -> None:
    """
    Minimal .env loader to avoid extra deps. Existing env vars take precedence.
    """
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def _require(keys: List[str]) -> Tuple[List[str], dict]:
    missing = []
    values = {}
    for k in keys:
        v = os.environ.get(k, "").strip()
        if not v:
            missing.append(k)
        values[k] = v
    return missing, values


def _parse_servers(guild_ids_raw: str, channel_ids_raw: str, servers_raw: Optional[str]) -> List[DiscordServerConfig]:
    if servers_raw:
        try:
            payload = json.loads(servers_raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"DISCORD_SERVERS is not valid JSON: {exc}")

        if not isinstance(payload, list):
            raise ValueError("DISCORD_SERVERS must be a JSON array of server definitions")

        servers: List[DiscordServerConfig] = []
        for idx, server in enumerate(payload):
            if not isinstance(server, dict):
                raise ValueError(f"Server entry at index {idx} must be an object")
            name = server.get("name") or f"server-{idx}"
            guild_id = str(server.get("guild_id") or server.get("guild") or "").strip()
            if not guild_id:
                raise ValueError(f"Server entry '{name}' must include a guild_id")
            raw_channels = server.get("channel_ids") or server.get("channels")
            if isinstance(raw_channels, str):
                channels = [c.strip() for c in raw_channels.split(",") if c.strip()]
            elif isinstance(raw_channels, list):
                channels = [str(c).strip() for c in raw_channels if str(c).strip()]
            else:
                channels = []
            if not channels:
                # Allow implicit "all channels" when not provided
                channels = ["*"]
            servers.append(DiscordServerConfig(name=name, guild_id=guild_id, channel_ids=channels))
        return servers

    guild_ids = [g.strip() for g in guild_ids_raw.split(",") if g.strip()]
    channel_ids = [c.strip() for c in channel_ids_raw.split(",") if c.strip()]
    if not guild_ids:
        raise ValueError("At least one DISCORD_GUILD_IDS entry is required when DISCORD_SERVERS is not set")
    if not channel_ids:
        raise ValueError("At least one DISCORD_CHANNEL_IDS entry is required when DISCORD_SERVERS is not set")

    servers = []
    for gid in guild_ids:
        servers.append(
            DiscordServerConfig(
                name=f"guild-{gid}",
                guild_id=gid,
                channel_ids=channel_ids,
            )
        )
    return servers


def load_config() -> AppConfig:
    """
    Load and validate configuration from environment variables.
    Raises ValueError with details on missing keys by section.
    """
    missing_sections = {}

    # Discord
    discord_required = [
        "DISCORD_CLIENT_ID",
        "DISCORD_CLIENT_SECRET",
        "DISCORD_PUBLIC_KEY",
        "DISCORD_BOT_TOKEN",
    ]
    miss, discord_vals = _require(discord_required)
    if miss:
        missing_sections["discord"] = miss

    guild_ids = os.environ.get("DISCORD_GUILD_IDS", "")
    channel_ids = os.environ.get("DISCORD_CHANNEL_IDS", "")
    servers_raw = os.environ.get("DISCORD_SERVERS")

    # LLM
    llm_required = ["LLM_PROVIDER", "LLM_MODEL"]
    miss, llm_vals = _require(llm_required)
    if miss:
        missing_sections["llm"] = miss

    # SMTP
    smtp_required = [
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "FROM_EMAIL",
        "TO_EMAILS",
    ]
    miss, smtp_vals = _require(smtp_required)
    if miss:
        missing_sections["smtp"] = miss

    # Paths / schedule / locale
    paths_required = ["INPUT_DIR", "OUTPUT_DIR", "SCHEDULE_CRON", "LANG", "TIMEZONE"]
    miss, paths_vals = _require(paths_required)
    if miss:
        missing_sections["general"] = miss

    schedule_type = os.environ.get("SCHEDULE_TYPE", "daily").strip().lower()
    if schedule_type not in VALID_SCHEDULE_TYPES:
        allowed = ", ".join(sorted(VALID_SCHEDULE_TYPES))
        raise ValueError(f"SCHEDULE_TYPE must be one of {allowed}; got '{schedule_type}'")

    if missing_sections:
        raise ValueError(f"Missing config keys: {missing_sections}")

    lang = paths_vals["LANG"].strip().lower()
    allowed_langs = {"en", "ko"}
    if lang not in allowed_langs:
        raise ValueError(f"LANG must be one of {', '.join(sorted(allowed_langs))}; got '{lang}'")

    input_dir = Path(paths_vals["INPUT_DIR"])
    if not input_dir.exists():
        raise ValueError(f"INPUT_DIR does not exist: {input_dir}")
    output_dir = Path(paths_vals["OUTPUT_DIR"])
    output_dir.mkdir(parents=True, exist_ok=True)

    discord_cfg = DiscordConfig(
        client_id=discord_vals["DISCORD_CLIENT_ID"],
        client_secret=discord_vals["DISCORD_CLIENT_SECRET"],
        public_key=discord_vals["DISCORD_PUBLIC_KEY"],
        bot_token=discord_vals["DISCORD_BOT_TOKEN"],
        servers=_parse_servers(guild_ids, channel_ids, servers_raw),
    )

    smtp_cfg = SMTPConfig(
        host=smtp_vals["SMTP_HOST"],
        port=int(smtp_vals["SMTP_PORT"]),
        username=smtp_vals["SMTP_USERNAME"],
        password=smtp_vals["SMTP_PASSWORD"],
        use_tls=_parse_bool(os.environ.get("SMTP_USE_TLS", "true")),
        from_email=smtp_vals["FROM_EMAIL"],
        to_emails=[e.strip() for e in smtp_vals["TO_EMAILS"].split(",") if e.strip()],
    )

    provider_name = llm_vals["LLM_PROVIDER"].lower()
    api_key = os.environ.get("LLM_API_KEY") or None
    # Fallback: provider-specific envs
    if not api_key:
        if provider_name in {"openai", "chatgpt"}:
            api_key = os.environ.get("OPEN_AI_API_KEY") or api_key
        elif provider_name in {"google", "gemini"}:
            api_key = os.environ.get("GOOGLE_AI_API_KEY") or api_key

    llm_cfg = LLMConfig(
        provider=provider_name,
        model=llm_vals["LLM_MODEL"],
        api_key=api_key,
        base_url=os.environ.get("LLM_BASE_URL") or None,
    )

    app_cfg = AppConfig(
        discord=discord_cfg,
        llm=llm_cfg,
        smtp=smtp_cfg,
        input_dir=input_dir,
        output_dir=output_dir,
        schedule_cron=paths_vals["SCHEDULE_CRON"],
        lang=lang,
        timezone=paths_vals["TIMEZONE"],
        schedule_type=schedule_type,
    )
    return app_cfg
