# CoCai: 抠菜

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A chatbot that plays Call of Cthulhu (CoC) with you, powered by AI.

一个陪你玩《克苏鲁的呼唤》（CoC）的聊天机器人，由AI驱动。

<img width="1176" alt="image" src="https://github.com/user-attachments/assets/f47f9b62-c93c-4933-a167-03cbe079c29e">

Inspired by the many impressive CoC replay videos on Bilibili, I'm programming this chatbot to operate in Chinese.

受到哔哩哔哩上那么多令人印象深刻的 CoC replay 视频的启发，我这个聊天机器人会以中文运行。

## Usage

### Pre-requisites

Install [Ollama](https://ollama.com/download), a local server that runs large language models (LLMs). This chatbot uses Ollama to generate text. If you prefer to use more powerful LLMs, you can edit the code.

Ensure that your local Ollama server has already downloaded the two `qwen2:7b` models. If you haven't (or aren't sure), run the following command:

```shell
ollama pull qwen2:7b-instruct # used by the Agent itself
ollama pull qwen2:7b-text # used by Agent's tools
```

Install [`just`](https://github.com/casey/just), a command runner. I use this because I always tend to forget the exact command to run.

Written in Python, this project uses the Rust-based package manager [`uv`](https://docs.astral.sh/uv/). It does not require you to explicitly create a virtual environment.

### Running the Chatbot

You can start the chatbot by running:

```shell
just serve
```

## 计划

- [x] 写一个推荐技能的tool。其input应为对场景的描述。直接读取 `choices_prompt.md` 的内容，填充 `{{situation}}`，然后让LLM自动补完即可。
- [ ] 在建立自己的车卡功能之前，先写一个其他车卡工具的parser？例如[猫爷TRPG的车卡工具](https://maoyetrpg.com/ckshare.html)。
