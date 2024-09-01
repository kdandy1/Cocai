import logging
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
        self, situation: str = Field(description="a brief description of the situation")
    ) -> str:
        """
        If the user wants to know what they can do in a particular situation (and what the possible consequences might be), you can use this tool.
        """
        prompt = self.__prompt.format(situation=situation)
        return Settings.llm.complete(prompt)


def roll_a_dice(
    n: int = Field(description="number of faces of the dice to roll", gt=0, le=100),
) -> int:
    """
    Roll a n-faced dice and return the result.
    """
    return random.randint(1, n)


class DegreesOfSuccess(IntEnum):
    FUMBLE = 0
    FAIL = 1
    SUCCESS = 2
    HARD_SUCCESS = 3
    EXTREME_SUCCESS = 4
    CRITICAL_SUCCESS = 5


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
    skill_value: int = Field(description="skill value", ge=0, le=100),
    difficulty: Difficulty = Field(
        description="difficulty level", default=Difficulty.REGULAR
    ),
) -> DegreesOfSuccess:
    """
    Roll a skill check and return the result.
    """
    result = roll_a_dice(n=100)
    logger = logging.getLogger("__roll_a_skill")
    logger.info(f"result: {result}")
    if result == 100:
        return DegreesOfSuccess.FUMBLE
    if result == 1:
        return DegreesOfSuccess.CRITICAL_SUCCESS
    result_ignoring_difficulty = DegreesOfSuccess.FAIL
    if result <= skill_value // 5:
        result_ignoring_difficulty = DegreesOfSuccess.EXTREME_SUCCESS
    elif result <= skill_value // 2:
        result_ignoring_difficulty = DegreesOfSuccess.HARD_SUCCESS
    elif result <= skill_value:
        result_ignoring_difficulty = DegreesOfSuccess.SUCCESS
    # Now, we consider the difficulty.
    if difficulty == Difficulty.REGULAR:
        return result_ignoring_difficulty
    elif difficulty == Difficulty.DIFFICULT:
        if result_ignoring_difficulty >= DegreesOfSuccess.HARD_SUCCESS:
            return result_ignoring_difficulty
        # else, fall through to return a FAIL.
    elif difficulty == Difficulty.EXTREME:
        if result_ignoring_difficulty == DegreesOfSuccess.EXTREME_SUCCESS:
            return result_ignoring_difficulty
        # else, fall through to return a FAIL.
    return DegreesOfSuccess.FAIL


def roll_a_skill(
    skill_value: int = Field(description="skill value", ge=0, le=100),
    difficulty: Difficulty = Field(
        description="difficulty level", default=Difficulty.REGULAR
    ),
) -> str:
    """
    Roll a skill check and check the result.
    """
    roll_result = __roll_a_skill(skill_value, difficulty)
    return {
        DegreesOfSuccess.FUMBLE: "fumble",
        DegreesOfSuccess.FAIL: "fail",
        DegreesOfSuccess.SUCCESS: "success",
        DegreesOfSuccess.HARD_SUCCESS: "hard success",
        DegreesOfSuccess.EXTREME_SUCCESS: "extreme success",
        DegreesOfSuccess.CRITICAL_SUCCESS: "critical success",
    }[roll_result]
