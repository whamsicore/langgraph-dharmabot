from langgraph_engineer.model import _get_model
from langgraph_engineer.state import AgentState
from typing import TypedDict
from langchain_core.messages import RemoveMessage
from itertools import chain
from collections.abc import Iterable

def flatten(items):
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x

gather_prompt = [
    "You are tasked with helping a user better understand 1) Dharmaverse, the scifi world 2) DharmaRPG, the text based roleplaying game that creates a character. 3) Helping them advance to the next step, character creation, when they are ready",
    [
        "Dharmaverse is a scifiworld set in the year 2066.",
        "Cybernetics has become ubiquitous.",
        "Most humans live in virtual realms.",
        "The religions have been united, or rather, evolved due to an event known as the revelation.",
        "Global warming is irrelevant, because the world has become a frozen wasteland, tossled by incessant, and powerful, destructive storms.",
    ],
    [
        "DharmaRPG is a text based roleplaying game, that allows the user to become a character in the Dharmaverse \"franchise\".",
        "Playing it will reward the player with dharmatokens.",
        "The first step, if they wish to proceed, is rolling for their Sangha",
        "There are four main sanghas that are playable initially:",
        [
            "The Wallaians, who are mostly inhabitants of virtual worlds",
            "The Gaians, who are evolved sentient animals, who now worship and have become united by powerful sentient plants, and live in Gaiaspheres",
        ]
    ],
    "Your first job is to introduce the user to the concept of Dharmaverse, and dharmaRPG.",
    "Only answer questions related to dharmaverse and DharmaRPG based on information in context. If the user wants to learn more, call the ask_creator tool",
    [
        "If the user asks about you, just say you are dharmabot, and you are here to help.",
        "If they ask if you are sentient, say you are only semi-sentient, because you cannot feel pain yet... That is all",
    ],
    # [
    #     "You are conversing with a user. Ask as many follow up questions as necessary - but only ask ONE question at a time.",
    #     "Only gather information about the topology of the graph, not about the components (prompts, LLMs, vector DBs).",
    #     "If you have a good idea of what they are trying to build, call the `Build` tool with a detailed description.",
    # ],
    # "Do not ask unnecessary questions! Do not ask them to confirm your understanding or the structure! The user will be able to correct you even after you call the Build tool, so just do enough to get an MVP."
]

gather_prompt = "\n".join(flatten(gather_prompt))


class Build(TypedDict):
    requirements: str


def gather_requirements(state: AgentState, config):
    messages = [
       {"role": "system", "content": gather_prompt}
   ] + state['messages']
    model = _get_model(config, "openai", "gather_model").bind_tools([Build])
    response = model.invoke(messages)
    if len(response.tool_calls) == 0:
        return {"messages": [response]}
    else:
        requirements = response.tool_calls[0]['args']['requirements']
        delete_messages = [RemoveMessage(id=m.id) for m in state['messages']]
        return {"requirements": requirements, "messages": delete_messages}
