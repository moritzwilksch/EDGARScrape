import os

from pymongo import MongoClient
from rich import print as print

from src.common.constants import DB_CONNECTION_STRING, FACTS_COLLECTION
from src.common.logger import log

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(DB_CONNECTION_STRING, authSource="admin")
db = client["edgar"]
coll = db[FACTS_COLLECTION]


def get_year_from_frame(frame: str) -> int:
    return int(frame.lstrip("CY"))


pipeline = [
    {"$project": {"name": 1, "frame": "$values.frame"}},
    {"$unwind": {"path": "$frame"}},
    {"$group": {"_id": "$name", "frames": {"$push": "$frame"}}},
    {"$project": {"mrf": {"$max": "$frames"}}},
]

log.info("Querying...")
result = coll.aggregate(pipeline)
log.info("Writing...")
n = 0
lines = []
for r in result:
    n += 1
    name = r.get("_id")
    oldest_entry = get_year_from_frame(r.get("mrf"))
    if oldest_entry <= 2014:
        # print(f"{oldest_entry}, {name}")
        lines.append(f"{oldest_entry},{name}")

with open("data/potentially_deprecated_fields.csv", "w") as f:
    f.write("most_recent_entry,name\n")
    f.write("\n".join(lines))

print(f"{n} names")
log.info("Done")
