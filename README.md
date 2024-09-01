# CoCai

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A chatbot that plays Call of Cthulhu (CoC) with you, powered by AI.


<img width="1176" alt="image" src="https://github.com/user-attachments/assets/f47f9b62-c93c-4933-a167-03cbe079c29e">

<img width="1754" alt="image" src="https://github.com/user-attachments/assets/0a83a329-04c8-45d2-98e1-c6c33a84c065">


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
