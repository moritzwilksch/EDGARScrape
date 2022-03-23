import os
from pathlib import Path
from traceback import FrameSummary

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jsonpath_ng import parse
from pymongo import MongoClient
from rich import print

from src.common.constants import AUTH_SOURCE, DB_CONNECTION_STRING, FACTS_COLLECTION

FRAMES_JSONPATH = parse("values[*].frame")

# DB INIT
mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(DB_CONNECTION_STRING, authSource=AUTH_SOURCE)
db = client["edgar"]
collection = db[FACTS_COLLECTION]

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
        "Dividend": "USD/share",
    },
    "table_data": {
        "Revenues": {"AAPL": 42, "MSFT": 12, "GOOG": 3, "AMZN": 2, "FB": 1},
        "Expenses": {"AAPL": 24, "MSFT": 5, "GOOG": 9, "AMZN": 8, "FB": 7},
        "Net Income": {"AAPL": 18, "MSFT": -2, "GOOG": -3, "AMZN": -4, "FB": -5},
        "Dividend": {"AAPL": 0.5, "MSFT": 0.2, "GOOG": 0.3, "AMZN": 0.4, "FB": 0.1},
    },
}


def get_most_recent_common_fact_values(fact_name: str, tickers: list):
    query = {"name": fact_name, "ticker": {"$in": tickers}}
    results = list(collection.find(query))

    frame_sets = []
    for item in results:
        frame_sets.append(set(m.value for m in FRAMES_JSONPATH.find(item)))
    most_recent_common_frame = max(set.intersection(*frame_sets))

    return_data = {fact_name: dict()}

    for res in results:
        value = [
            val["val"]
            for val in res["values"]
            if val["frame"] == most_recent_common_frame
        ][0]
        return_data[fact_name][res["ticker"]] = value

    return most_recent_common_frame, return_data


print(
    get_most_recent_common_fact_values(
        "Revenues", ["AAPL", "MSFT", "GOOG", "AMZN", "FB"]
    )
)


@app.get("/")
async def root(request: Request):
    print(
        get_most_recent_common_fact_values(
            "Revenues", ["AAPL", "MSFT", "GOOG", "AMZN", "FB"]
        )
    )
    return templates.TemplateResponse(
        "index.html", {"request": request, "id": id, "data": stub}
    )
