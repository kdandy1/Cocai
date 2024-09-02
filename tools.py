import logging
import random

# How to use enums in Python: https://docs.python.org/3/howto/enum.html
from enum import IntEnum
from pathlib import Path

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine
from pydantic import Field


class ToolForSuggestingChoices:
    def __init__(self, path_to_prompts_file: Path = Path("prompts/choices_prompt.md")):
        self.__prompt = path_to_prompts_file.read_text()

    def suggest_choices(
        self, situation: str = Field(description="a brief description of the situation")
    ) -> str:
        """
        If the user wants to know what they can do in a particular situation (and what the possible consequences might be), you can use this tool.
        """
        prompt = self.__prompt.format(situation=situation)
        return Settings.llm.complete(prompt)


class ToolForConsultingTheModule:
    query_engine: BaseQueryEngine = None

    def __init__(
        self,
        path_to_module_folder: Path = Path("game_modules/"),
    ):
        documents = SimpleDirectoryReader(
            input_dir=str(path_to_module_folder),
            # https://docs.llamaindex.ai/en/stable/module_guides/loading/simpledirectoryreader.html#reading-from-subdirectories
            recursive=True,
            # https://docs.llamaindex.ai/en/stable/module_guides/loading/simpledirectoryreader.html#restricting-the-files-loaded
            # Before including image files here, `mamba install pillow`.
            # Before including audio files here, `pip install openai-whisper`.
            required_exts=[".md", ".txt"],
        ).load_data()
        index = VectorStoreIndex.from_documents(
            # https://docs.llamaindex.ai/en/stable/api_reference/indices/vector_store.html#llama_index.indices.vector_store.base.VectorStoreIndex.from_documents
            documents=documents,
            show_progress=True,
        )
        self.query_engine = index.as_query_engine(
            similarity_top_k=5,
            # For a query engine hidden inside an Agent, streaming really doesn't make sense.
            # https://docs.llamaindex.ai/en/stable/module_guides/deploying/query_engine/streaming.html#streaming
            streaming=False,
        )

    def consult_the_game_module(
        self,
        query: str = Field(
            description="a brief description of what you want to consult about"
        ),
    ) -> str:
        """
        If you feel you need to consult the module ("playbook" / handbook) about:

        - how the story should progress,
        - some factual data, or
        - how the situation / a particular NPC is set up,

        you can use this tool.
        """
        return self.query_engine.query(query).response or ""


def roll_a_dice(
    n: int = Field(description="number of faces of the dice to roll", gt=0, le=100),
) -> int:
    """
    Roll an n-faced dice and return the result.
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
    degree_of_success = __map_dice_outcome_to_degree_of_success(
        difficulty, result, skill_value
    )
    return degree_of_success


def __map_dice_outcome_to_degree_of_success(difficulty, result, skill_value):
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
