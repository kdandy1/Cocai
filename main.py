#!/usr/bin/env python
import logging
import os
import sys

import chainlit as cl
import phoenix as px
from llama_index.agent.openai import OpenAIAgent
from llama_index.core import Settings
from llama_index.core.agent import AgentRunner
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.tools import FunctionTool
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.tools.tavily_research import TavilyToolSpec
from phoenix.trace.llama_index import OpenInferenceTraceCallbackHandler

# If Python’s builtin readline module is previously loaded, elaborate line editing and history features will be available.
# https://rich.readthedocs.io/en/stable/console.html#input
from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

from my_monkey_patch import ChainlitCallbackHandler
from tools import (
    ToolForConsultingTheModule,
    ToolForSuggestingChoices,
    illustrate_a_scene,
    roll_a_dice,
    roll_a_skill,
    tool_for_creating_character,
)
from utils import set_up_data_layer

console = Console()

SHOULD_USE_PHOENIX = True
# "Phoenix can display in real time the traces automatically collected from your LlamaIndex application."
# https://docs.llamaindex.ai/en/stable/module_guides/observability/observability.html
if SHOULD_USE_PHOENIX:
    px.launch_app()

SHOULD_USE_RICH = True

SHOULD_PERSIST_CHAT_STORE = False

# https://rich.readthedocs.io/en/latest/logging.html#handle-exceptions
logging.basicConfig(
    # This can get really verbose if set to `logging.DEBUG`.
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        (
            RichHandler(rich_tracebacks=True, console=console)
            if SHOULD_USE_RICH
            else logging.StreamHandler()
        )
    ],
    # This function does nothing if the root logger already has handlers configured,
    # unless the keyword argument force is set to True.
    # https://docs.python.org/3/library/logging.html#logging.basicConfig
    force=True,
)
logger = logging.getLogger(__name__)

if SHOULD_USE_RICH:
    # https://rich.readthedocs.io/en/stable/traceback.html#traceback-handler
    logger.debug("Installing rich traceback handler.")
    old_traceback_handler = install(show_locals=True, console=console)
    logger.debug(
        f"The global traceback handler has been swapped from {old_traceback_handler} to {sys.excepthook}."
    )

if SHOULD_PERSIST_CHAT_STORE:
    # https://docs.llamaindex.ai/en/stable/module_guides/storing/chat_stores/#simplechatstore
    try:
        chat_store = SimpleChatStore.from_persist_path(persist_path="chat_store.json")
    except Exception as e:
        logger.warning(f"Failed to load chat store from file: {e}, using a new one.")
        chat_store = SimpleChatStore()
else:
    chat_store = SimpleChatStore()

set_up_data_layer()


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(identifier="admin", metadata={"role": "admin"})
    else:
        return None


def create_callback_manager(should_use_chainlit: bool = True) -> CallbackManager:
    # Phoenix can display in real time the traces automatically collected from your LlamaIndex application.
    # The one-click way is as follows:
    # ```
    # llama_index.core.set_global_handler("arize_phoenix")
    # from llama_index.callbacks.arize_phoenix import (
    #     arize_phoenix_callback_handler,
    # )
    # ```
    # But I prefer to do it manually, so that I can put all callback handlers in one place.
    debug_logger = logging.getLogger("debug")
    debug_logger.setLevel(logging.DEBUG)
    callback_handlers = [
        LlamaDebugHandler(logger=debug_logger),
    ]
    if SHOULD_USE_PHOENIX:
        callback_handlers.append(OpenInferenceTraceCallbackHandler())
    if should_use_chainlit:
        callback_handlers.append(
            # TODO: When https://github.com/Chainlit/chainlit/pull/1285 is merged,
            #  change this back to `cl.LlamaIndexCallbackHandler()`.
            ChainlitCallbackHandler()
        )
    return CallbackManager(callback_handlers)


def create_agent(
    should_use_chainlit: bool,
    max_action_steps: int = 5,
) -> AgentRunner:
    # Needed for "Retrieved the following sources" to show up on Chainlit.
    Settings.callback_manager = create_callback_manager(should_use_chainlit)
    # ============= Beginning of the code block for wiring on to models. =============
    # At least when Chainlit is involved, LLM initializations must happen upon the `@cl.on_chat_start` event,
    # not in the global scope.
    # Otherwise, it messes up with Arize Phoenix: LLM calls won't be captured as parts of an Agent Step.
    if api_key := os.environ.get("OPENAI_API_KEY", None):
        logger.info("Using OpenAI API.")
        from llama_index.llms.openai import OpenAI

        Settings.llm = OpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            is_function_calling_model=True,
            is_chat_model=True,
        )
    else:
        logger.info("Using Ollama's OpenAI-compatible API.")
        from llama_index.llms.openai_like import OpenAILike

        Settings.llm = OpenAILike(
            model="llama3.1",
            api_base="http://localhost:11434/v1",
            api_key="ollama",
            is_function_calling_model=True,
            is_chat_model=True,
        )

    Settings.embed_model = OllamaEmbedding(
        # https://ollama.com/library/nomic-embed-text
        model_name="nomic-embed-text",
        # Uncomment the following line to use the LLM server running on my gaming PC.
        # base_url="http://10.147.20.237:11434",
    )
    # ============= End of the code block for wiring on to models. =============
    if api_key := os.environ.get("TAVILY_API_KEY", None):
        # Manage your API keys here: https://app.tavily.com/home
        logger.info(
            "Thanks for providing a Tavily API key. This AI agent will be able to use search the internet."
        )
        tavily_tool = TavilyToolSpec(
            api_key=api_key,
        ).to_tool_list()
    else:
        tavily_tool = []
    all_tools = tavily_tool + [
        FunctionTool.from_defaults(
            ToolForSuggestingChoices().suggest_choices,
        ),
        FunctionTool.from_defaults(
            ToolForConsultingTheModule().consult_the_game_module,
        ),
        FunctionTool.from_defaults(
            roll_a_dice,
        ),
        FunctionTool.from_defaults(
            roll_a_skill,
        ),
        FunctionTool.from_defaults(
            illustrate_a_scene,
        ),
        tool_for_creating_character,
    ]
    # Override the default system prompt for ReAct chats.
    with open("prompts/system_prompt.md") as f:
        MY_SYSTEM_PROMPT = f.read()
    my_system_prompt = MY_SYSTEM_PROMPT.replace(
        # TODO: Use `PromptTemplate.partial_format`. Today, it's not working.
        "{allowance}",
        str(max_action_steps),
    )
    agent = OpenAIAgent.from_tools(
        system_prompt=my_system_prompt,
        tools=all_tools,
        verbose=True,
        # x2: An observation step also takes as an iteration.
        # +1: The final output reasoning step needs to take a spot.
    )
    return agent


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Roll a 7-faced dice. Outcome?",
            message="Roll a 7-faced dice just for fun. What's the outcome?",
            icon="/public/avatars/roll_a_dice.png",
        ),
        cl.Starter(
            label="I'm stuck in a cave. What skills to use?",
            message="I'm stuck in a dark cave. What can I do?",
            icon="/public/avatars/suggest_choices.png",
        ),
        cl.Starter(
            label="Create a character for me.",
            message='Can you generate a character for me? Let\'s call him "Don Joe". Describe what kind of guy he is.',
            icon="/public/avatars/create_character.png",
        ),
        cl.Starter(
            label="What's the story background?",
            message="Briefly describe the story background of the module we are playing today.",
            icon="/public/avatars/consult_the_game_module.png",
        ),
    ]


@cl.on_chat_start
async def factory():
    cl.user_session.set("agent", create_agent(should_use_chainlit=True))


@cl.on_chat_end
async def cleanup():
    logger.warning("Interrupted. Persisting chat storage.")
    if SHOULD_PERSIST_CHAT_STORE:
        chat_store.persist(persist_path="chat_store.json")


@cl.on_message
async def main(message: cl.Message):
    """
    ChainLit provides a web GUI for this application.

    See https://docs.chainlit.io/integrations/llama-index.

    Usage:

    ```shell
    chainlit run main.py -w
    ```
    """
    agent: AgentRunner = cl.user_session.get("agent")
    app_user = cl.user_session.get("user").identifier or "guest"
    chat_memory = ChatMemoryBuffer.from_defaults(
        chat_store=chat_store,
        chat_store_key=app_user,
    )
    # The Chainlit doc recommends using `await cl.make_async(agent.chat)(message.content)` instead:
    # > The make_async function takes a synchronous function (for instance a LangChain agent) and returns an
    # > asynchronous function that will run the original function in a separate thread. This is useful to run
    # > long running synchronous tasks without blocking the event loop.
    # (https://docs.chainlit.io/api-reference/make-async#make-async)
    # I thought we can just use `agent.achat` directly, but it would cause `<ContextVar name='chainlit' at 0x...>`.
    # TODO: streaming seems broken. Why?
    response = await cl.make_async(agent.chat)(
        message.content, chat_history=chat_memory.get_all()
    )
    response_message = cl.Message(content="")
    response_message.content = response.response
    await response_message.send()


if __name__ == "__main__":
    # This block
    agent = create_agent(should_use_chainlit=False)
    try:
        agent.chat_repl()
    except KeyboardInterrupt:
        logger.warning("Interrupted. Persisting chat storage.")
        chat_store.persist(persist_path="chat_store.json")
