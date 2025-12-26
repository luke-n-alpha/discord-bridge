import json
from typing import Any, Dict, Optional

from bridge.llm import ChatQuestion, ChatHelp, ActionItem, LLMAnalysis, LLMProvider

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        if openai is None:
            raise ImportError("openai package is required for OpenAIProvider")
        if api_key:
            openai.api_key = api_key
        if base_url:
            openai.api_base = base_url
        self.model = model
        self.client = openai

    def _build_prompt(self, transcript: str, lang: str = "en") -> str:
        return f"""
You are Discord Bridge, a focused assistant that synthesizes Discord chat transcripts into concise Markdown analyses.
Produce JSON with keys: summary (string), faq (array of {{question, asker}}), help_interactions (array of {{helper, recipient, task, assistance}}), action_items (array of {{description, mentioned_by, type}}).
Prioritize technical discussions, highlight decisions, and skip fluff.

Provide responses in {lang.title()}.

Transcript:
{transcript}
"""

    def analyze(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> LLMAnalysis:
        lang = metadata.get("lang", "en") if metadata else "en"
        prompt = self._build_prompt(transcript, lang=lang)
        response = self.client.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You turn Discord transcripts into structured summaries."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        return self._parse_content(content)

    def _parse_content(self, content: str) -> LLMAnalysis:
        json_payload = self._extract_json(content)
        data = json.loads(json_payload)
        return self._dict_to_analysis(data)

    def _extract_json(self, text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("OpenAI response did not contain JSON payload")
        return text[start : end + 1]

    def _dict_to_analysis(self, data: Dict[str, Any]) -> LLMAnalysis:
        return LLMAnalysis(
            summary=data.get("summary", "").strip(),
            faq=[
                ChatQuestion(question=item.get("question", ""), asker=item.get("asker", ""))
                for item in data.get("faq", [])
            ],
            help_interactions=[
                ChatHelp(
                    helper=item.get("helper", ""),
                    recipient=item.get("recipient", ""),
                    task=item.get("task", ""),
                    assistance=item.get("assistance", ""),
                )
                for item in data.get("help_interactions", [])
            ],
            action_items=[
                ActionItem(
                    description=item.get("description", ""),
                    mentioned_by=item.get("mentioned_by", ""),
                    type=item.get("type", "Technical Tasks"),
                )
                for item in data.get("action_items", [])
            ],
        )
