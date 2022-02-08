from gc import collect
from src.common.constants import CIK_COLLECTION
import os
from pymongo import MongoClient
from rich import print

# DB INIT
mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar?authSource=admin")
db = client["edgar"]
collection = db[CIK_COLLECTION]

industries = list(collection.distinct("industry"))

# print(sorted(industries))


def get_same_industry(ticker: str):
    query = {"ticker": ticker}
    results = list(collection.find(query))
    industries = set([item.get("industry") for item in results])
    return list(collection.find({"industry": {"$in": list(industries)}}))

print(get_same_industry("MSFT"))