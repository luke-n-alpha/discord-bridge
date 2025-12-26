from typing import Dict

from bridge.config import LLMConfig
from bridge.llm import LLMProvider
from bridge.providers.google_provider import GoogleGeminiProvider
from bridge.providers.ollama_provider import OllamaProvider
from bridge.providers.openai_provider import OpenAIProvider

_PROVIDERS: Dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "chatgpt": OpenAIProvider,
    "google": GoogleGeminiProvider,
    "gemini": GoogleGeminiProvider,
    "ollama": OllamaProvider,
}


def create_provider(cfg: LLMConfig) -> LLMProvider:
    provider_cls = _PROVIDERS.get(cfg.provider.lower())
    if not provider_cls:
        raise ValueError(f"Unsupported provider '{cfg.provider}'")
    return provider_cls(model=cfg.model, api_key=cfg.api_key, base_url=cfg.base_url)
