from pathlib import Path

from llama_index.core import Settings
from llama_index.core.llms.utils import LLMType
from pydantic import Field


class ToolForSuggestingChoices:
    llm: LLMType = None

    def __init__(
        self, llm, path_to_prompts_file: Path = Path("prompts/choices_prompt.md")
    ):
        self.__prompt = path_to_prompts_file.read_text()
        self.llm = llm

    def suggest_choices(
        self, situation: str = Field(description="当前场景的描述")
    ) -> str:
        """
        如果用户想知道在这个情景下可以做些什么（以及可能会有怎样的后果），可以用这个工具查询。
        """
        prompt = self.__prompt.format(situation=situation)
        return Settings.llm.complete(prompt)
