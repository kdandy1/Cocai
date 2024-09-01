import random

# How to use enums in Python: https://docs.python.org/3/howto/enum.html
from enum import IntEnum
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


def roll_a_dice(n: int = Field(description="骰子的面数", gt=0, le=100)) -> int:
    """
    掷一个骰子，返回 1 到 n 之间的一个整数。
    """
    return random.randint(1, n)


class RollResult(IntEnum):
    FUMBLE = 0  # 大失败
    FAIL = 1  # 失败
    SUCCESS = 2  # 成功
    HARD_SUCCESS = 3  # 困难成功
    EXTREME_SUCCESS = 4  # 极难成功
    CRITICAL_SUCCESS = 5  # 大成功


class Difficulty(IntEnum):
    """
    For tasks:
    > A regular task requires a roll of equal to or less than your skill value on 1D100 (a Regular success).
    > A difficult task requires a roll result equal to or less than half your skill value (a Hard success).
    > A task approaching the limits of human capability requires a roll equal to or less than one-fifth of your skill
    >   value (an Extreme success).

    ([source](https://cthulhuwiki.chaosium.com/rules/game-system.html#skill-rolls-and-difficulty-levels))


    For opposed rolls:
    - Regular: Opposing skill/characteristic is below 50.
    - Hard: Opposing skill/characteristic is equal to or above 50.
    - Extreme: Opposing skill/characteristic is equal to or above 90.

    ([source](https://trpgline.com/en/rules/coc7/summary))
    """

    REGULAR = 0
    DIFFICULT = 1
    EXTREME = 2


def __roll_a_skill(
    skill_value: int = Field(description="技能值", ge=0, le=100),
    difficulty: Difficulty = Field(description="难度等级", default=Difficulty.REGULAR),
) -> RollResult:
    """
    Roll a skill check and return the result.
    """
    result = roll_a_dice(n=100)
    if result == 100:
        return RollResult.FUMBLE
    if result == 1:
        return RollResult.CRITICAL_SUCCESS
    result_ignoring_difficulty = RollResult.FAIL
    if result <= skill_value // 5:
        result_ignoring_difficulty = RollResult.EXTREME_SUCCESS
    elif result <= skill_value // 2:
        result_ignoring_difficulty = RollResult.HARD_SUCCESS
    elif result <= skill_value:
        result_ignoring_difficulty = RollResult.SUCCESS
    # Now, we consider the difficulty.
    if difficulty == Difficulty.REGULAR:
        return result_ignoring_difficulty
    elif difficulty == Difficulty.DIFFICULT:
        if result_ignoring_difficulty >= RollResult.HARD_SUCCESS:
            return result_ignoring_difficulty
        # else, fall through to return a FAIL.
    elif difficulty == Difficulty.EXTREME:
        if result_ignoring_difficulty == RollResult.EXTREME_SUCCESS:
            return result_ignoring_difficulty
        # else, fall through to return a FAIL.
    return RollResult.FAIL


def roll_a_skill(
    skill_value: int = Field(description="技能值", ge=0, le=100),
    difficulty: Difficulty = Field(description="难度等级", default=Difficulty.REGULAR),
) -> str:
    """
    掷一个技能骰，返回结果。
    """
    roll_result = __roll_a_skill(skill_value, difficulty)
    return {
        RollResult.FUMBLE: "大失败",
        RollResult.FAIL: "失败",
        RollResult.SUCCESS: "成功",
        RollResult.HARD_SUCCESS: "困难成功",
        RollResult.EXTREME_SUCCESS: "极难成功",
        RollResult.CRITICAL_SUCCESS: "大成功",
    }[roll_result]
