from typing import Annotated, List

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Template

app = FastAPI()


# Mount the 'static' directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Template for rendering the dice in the HTML
dice_template = open("index.jinja").read()


@app.get("/roll_dice", response_class=HTMLResponse)
async def roll_dice(
    d4: Annotated[List[int] | None, Query()] = None,
    d6: Annotated[List[int] | None, Query()] = None,
    d8: Annotated[List[int] | None, Query()] = None,
    d10: Annotated[List[int] | None, Query()] = None,
    d12: Annotated[List[int] | None, Query()] = None,
):
    # Prepare a list of dice types and their values
    dice_data = []

    if d4:
        dice_data.append(["d4", d4])
    if d6:
        dice_data.append(["d6", d6])
    if d8:
        dice_data.append(["d8", d8])
    if d10:
        dice_data.append(["d10", d10])
    if d12:
        dice_data.append(["d12", d12])

    # Render the template with the dice data passed as context
    template = Template(dice_template)
    print(dice_data)
    return template.render(dice_options=dice_data)
