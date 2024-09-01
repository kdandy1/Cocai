# CoCai: 抠菜

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A chatbot that plays Call of Cthulhu (CoC) with you, powered by AI.

一个陪你玩《克苏鲁的呼唤》（CoC）的聊天机器人，由AI驱动。

<img width="973" alt="image" src="https://github.com/user-attachments/assets/a8d2df9a-84b3-4c86-85ce-ade6469b213b">

Written in Python, this project uses the Rust-based package manager [`uv`](https://docs.astral.sh/uv/).

这个项目使用Python编写，使用基于Rust的包管理器[`uv`](https://docs.astral.sh/uv/)。

Inspired by the many impressive CoC replay videos on Bilibili, I'm programming this chatbot to operate in Chinese.

受到哔哩哔哩上那么多令人印象深刻的 CoC replay 视频的启发，我这个聊天机器人会以中文运行。

## Usage

First, ensure that your local Ollama server has already downloaded the two `qwen2:7b` models. If you haven't (or aren't sure), run the following command:

首先，确保你的本地 Ollama 服务器已经下载了两个 `qwen2:7b` 模型。如果你没有（或者不确定），运行以下命令：

```shell
ollama pull qwen2:7b-instruct # used by the Agent itself
ollama pull qwen2:7b-text # used by Agent's tools
```

You only have to this once in a lifetime. After that, you can start the chatbot by running:

这个操作只需要做一次。之后，你可以通过运行以下命令来启动聊天机器人：

```shell
just serve
```

## 计划

- [x] 写一个推荐技能的tool。其input应为对场景的描述。直接读取 `choices_prompt.md` 的内容，填充 `{{situation}}`，然后让LLM自动补完即可。
- [ ] 在建立自己的车卡功能之前，先写一个其他车卡工具的parser？例如[猫爷TRPG的车卡工具](https://maoyetrpg.com/ckshare.html)。
