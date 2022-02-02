from pymongo import MongoClient
import os
from src.common.constants import FACTS_COLLECTION

from rich.console import Console
from rich.table import Table


c = Console()

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(
    f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar", authSource="admin"
)
db = client["edgar"]
collection = db[FACTS_COLLECTION]

res_gross: list[dict] = collection.find(
    {"ticker": "AAPL", "name": "SalesRevenueNet"}, {"values": 1, "_id": 0}
).next()["values"]
res_net: list[dict] = collection.find(
    {"ticker": "AAPL", "name": "NetIncomeLoss"}, {"values": 1, "_id": 0}
).next()["values"]

res_gross = [
    x for x in res_gross if len(x.get("frame")) == 6
]  # only use CYXXXX, not CYXXXXQ3
res_net = [
    x for x in res_net if len(x.get("frame")) == 6
]  # only use CYXXXX, not CYXXXXQ3

overlap = set(r.get("frame") for r in res_gross).union(
    set(r.get("frame") for r in res_gross)
)

gross = {v["frame"]: v["val"] for v in res_gross}
net = {v["frame"]: v["val"] for v in res_net}

metrics = []
for period in overlap:
    metric = net.get(period) / gross.get(period)
    metrics.append((period, metric))

metrics = sorted(metrics, key=lambda x: x[0])
table = Table(title="Metric over Time")
table.add_column("Period", justify="center")
table.add_column("Value", justify="center")

for t in metrics:
    table.add_row(f"{t[0]}", f"{t[1]:.5f}")
c.clear()
c.print(table)
