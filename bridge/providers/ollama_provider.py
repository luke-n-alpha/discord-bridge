import json
import logging
from typing import Any, Dict, Optional

from bridge.llm import ActionItem, ChatHelp, ChatQuestion, LLMAnalysis, LLMProvider

try:
    import requests
    from requests import HTTPError
except ImportError:  # pragma: no cover
    requests = None
    HTTPError = Exception  # type: ignore

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.2,
    ):
        if requests is None:
            raise ImportError("requests package is required for OllamaProvider")
        self.model = model
        self.base_url = base_url or "http://127.0.0.1:11434"
        self.temperature = temperature
        self.api_key = api_key

    def _build_prompt(self, transcript: str, lang: str = "en") -> str:
        return f"""
You are Discord Bridge, a focused assistant that synthesizes Discord chat transcripts into concise Markdown analyses in {lang.title()}.
Return JSON with keys: summary, faq, help_interactions, action_items.
Prioritize technical discussions, highlight decisions, and skip fluff.
Respond with JSON only (no code fences or extra commentary).

Transcript:
{transcript}
"""

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            return {}
        return {"Authorization": f"Bearer {self.api_key}"}

    def _post_chat(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You produce structured summaries from Discord transcripts"},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "stream": False,
            "options": {"num_predict": 512},
        }
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            headers=self._headers(),
            timeout=120,
        )
        response.raise_for_status()
        content = response.json()
        message = (
            content.get("message", {})
            or content.get("choices", [{}])[0].get("message", {})
        ).get("content", "")
        if not message:
            raise ValueError("Ollama chat response did not include message content")
        return message

    def _post_generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False,
            "options": {"num_predict": 512},
        }
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            headers=self._headers(),
            timeout=120,
        )
        response.raise_for_status()
        content = response.json()
        message = content.get("response", "")
        if not message:
            raise ValueError("Ollama generate response did not include response text")
        return message

    def analyze(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> LLMAnalysis:
        lang = metadata.get("lang", "en") if metadata else "en"
        prompt = self._build_prompt(transcript, lang=lang)

        try:
            message = self._post_generate(prompt)
        except HTTPError as exc:
            status = getattr(exc.response, "status_code", None)
            logger.info("Ollama /api/generate failed with status %s; falling back to /api/chat", status)
            message = self._post_chat(prompt)
        except requests.ConnectionError:
            logger.error("Failed to reach Ollama at %s", self.base_url)
            raise
        return self._parse_content(message)

    def _parse_content(self, content: str) -> LLMAnalysis:
        try:
            data = json.loads(self._extract_json(content))
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Failed to parse Ollama response as JSON: %s", exc)
            return LLMAnalysis(summary=content.strip(), faq=[], help_interactions=[], action_items=[])
        return self._dict_to_analysis(data)

    def _extract_json(self, text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Ollama response did not contain JSON payload")
        return text[start : end + 1]

    def _dict_to_analysis(self, data: Dict[str, Any]) -> LLMAnalysis:
        return LLMAnalysis(
            summary=data.get("summary", "").strip(),
            faq=[
                ChatQuestion(
                    question=item.get("question", "") if isinstance(item, dict) else str(item),
                    asker=item.get("asker", "") if isinstance(item, dict) else "",
                )
                for item in data.get("faq", [])
            ],
            help_interactions=[
                ChatHelp(
                    helper=item.get("helper", "") if isinstance(item, dict) else "",
                    recipient=item.get("recipient", "") if isinstance(item, dict) else "",
                    task=item.get("task", "") if isinstance(item, dict) else str(item),
                    assistance=item.get("assistance", "") if isinstance(item, dict) else "",
                )
                for item in data.get("help_interactions", [])
            ],
            action_items=[
                ActionItem(
                    description=item.get("description", "") if isinstance(item, dict) else str(item),
                    mentioned_by=item.get("mentioned_by", "") if isinstance(item, dict) else "",
                    type=item.get("type", "Technical Tasks") if isinstance(item, dict) else "Technical Tasks",
                )
                for item in data.get("action_items", [])
            ],
        )
