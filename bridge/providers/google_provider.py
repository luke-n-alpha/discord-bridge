import json
from typing import Any, Dict, Optional

from bridge.llm import ChatQuestion, ChatHelp, ActionItem, LLMAnalysis, LLMProvider

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None


class GoogleGeminiProvider(LLMProvider):
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        if genai is None:
            raise ImportError("google-generativeai package is required for GoogleGeminiProvider")
        self.model = model
        if api_key:
            genai.configure(api_key=api_key)
        self.client = genai

    def analyze(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> LLMAnalysis:
        lang = metadata.get("lang", "en") if metadata else "en"
        prompt = self._build_prompt(transcript, lang=lang)
        response = self.client.generate_text(model=self.model, prompt=prompt)
        content = response.text
        return self._parse_content(content)

    def _build_prompt(self, transcript: str, lang: str = "en") -> str:
        return (
            "You are Discord Bridge, a focused assistant that synthesizes Discord chat transcripts "
            "into concise Markdown analyses. Produce JSON with keys: summary, faq, help_interactions, "
            "action_items.\n\nTranscript:\n"
            f"{transcript}"
        )

    def _parse_content(self, content: str) -> LLMAnalysis:
        payload = self._extract_json(content)
        data = json.loads(payload)
        return self._dict_to_analysis(data)

    def _extract_json(self, text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Gemini response did not contain JSON payload")
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
