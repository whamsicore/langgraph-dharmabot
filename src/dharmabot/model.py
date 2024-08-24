"""
This file contains a function that is responsible for getting a specific chat model based on the configuration provided. It checks the model type specified in the configuration and returns an instance of either ChatOpenAI or ChatAnthropic with predefined parameters. This function is crucial for dynamically selecting and initializing the appropriate chat model based on the user's choice within the DharmaBot UI.
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


def _get_model(config, default, key):
    model = config['configurable'].get(key, default)
    if model == "openai":
        return ChatOpenAI(temperature=0, model_name="gpt-4o-2024-08-06")
    elif model == "anthropic":
        return ChatAnthropic(temperature=0, model_name="claude-3-5-sonnet-20240620")
    else:
        raise ValueError
