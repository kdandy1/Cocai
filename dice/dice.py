from itertools import chain, repeat
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
    # Use List instead of Iterable here, so that multiple values can be passed in the query parameter.
    d4: Annotated[List[int], Query()] = [],
    d6: Annotated[List[int], Query()] = [],
    d8: Annotated[List[int], Query()] = [],
    d10: Annotated[List[int], Query()] = [],
    d12: Annotated[List[int], Query()] = [],
):
    # Prepare a list of dice types and their values
    dice_data = [
        [dice_type, dice_value]
        for dice_type, dice_value in chain.from_iterable(
            [
                zip(repeat("d4"), d4),
                zip(repeat("d6"), d6),
                zip(repeat("d8"), d8),
                zip(repeat("d10"), d10),
                zip(repeat("d12"), d12),
            ]
        )
    ]
    # Render the template with the dice data passed as context
    template = Template(dice_template)
    return template.render(dice_options=dice_data)
