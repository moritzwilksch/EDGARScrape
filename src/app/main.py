from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# from os.path import dirname, join

# current_dir = dirname(__file__)  # this will be the location of the current .py file
# template_path = join(current_dir, "templates")
templates = Jinja2Templates(directory="src/app/templates")


app = FastAPI()
app.mount(
    "/src/app/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)

stub = {
    "companies": ["AAPL", "MSFT", "GOOG", "AMZN", "FB"],
    "units": {
        "Revenues": "USD",
        "Expenses": "USD",
        "Net Income": "USD",
        "Dividend": "USD/share"
    },

    "table_data": {
        "Revenues": {"AAPL": 42, "MSFT": 12, "GOOG": 3, "AMZN": 2, "FB": 1},
        "Expenses": {"AAPL": 24, "MSFT": 5, "GOOG": 9, "AMZN": 8, "FB": 7},
        "Net Income": {"AAPL": 18, "MSFT": -2, "GOOG": -3, "AMZN": -4, "FB": -5},
        "Dividend": {"AAPL": 0.5, "MSFT": 0.2, "GOOG": 0.3, "AMZN": 0.4, "FB": 0.1}

    }
}

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "id": id, "data": stub})
