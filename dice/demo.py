import chainlit as cl


@cl.on_chat_start
async def main():
    message = cl.Message(
        content="Let me roll them dices for you:",
        elements=[
            cl.Pdf(
                name="fake-pdf",
                display="inline",
                url="/roll_dice?d4=1&d6=2&d8=3&d10=4&d12=5&d20=6",
            )
        ],
    )
    await message.send()
