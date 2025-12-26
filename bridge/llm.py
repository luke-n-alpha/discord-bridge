from dataclasses import dataclass
from typing import List, Protocol, Optional, Dict, Any


@dataclass
class ChatQuestion:
    question: str
    asker: str


@dataclass
class ChatHelp:
    helper: str
    recipient: str
    task: str
    assistance: str


@dataclass
class ActionItem:
    description: str
    mentioned_by: str
    type: str  # Technical Tasks | Documentation Needs | Feature Requests


@dataclass
class LLMAnalysis:
    summary: str
    faq: List[ChatQuestion]
    help_interactions: List[ChatHelp]
    action_items: List[ActionItem]


class LLMProvider(Protocol):
    def analyze(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> LLMAnalysis:
        ...
