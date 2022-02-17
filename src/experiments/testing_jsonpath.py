import os

from jsonpath_ng import parse
from pymongo import MongoClient
from rich import print

from src.common.constants import DB_CONNECTION_STRING, FACTS_COLLECTION

# DB INIT
mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(DB_CONNECTION_STRING, authSource="admin")
db = client["edgar"]
collection = db[FACTS_COLLECTION]

res = list(collection.find({"ticker": "AAPL"}, limit=2))
# print(list(res))

# exp = parse("data[*].values")
# # print(dir(exp))
# print([m.value for m in exp.find({"data": res})])


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
exp = parse("table_data.Revenues.*")
print([m.value for m in exp.find(stub)])
