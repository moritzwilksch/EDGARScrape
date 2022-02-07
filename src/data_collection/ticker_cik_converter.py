from email import header
import requests
from pymongo import MongoClient
import os
from src.common.logger import log
import time
from joblib import Parallel, delayed, parallel_backend

# -------------------------------------------------------------------------------


mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")


class CIKTickerPopulator:
    """Fetches json of CIK <-> Ticker mappings from the SEC and updates them in the DB"""

    def __init__(self, collection=None):
        self.collection = collection

        self.headers = {
            "User-Agent": "Duke University info@duke.edu www.duke.edu",  # EDGAR requires basic ID
            "Accept-Encoding": "gzip, deflate",
        }

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
                {
                    "cik": int(cik_str),
                    "ticker": ticker,
                    "title": title,
                }
            )

        # update mongo
        log.info(f"Adding {len(mappings)} mappings.")

        if mappings:
            self.collection.insert_many(mappings)  # TODO: refactor to update w/ upsert??

    def _pull_industry_from_api(self, cik):
        try:
            response = requests.get(
                f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json",
                headers=self.headers,
            )
        except:
            log.warning("API call failed.")
            return None

        self.collection.update_one(
            {"cik": cik}, {"$set": {"industry": response.json().get("sicDescription")}}
        )
        log.debug(f"Got industry for CIK {cik}")
        time.sleep(1)

    def pull_all_industries_from_api(self, only_add_nonexisting: bool = True):
        ciks = [item.get("cik") for item in self.collection.find({"industry": {"$exists": not only_add_nonexisting}}, {"cik": 1})]

        _ = Parallel(n_jobs=4, prefer="threads")(
            delayed(self._pull_industry_from_api)(cik) for cik in ciks
        )
        log.info("Fetching industries DONE.")


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
    populator.pull_all_industries_from_api()
