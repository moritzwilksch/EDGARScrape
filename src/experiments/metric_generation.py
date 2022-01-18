from pymongo.database import Database
import os
from pymongo import MongoClient
from metric_definition import RevenueProfitMargin
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
    metric1 = RevenueProfitMargin("RevenueProfitMargin", "AAPL", "CY2016", ["Revenues", "GrossProfit"], db)
    metric1.calculate()
    c.print(metric1)
