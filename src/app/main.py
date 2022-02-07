from src.common.constants import FACTS_COLLECTION


from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from pymongo import MongoClient
from rich import print

# DB INIT
mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(
    f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar?authSource=admin"
)
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
    values = [item.get("values") for item in results]
    frame_sets = []
    for val in values:
        frame_sets.append(set([item.get("frame") for item in val]))

    most_recent_common_frame = max(set.intersection(*frame_sets))

    return_data = {
        fact_name: dict()
    }

    for res in results:
        value = [val["val"] for val in res["values"] if val["frame"] == most_recent_common_frame][0]
        return_data[fact_name][res["ticker"]] = value

    return most_recent_common_frame, return_data




print(get_most_recent_common_fact_values("Revenues", ["AAPL", "MSFT"]))




@app.get("/")
async def root(request: Request):
    print(get_most_recent_common_fact_values("Revenues", ["AAPL", "MSFT", "GOOG", "AMZN", "FB"]))
    return templates.TemplateResponse(
        "index.html", {"request": request, "id": id, "data": stub}
    )
