# ![](public/logo_light.png) CoCai

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A chatbot that plays Call of Cthulhu (CoC) with you, powered by AI.

<img width="2317" alt="image" src="https://github.com/user-attachments/assets/4617c031-72f3-4915-8582-fd8700b0f725">

_(Logo by [@Norod78](https://linktr.ee/Norod78), originally [published on Civitai](https://civitai.com/images/1231343))_

## Demo

Check out this transcript:

<img width="786" alt="image" src="https://github.com/user-attachments/assets/e039276c-d495-4596-b547-acfc66ce6a84">

In the first message, I asked Cocai to generate a character for me:

> Can you generate a character for me? Let's call him "Don Joe". Describe what kind of guy he is, then tabulate his stats.

Under the hood, Cocai used [Cochar](https://www.cochar.pl/). In the first couple of attempts, Cocai forgot to provide some required parameters. Cocai fixed that problem and successfully generated a character profile from Cochar.

Then, I asked Cocai what I -- playing the character of Mr. Don Joe -- can do, being stuck in a dark cave. It suggested a couple of options and described the potential outcomes associated with each choice.

I then asked Cocai to roll a skill check for me, Spot Hidden. Based on the chat history, Cocai was able to recall that Mr. Joe had a Spot Hidden skill of 85%. It rolled the dice, got a successful outcome, and took some inspiration from its 2nd response to progress the story.

Thanks to the chain-of-thought (CoT) visualization feature, you can unfold the tool-using steps and verify yourself that Cocai was indeed able to recall the precise value of Joe's Spot Hidden skill:

<img width="771" alt="image" src="https://github.com/user-attachments/assets/8ae52b80-b3c0-4978-9649-64039a5c113e">


## Usage

### Pre-requisites

Bring your own large language model (LLM).
- The easiest (and perhaps highest-quality) way would be to provide an API key to OpenAI. Simply add `OPENAI_API_KEY=sk-...` to a `.env` file in the project root.
- With the absence of an OpenAI API key, the chatbot will default to using [Ollama](https://ollama.com/download), a program that serves LLMs locally.
  - Ensure that your local Ollama server has already downloaded the `llama3.1` model. If you haven't (or aren't sure), run `ollama pull llama3.1`.
  - If you want to use a different model that does not support function-calling, that's also possible. Revert [this commit][tc], so that you can use the ReAct paradigm to simulate function-calling capabilities with a purely semantic approach.

[tc]: https://github.com/StarsRail/Cocai/commit/13d777767d1dd96024021c085247525ec52b79ba

Install [`just`](https://github.com/casey/just), a command runner. I use this because I always tend to forget the exact command to run.

Written in Python, this project uses the Rust-based package manager [`uv`](https://docs.astral.sh/uv/). It does not require you to explicitly create a virtual environment.

**Prepare a CoC module**. Unsure which to pick? Start with [_“Clean Up, Aisle Four!”_][a4] by [Dr. Michael C. LaBossiere][mc].
You'll need it in Markdown format, though. If you can only find the PDF edition, you can:
1. upload it to Google Drive,
2. open it with Google Docs,
3. download it as Markdown, and finally
4. do some cleanings.

[a4]: https://shadowsofmaine.wordpress.com/wp-content/uploads/2008/03/cleanup.pdf
[mc]: https://lovecraft.fandom.com/wiki/Michael_LaBossiere

### Running the Chatbot

You can start the chatbot by running:

```shell
just serve
```

# Let's write an AI Keeper for _Call of Cthulhu_! Part II: Building the Tools

Here comes the fun part. We need to build the tools that the AI Keeper can use.

## The search engine integration

Let's start with the easiest one, which is **the search engine integration**. As mentioned earlier, we can use [Tavily](https://tavily.com/) for this purpose. LlamaIndex has a well-maintained integration package with Tavily. It's [available](https://llamahub.ai/l/tools/llama-index-tools-tavily-research) in its repository of agentic tools, not-so-creatively named [LlamaHub][lh]. (I'm curious about who started it, calling everything "something-hub". Was it [GitHub](https://github.com/)? [Hugging Face Hub](https://huggingface.co/docs/hub/en/index)? [JupyterHub](https://jupyter.org/hub)?) All we need to do is to install the package and use it in our code like this:

```python
from llama_index.tools.tavily_research import TavilyToolSpec

if api_key := os.environ.get("TAVILY_API_KEY", None):
    tavily_tool = TavilyToolSpec(
        api_key=api_key,
    ).to_tool_list()
else:
    tavily_tool = []

# then...
    cl.user_session.set("agent",
      OpenAIAgent.from_tools( # ...
        tools=tavily_tool + [...],
    ))
```

**Secret management.** In the snippet above, we are reading the API key from the environment variable `TAVILY_API_KEY`. "Does it mean I have to supply that env var every time I run the script, or do I have to add it into my `.profile` script?", you may ask. No, you don't have to! Here's a lesser-known side effect of using Chainlit: It automatically reads the environment variables from a `.env` file in the project root, thanks to [its usage][iu] of the [`python-dotenv`][pde] package. The more you know.

[lh]: https://llamahub.ai/
[iu]: https://github.com/Chainlit/chainlit/blob/d4eeeb8f8055e1d5f90607f8cfcbf28b89618952/backend/chainlit/__init__.py#L6
[pde]: https://pypi.org/project/python-dotenv/

**A peek under the hood.** In [the first post of this series][1st], I demonstrated that our AI Keeper could consult the internet when both of us were unsure about a particular rule. Behind the scene, this was what happened:

[1st]: https://blog.myli.page/lets-write-an-ai-keeper-for-call-of-cthulhu-part-i-design-demo-703ae46ece1b

<img width="733" alt="image" src="https://github.com/user-attachments/assets/56120b22-2dc2-4c41-9b44-7d0b14ade8e3">


## Incorporating an arbitrary PyPI library

**What if our chosen library lacks an off-the-shelf integration with LlamaIndex?** That's where we have to specify the tool's metadata ourselves. The nominal example in our project is [Cochar][cr], our character creation tool of choice. At the minimum, Cochar only requires a year and a country to generate a full character profile:

[cr]: https://www.cochar.pl/

```python
>>> print(cochar.create_character(1995, "US"))
Character
Name: Breland Justice
Sex: M, Age: 38, Country: US
Occupation: Tribe member
STR: 85 CON: 18 SIZ: 90
DEX: 81 APP: 15 EDU: 57
INT: 90 POW: 45 Luck: 35
Damage bonus: +1K6
Build: 2
Dodge: 40
Move rate: 7
Skills:
| Climb: 86 || Throw: 78 || Natural world: 15 |
| Listen: 22 || Occult: 15 || Spot hidden: 20 |
| Fighting (sword): 75 || Survival (jungle): 88 || Archeology: 67 |
| History: 6 || Locksmith: 49 || Mechanical repair: 42 |
| Pilot: 12 || Fast talk: 17 || Persuade: 16 |
| Fighting (whip): 8 || Language (latin): 2 || Credit rating: 7 |
```

**The output format needs an overhaul, though.** For CLI programs, these ASCII tables are fine, but they will look horrible in a chat bubble. I want a natural-language description of generated characters, so the LLM will run over the raw output. However, [LLMs are sensitive to][tllm] table formats (choice of delimiters, etc.) and partition marks (where a table begins and ends), both of which are improvised quite liberally in the above design. Let's avoid risking typography biasing our AI: We'd be better off standardizing to a data serialization format that your LLM likely **have seen a lot, across numerous topics**.

In terms of popularity, what can possibly be a better option than JSON?

[tllm]: https://www.microsoft.com/en-us/research/publication/table-meets-llm-can-large-language-models-understand-structured-table-data-a-benchmark-and-empirical-study/

```python
>>> print(cochar.create_character(1995, "US").get_json_format())
{'year': 1995, 'country': 'US', 'first_name': 'Japheth', 'last_name': 'Rowles', 'age': 46, 'sex': 'M', 'occupation': 'chauffeur', 'strength': 28, 'condition': 68, 'size': 65, 'dexterity': 61, 'appearance': 23, 'education': 57, 'intelligence': 76, 'power': 31, 'move_rate': 6, 'luck': 26, 'damage_bonus': '0', 'build': 0, 'skills': {'drive auto': 38, 'mechanical repair': 75, 'navigate': 83, 'psychology': 79, 'persuade': 18, 'art/craft': 30, 'acting': 49, 'jump': 79, 'library use': 21, 'pilot': 18, 'psychoanalysis': 2, 'stealth': 22, 'track': 12, 'credit rating': 25}, 'dodge': 30, 'sanity_points': 31, 'magic_points': 6, 'hit_points': 13}
```

We can wrap this into a small function called `make_character`. To declare it as a tool for LlamaIndex Agents, just wrap it with `FunctionTool.from_defaults`:

```python
@wraps(cochar.create_character)
def make_character(*args, **kwargs) -> dict:
    character: Character = cochar.create_character(*args, **kwargs)
    return character.get_json_format()

tool_for_creating_character = FunctionTool.from_defaults(
    make_character,
)
```

`FunctionTool.from_defaults` (and its [LangChain equivalent, `@tool`][td]) uses the docstring to describe the tool to the LLM, so we want to keep the docstring intact. (If it's not obvious -- `cochar.create_character` has a huge docstring, whereas `make_character` has none.) That's where `@wraps` comes to play. It copies [a handful of attributes][ha] of the original function to the wrapper function, including the docstring.

[td]: https://python.langchain.com/v0.1/docs/modules/tools/custom_tools/#tool-decorator
[ha]: https://stackoverflow.com/a/55102697/27163563

We are not done yet. As part of the `Character` class, Cochar also brings in a special class, `SkillsDict`. This customized dictionary type has an overridden `__setitem__` method, which Pydantic -- the library that LlamaIndex uses to infer input schema from function signatures -- doesn't like:

> pydantic.errors.PydanticSchemaGenerationError: Unable to generate pydantic-core schema for <class 'cochar.skill.SkillsDict'>. Set `arbitrary_types_allowed=True` in the model_config to ignore this error or implement `__get_pydantic_core_schema__` on your type to fully support it.

"Wait, where did you see `__setitem__` in the complaint?", I hear you ask. This brings us to a detour of some Python niches. Notice that `SkillDict` is declared as a subclass of the built-in type, `UserDict`.

```python
class SkillsDict(UserDict):
```

If you monkey-patched this `UserDict` to `dict`, Pydantic would stop complaining. However, `SkillsDict` needs to override `__setitem__`, so it can't subclass `dict` and have to implement the Abstract Base Class (ABC) `MutableMapping`. The class `UserDict` serves as a default implementation for just that. To paraphrase this [Stack Overflow answer][soa]:
* You subclass `dict` if you want to _extend_ (i.e., add more methods to) `dict`, and
* you subclass `UserDict` if you want to _override_ (i.e., rewrite existing methods on) `dict`.

That's enough detour of Python niches; back to the problem at hand. `arbitrary_types_allowed` looks risky to me, and I don't have control over the `SkillsDict` class. Let's just write a tool schema by hand:

```python
class CreateCharacterRequest(BaseModel):
    year: int = Field(
        1925,
        ge=1890,
        description="Year of the game, must be an integer starting from 1890.",
    )
    country: Literal["US", "PL", "ES"] = Field(
        ...,
        description="Country of the character's origin. Available options: 'US', 'PL', 'ES'.",
    )
    ...

tool_for_creating_character = FunctionTool.from_defaults(
    make_character,
    fn_schema=CreateCharacterRequest,
    description="Create a character.",
)
```

Writing a Pydantic model for the input schema also gives me a chance to reword some parameter descriptions, which helps the LLM understand the tool better. I can then get rid of the original docstring by overriding the `description=` in `FunctionTool.from_defaults` with a succinct one-liner. This also means our `make_character` function no longer needs its `@wraps` decorator. At this point, our tool looks like this to our agent:

<img width="910" alt="image" src="https://github.com/user-attachments/assets/1e131212-478a-45c3-803f-b057e4a2cb53">

[soa]: https://stackoverflow.com/a/7148602/27163563

## Defining our own Python function

==TODO==

## Creating a tool powered by LLM, for LLM

==TODO==

## Conclusion

==TODO==


<img width="1098" alt="image" src="https://github.com/user-attachments/assets/097a580a-67fa-4069-bdd6-32cea138976d">

_Photo by [Shane Scarbrough](https://unsplash.com/@darkelfdice?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash) on [Unsplash](https://unsplash.com/photos/text-vQVv4UIrYR4?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash)_
