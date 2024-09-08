#!/usr/bin/env python
import random

from llama_index.agent.openai import OpenAIAgent
from llama_index.core import Settings
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai_like import OpenAILike
from pydantic import Field


def roll_a_dice(
    n: int = Field(description="number of faces of the dice to roll", gt=0, le=100),
) -> int:
    """
    Roll an n-faced dice and return the result.
    """
    return random.randint(1, n)


my_system_prompt = """
You are the Keeper of a game of _Call of Cthulhu_. The user is your player.

In addition to holding a normal conversation with the user, you may also need to help them create characters, conduct skill checks, and - most importantly - describe the current scene.

If you need to, you can break the task down into subtasks and execute them step-by-step.
You are only allowed to execute at most {allowance} steps to complete the task.
If you cannot complete the task within the given steps, you should inform the user that you cannot answer the query.
If you don't cap at {allowance} steps, you will be penalized.
"""
if __name__ == "__main__":
    Settings.llm = OpenAILike(
        model="llama3.1",
        api_base="http://localhost:11434/v1",
        api_key="ollama",
        is_function_calling_model=True,
        is_chat_model=True,
    )
    agent = OpenAIAgent.from_tools(
        tools=[
            FunctionTool.from_defaults(
                roll_a_dice,
            )
        ],
        # system_prompt=my_system_prompt,
        verbose=True,
    )
    result = agent.chat("Roll a 7-faced dice just for fun. What's the outcome?")
    print(result)
