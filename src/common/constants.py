import os

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# Database related
DB_CONNECTION_STRING = f"mongodb://{mongo_user}:{mongo_pass}@65.108.135.187:27017"
AUTH_SOURCE = "edgar"

FACTS_COLLECTION = "dev_facts"
METRICS_COLLECTION = "dev_metrics"
LOGS_COLLECTION = "scrape_logs"
CIK_COLLECTION = "ciks"
