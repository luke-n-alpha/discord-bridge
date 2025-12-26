from types import SimpleNamespace

import pytest

from bridge.llm import ChatQuestion, ChatHelp
from bridge.providers import create_provider
from bridge.providers.ollama_provider import OllamaProvider
from bridge.providers.openai_provider import OpenAIProvider
from bridge.providers.google_provider import GoogleGeminiProvider


def fake_openai_module():
    fake = SimpleNamespace()
    fake.api_key = None
    fake.api_base = None

    class ChatCompletion:
        @staticmethod
        def create(**kwargs):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content='{"summary":"OK","faq":[{"question":"q","asker":"a"}],"help_interactions":[],"action_items":[]}'
                        )
                    )
                ]
            )

    fake.ChatCompletion = ChatCompletion
    return fake


def test_openai_provider_parses(monkeypatch):
    fake = fake_openai_module()
    monkeypatch.setattr("bridge.providers.openai_provider.openai", fake, raising=False)
    provider = OpenAIProvider(model="gpt-4o-mini")
    analysis = provider.analyze("transcript")
    assert analysis.summary == "OK"
    assert analysis.faq[0].question == "q"


def fake_genai_module():
    fake = SimpleNamespace()

    def configure(api_key):
        fake.api_key = api_key

    fake.configure = configure

    class Response:
        def __init__(self):
            self.text = '{"summary":"GO","faq":[],"help_interactions":[],"action_items":[]}'

    class Gen:
        def generate_text(self, model, prompt):
            return Response()

    fake.generate_text = Gen().generate_text
    return fake


def test_google_provider_parses(monkeypatch):
    fake = fake_genai_module()
    monkeypatch.setattr("bridge.providers.google_provider.genai", fake, raising=False)
    provider = GoogleGeminiProvider(model="gemini-pro")
    analysis = provider.analyze("transcript")
    assert analysis.summary == "GO"
    assert analysis.faq == []


def test_create_provider_openai(monkeypatch):
    cfg = SimpleNamespace(provider="openai", model="gpt-4o-mini", api_key="key", base_url=None)
    fake = fake_openai_module()
    monkeypatch.setattr("bridge.providers.openai_provider.openai", fake, raising=False)
    provider = create_provider(cfg)  # type: ignore[arg-type]
    assert isinstance(provider, OpenAIProvider)


def test_create_provider_google(monkeypatch):
    cfg = SimpleNamespace(provider="google", model="gemini-pro", api_key="key", base_url=None)
    fake = fake_genai_module()
    monkeypatch.setattr("bridge.providers.google_provider.genai", fake, raising=False)
    provider = create_provider(cfg)  # type: ignore[arg-type]
    assert isinstance(provider, GoogleGeminiProvider)


def fake_requests_module():
    class Response:
        def __init__(self):
            self._json = {
                "choices": [
                    {"message": {"content": '{"summary":"OK","faq":[],"help_interactions":[],"action_items":[]}'}}]
            }

        def json(self):
            return self._json

        def raise_for_status(self):
            return

    class Requests:
        @staticmethod
        def post(*args, **kwargs):
            return Response()

    return Requests()


def test_create_provider_ollama(monkeypatch):
    cfg = SimpleNamespace(provider="ollama", model="gpt-oss:20b", api_key=None, base_url="http://127.0.0.1:11434")
    fake = fake_requests_module()
    monkeypatch.setattr("bridge.providers.ollama_provider.requests", fake, raising=False)
    provider = create_provider(cfg)  # type: ignore[arg-type]
    assert isinstance(provider, OllamaProvider)


def test_ollama_fallback_to_chat(monkeypatch):
    calls = []

    class Generate404Response:
        status_code = 404

        def json(self):
            return {}

        def raise_for_status(self):
            from bridge.providers.ollama_provider import HTTPError

            raise HTTPError(response=self)

    class ChatResponse:
        def json(self):
            return {"choices": [{"message": {"content": '{"summary":"OK","faq":[],"help_interactions":[],"action_items":[]}'}}]}

        def raise_for_status(self):
            return

    def post(url, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            return Generate404Response()
        return ChatResponse()

    class FakeRequests:
        ConnectionError = Exception

        @staticmethod
        def post(url, **kwargs):
            return post(url, **kwargs)

    monkeypatch.setattr("bridge.providers.ollama_provider.requests", FakeRequests(), raising=False)
    provider = OllamaProvider(model="gpt-oss:20b", base_url="http://dummy")
    analysis = provider.analyze("hi")

    assert calls[0].endswith("/api/generate")
    assert calls[1].endswith("/api/chat")
    assert analysis.summary == "OK"
