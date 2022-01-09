import requests
import json
from pymongo import MongoClient
import os

mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")


class CIKTickerPopulator:
    """ Fetches json of CIK <-> Ticker mappings from the SEC and updates them in the DB """

    def __init__(self, collection=None):
        self.collection = collection

        # load all existing ciks in memory to only add the new ones
        self.existing_ciks = set()
        for x in self.collection.find({}, {"cik": 1}):
            self.existing_ciks.add(x["cik"])

    def populate_database(self):
        # fetch mapping from SEC
        response = requests.get("https://www.sec.gov/files/company_tickers.json")

        mappings = []
        for triple in response.json().values():
            cik_str, ticker, title = (
                triple.get("cik_str"),
                triple.get("ticker"),
                triple.get("title"),
            )

            # only add new CIKs
            if cik_str in self.existing_ciks:
                continue

            mappings.append(
                {"cik": int(cik_str), "ticker": ticker, "title": title,}
            )

        # update mongo
        print(f"Adding {len(mappings)} mappings.")

        if mappings:
            self.collection.insert_many(mappings)


if __name__ == "__main__":
    # DB INIT
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(
        f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar?authSource=admin"
        # authSource referrs to admin collection in mongo, this needs to be here as a param otherwise: AuthenticationFailed
    )
    db = client["edgar"]
    collection = db["ciks"]

    # Populate
    populator = CIKTickerPopulator(collection=collection)
    populator.populate_database()
