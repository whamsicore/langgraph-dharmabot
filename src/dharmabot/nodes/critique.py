"""
This Python file seems to be a part of the DharmaBot UI system. It includes functions related to critiquing a developer's work on building a LangGraph application. The `critique` function loads a unit test file from a GitHub URL, prompts for a critique based on the content, swaps message roles between AI and user, and then invokes a model to provide feedback on the developer's work.
"""

from dharmabot.loader import load_github_file
from dharmabot.model import _get_model
from dharmabot.state import AgentState
from langchain_core.messages import AIMessage
from langchain_core.pydantic_v1 import BaseModel

critique_prompt = """You are tasked with critiquing a junior developers first attempt at building a LangGraph application. \
Here is a long unit test file for LangGraph. This should contain a lot (but possibly not all) \
relevant information on how to use LangGraph.

<unit_test_file>
{file}
</unit_test_file>

Based on the conversation below, attempt to critique the developer. If it seems like the written solution is fine, then call the `Accept` tool.

Do NOT critique the internal logic of the nodes too much - just make sure the flow (the nodes and edges) are correct and make sense. \
It's totally fine to use dummy LLMs or dummy retrieval steps."""


class Accept(BaseModel):
    logic: str
    accept: bool


def _swap_messages(messages):
    """ purpose
    Swaps the roles of messages between AI and user.
    
    This function takes a list of messages and swaps the roles:
    - AI messages become user messages
    - Non-AI messages (assumed to be user messages) become assistant messages
    
    This is useful for reframing the conversation history in a different perspective,
    which can be helpful in certain critique or analysis scenarios.

    Args:
        messages (list): A list of message objects.

    Returns:
        list: A new list of messages with swapped roles.
    """
    new_messages = []
    for m in messages:
        if isinstance(m, AIMessage):
            new_messages.append({"role": "user", "content": m.content})
        else:
            new_messages.append({"role": "assistant", "content": m.content})
    return new_messages


def critique(state: AgentState, config):
    github_url = "https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/tests/test_pregel.py"
    file_contents = load_github_file(github_url)
    messages = [
                   {"role": "user", "content": critique_prompt.format(file=file_contents)},
                   {"role": "assistant", "content": state.get('requirements')},

               ] + _swap_messages(state['messages'])
    model = _get_model(config, "openai", "critique_model").with_structured_output(Accept)
    response = model.invoke(messages)
    accepted = response.accept
    if accepted:
        return {
            "messages": [
                {"role": "user", "content": response.logic},
                {"role": "assistant", "content": "okay, sending to user"}],
            "accepted": True
        }
    else:
        return {
            "messages": [
                {"role": "user", "content": response.logic},
            ],
            "accepted": False
        }
