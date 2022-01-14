#%%
from pymongo import MongoClient
import os
import pandas as pd

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(
    f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar?authSource=admin"
    # authSource referrs to admin collection in mongo, this needs to be here as a param otherwise: AuthenticationFailed
)
db = client["edgar"]
collection = db["facts"]

#%%
res = collection.aggregate(
    [
        {"$match": {"name": "AccountsPayableCurrent"}},
        {"$group": {"_id": "$ticker", "count": {"$sum": 1}}},
    ]
)

#%%
from rich.console import Console

print = Console().print

#%%
for x in res:
    print(x)
