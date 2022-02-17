import os

from joblib import Parallel, delayed
from pymongo import MongoClient

from src.common.constants import DB_CONNECTION_STRING

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(DB_CONNECTION_STRING, authSource="admin")
db = client["edgar"]
collection = db["compute_tasks"]

collection.drop()
collection.insert_one({"ticker": "TSLA", "visited": 0})


def increment_by_ten():
    for i in range(100):
        collection.update_one({"ticker": "TSLA"}, {"$inc": {"visited": 1}})


Parallel(n_jobs=20, prefer="threads")(delayed(increment_by_ten)() for _ in range(600))
