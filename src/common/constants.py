import os

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
mongo_ip = os.getenv("MONGO_IP")

# Database related
DB_CONNECTION_STRING = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_ip}:27017"
AUTH_SOURCE = "edgar"

FACTS_COLLECTION = "dev_facts"
METRICS_COLLECTION = "dev_metrics"
LOGS_COLLECTION = "scrape_logs"
CIK_COLLECTION = "ciks"
