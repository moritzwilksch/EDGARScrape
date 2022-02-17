#%%
import os

from pymongo import MongoClient
from rich import print as print

from src.common.constants import DB_CONNECTION_STRING, FACTS_COLLECTION

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(DB_CONNECTION_STRING, authSource="admin")
db = client["edgar"]
collection = db[FACTS_COLLECTION]

#%%
# res = collection.aggregate(
#     [
#         {"$match": {"name": "AccountsPayableCurrent"}},
#         {"$group": {"_id": "$ticker", "count": {"$sum": 1}}},
#     ]
# )

#%%
res = collection.distinct(
    key="name",
    filter={"values.0": {"$exists": True}},
)

print(f"Found {len(res)} distinct fact names with values.")
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
