from pymongo import MongoClient
import os
from rich.console import Console

print = Console().print

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(
    f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar", authSource="admin"
)
db = client["edgar"]
collection = db["facts"]

res_gross = collection.find(
    {"ticker": "AAPL", "name": "GrossProfit"}, {"period": 1, "value": 1, "_id": 0}
)
res_net = collection.find(
    {"ticker": "AAPL", "name": "NetIncomeLoss"}, {"period": 1, "value": 1, "_id": 0}
)

res_gross = [x for x in res_gross if len(x.get("period")) == 6]
res_net = [x for x in res_net if len(x.get("period")) == 6]

overlap = set(r.get("period") for r in res_gross).union(
    set(r.get("period") for r in res_gross)
)

gross = {v["period"]: v["value"] for v in res_gross}
net = {v["period"]: v["value"] for v in res_net}

metrics = []
for period in overlap:
    metric = net.get(period)/gross.get(period)
    metrics.append((period, metric))

metrics = sorted(metrics, key=lambda x: x[0])
for t in metrics:
    print(f"Period: {t[0]:<8}: Metric: {t[1]}")
