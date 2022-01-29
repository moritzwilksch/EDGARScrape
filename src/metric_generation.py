from pymongo.database import Database
import os
from pymongo import MongoClient
from metric_definition import RevenueProfitMargin, AdsToRevenue
from rich.console import Console

c = Console()

if __name__ == "__main__":
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(
        f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar", authSource="admin"
    )
    db = client["edgar"]
    collection = db["facts"]
    metric1 = RevenueProfitMargin("AAPL", db)
    metric1.populate()
    c.print(metric1)
    metric1.write_to_db()

    metric2 = AdsToRevenue("AAPL", db)
    metric2.populate()
    c.print(metric2)
    metric2.write_to_db()

