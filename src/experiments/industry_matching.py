import os

from pymongo import MongoClient
from rich import print

from src.common.constants import AUTH_SOURCE, CIK_COLLECTION, DB_CONNECTION_STRING

# DB INIT
mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(DB_CONNECTION_STRING, authSource=AUTH_SOURCE)
db = client["edgar"]
collection = db[CIK_COLLECTION]

industries = list(collection.distinct("industry"))

# print(sorted(industries))


def get_same_industry(ticker: str):
    query = {"ticker": ticker}
    results = list(collection.find(query))
    industries = set([item.get("industry") for item in results])
    return list(collection.find({"industry": {"$in": list(industries)}}))


# print(get_same_industry("MSFT"))

import yfinance as yf
