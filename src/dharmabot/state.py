"""
This file defines different classes and type hints related to the configuration and state of the DharmaBot UI. The `AgentState` class extends `MessagesState` and includes attributes like `requirements`, `code`, `accepted`, `is_admin`, and `context`, which likely represent the state of an agent in the UI. The `OutputState` class specifies the structure of output messages, and `GraphConfig` defines the configuration options related to different models used within the UI.
"""

from langgraph.graph import MessagesState
from typing import TypedDict, Literal
class AgentState(MessagesState):
    requirements: str
    code: str
    accepted: bool
    is_admin: bool
    context: dict
class OutputState(TypedDict):
    code: str


class GraphConfig(TypedDict):
    gather_model: Literal['openai', 'anthropic']
    draft_model: Literal['openai', 'anthropic']
    critique_model: Literal['openai', 'anthropic']
