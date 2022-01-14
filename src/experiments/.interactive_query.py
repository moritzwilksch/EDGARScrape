#%%
from unicodedata import category
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
# res = collection.aggregate(
#     [
#         {"$match": {"name": "AccountsPayableCurrent"}},
#         {"$group": {"_id": "$ticker", "count": {"$sum": 1}}},
#     ]
# )

#%%

#%%
import polars as pl

data = collection.find(
    {"ticker": {"$in": ["AAPL", "JPM", "F"]}},
    {"ticker": 1, "name": 1, "period": 1, "_id": 0},
)

#%%

df = pl.from_records(list(data)).with_columns(
    [
        pl.col("ticker").cast(pl.Categorical),
        pl.col("name").cast(pl.Categorical),
        # pl.col("period").cast(pl.Categorical),
    ]
)

#%%
low_occurence_facts = (
    df.groupby(["ticker", "name"])
    .agg({"period": "count"})
    .sort("period_count")
    .groupby("ticker")
    .apply(lambda g: g[:10])
)

#%%
print(df.groupby("name").agg({"period": ["min", "max"]}))

#%%
res = collection.aggregate(
    [{"$group": {"_id": ["$ticker", "$name"], "size": {"$count": {}}}}]
)

#%%
for x in res:
    print(x)
    break
