import os

from pymongo import MongoClient
from pymongo.database import Database
from rich.console import Console

from src.common.constants import DB_CONNECTION_STRING, FACTS_COLLECTION
from src.metrics.metric_definition import AdsToRevenue, FreeCashFlow, RevenueProfitMargin

c = Console()

if __name__ == "__main__":
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(DB_CONNECTION_STRING, authSource="admin")
    db = client["edgar"]
    collection = db[FACTS_COLLECTION]
    metric1 = RevenueProfitMargin("AAPL", db)
    metric1.populate()
    c.print(metric1)
    metric1.write_to_db()

    metric2 = AdsToRevenue("AAPL", db)
    metric2.populate()
    c.print(metric2)
    metric2.write_to_db()

    metric3 = FreeCashFlow("AAPL", db)
    metric3.populate()
    c.print(metric3)
    metric3.write_to_db()
