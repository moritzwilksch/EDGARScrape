from pymongo import MongoClient
import os
from joblib import Parallel, delayed

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(
    f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar?authSource=admin"
    # authSource referrs to admin collection in mongo, this needs to be here as a param otherwise: AuthenticationFailed
)
db = client["edgar"]
collection = db["compute_tasks"]

collection.drop()
collection.insert_one({"ticker": "TSLA", "visited": 0})


def increment_by_ten():
    for i in range(100):
        collection.update_one({"ticker": "TSLA"}, {"$inc": {"visited": 1}})


Parallel(n_jobs=3, prefer="threads")(delayed(increment_by_ten)() for _ in range(600))
