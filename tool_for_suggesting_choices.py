from pydantic import Field


from llama_index.core import Settings
from llama_index.core.tools import FunctionTool


with open("prompts/choices_prompt.md") as f:
    CHOICES_PROMPT = f.read()


def suggest_choices(situation: str = Field(description="当前场景的描述")) -> str:
    """
    如果用户想知道在这个情景下可以做些什么（以及可能会有怎样的后果），可以用这个工具查询。
    """
    prompt = CHOICES_PROMPT.format(situation=situation)
    return Settings.llm.complete(prompt)


tool = FunctionTool.from_defaults(
    suggest_choices,
)
