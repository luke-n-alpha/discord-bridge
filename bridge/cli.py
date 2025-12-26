import argparse
import json
import logging
from pathlib import Path
from typing import Iterable, List

from bridge.config import load_config, load_env_file
from bridge.emailer import send_email
from bridge.pipeline import run_pipeline
from bridge.providers import create_provider

logger = logging.getLogger(__name__)


def collect_inputs(path: Path) -> Iterable[Path]:
    if path.is_dir():
        for file in sorted(path.glob("*.json")):
            yield file
    else:
        yield path


def build_subject(files: List[Path], cfg_name: str | None = None) -> str:
    base = "Discord Bridge Report"
    if cfg_name:
        base = f"{base} ({cfg_name})"
    if files:
        dates = {p.stem for p in files}
        base = f"{base} - {', '.join(sorted(dates))}"
    return base


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Discord Bridge summary + email workflow")
    parser.add_argument("-i", "--input", required=True, type=Path, help="Input JSON file or folder")
    parser.add_argument("--config", type=Path, default=Path(".env"), help="Path to .env file")
    parser.add_argument("--no-email", action="store_true", help="Do not send email, only generate Markdown")
    parser.add_argument("--dry-run", action="store_true", help="Run without email or file writing")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    load_env_file(args.config)
    cfg = load_config()

    provider = create_provider(cfg.llm)

    processed: List[Path] = []
    attachments = []

    for input_path in collect_inputs(args.input):
        if not input_path.exists():
            logger.warning("Skipping missing input %s", input_path)
            continue
        with input_path.open("r", encoding="utf-8") as f:
            chat_data = json.load(f)
        out_path = cfg.output_dir / f"{chat_data.get('channel', {}).get('name','channel')}_{chat_data.get('date','')}.md"
        markdown = run_pipeline(
            chat_data,
            provider,
            None if args.dry_run else out_path,
            metadata={"lang": cfg.lang},
        )
        processed.append(out_path)
        attachments.append((out_path.name, markdown.encode("utf-8"), "text/markdown"))
        logger.info("Processed %s -> %s", input_path, out_path)

    if args.dry_run or args.no_email:
        return

    if not attachments:
        logger.warning("No attachments generated; skipping email.")
        return

    subject = build_subject(processed)
    body = f"Discord Bridge processed {len(processed)} file(s). See attachments for details."
    send_email(cfg.smtp, subject, body, attachments=attachments)
    logger.info("Report email sent to %s", ", ".join(cfg.smtp.to_emails))


if __name__ == "__main__":
    main()
