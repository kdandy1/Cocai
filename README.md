# CoCai: 抠菜

A chatbot that plays Call of Cthulhu (CoC) with you, powered by AI.

一个陪你玩《克苏鲁的呼唤》（CoC）的聊天机器人，由AI驱动。

Written in Python, this project uses the Rust-based package manager [`uv`](https://docs.astral.sh/uv/).

这个项目使用Python编写，使用基于Rust的包管理器[`uv`](https://docs.astral.sh/uv/)。

Inspired by the many impressive CoC replay videos on Bilibili, I'm programming this chatbot to operate in Chinese.

受到哔哩哔哩上那么多令人印象深刻的 CoC replay 视频的启发，我这个聊天机器人会以中文运行。

计划：

- [ ] 写一个推荐技能的tool。其input应为对场景的描述。直接读取 `choices_prompt.md` 的内容，填充 `{{situation}}`，然后让LLM自动补完即可。
- [ ] 在建立自己的车卡功能之前，先写一个其他车卡工具的parser？例如[猫爷TRPG的车卡工具](https://maoyetrpg.com/ckshare.html)。
