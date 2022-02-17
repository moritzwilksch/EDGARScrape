import os
import time

import pymongo
from joblib import Parallel, delayed
from pymongo import MongoClient

from src.common.constants import (DB_CONNECTION_STRING, FACTS_COLLECTION,
                                  LOGS_COLLECTION)
from src.common.logger import log
from src.data_collection.edgar_collector import Crawler
from src.data_collection.populate_mongodb import DatabaseAdapter

# -------------------------------------------------------------------------------


def read_cik_from_db(ticker: str, db) -> str:
    """Read and return CIK for ticker from DB."""
    query_result = db["ciks"].find_one({"ticker": {"$eq": ticker}})
    if query_result is not None:
        cik = str(query_result["cik"]).zfill(10)
    else:
        raise ValueError(f"Ticker {ticker} not found in DB")

    return cik


def scrape_one_ticker(
    ticker: str,
    db,
    data_collection: pymongo.collection.Collection,
    meta_collection: pymongo.collection.Collection,
):
    """Scrape one ticker and populate DB. Logs to `scrape_meta` collection"""

    log.debug(f"Scraping {ticker}...")
    metadata = dict()
    try:
        # CRAWL
        cik = read_cik_from_db(ticker, db)
        spider = Crawler(cik)
        result = spider.fetch_facts()
        adapter = DatabaseAdapter(result, data_collection)
        adapter.populate_database(ticker)
        log.debug(f"{ticker:<5} -> [green]Success[/]", extra={"markup": True})
    except ValueError:
        metadata = {"ticker": ticker, "status": "error", "msg": "cik not found"}
        log.warning(f"{ticker:<5} -> CIK not found")

    except Exception as e:
        metadata = {"ticker": ticker, "status": "error", "msg": "unknown error"}
        log.error(f"{ticker:<5} -> Unkown error")
        log.exception(e)

    finally:
        if metadata:
            meta_collection.insert_one(metadata)

    time.sleep(0.75)


def main(
    db,
    data_collection: pymongo.collection.Collection,
    meta_collection: pymongo.collection.Collection,
):
    with open("data/sp500_tickers.txt") as f:
        tickers = f.read().splitlines()

    log.debug("Dispatching threads...")
    Parallel(n_jobs=5, prefer="threads")(
        delayed(scrape_one_ticker)(ticker, db, data_collection, meta_collection)
        for ticker in tickers
    )
    log.info("Done.")


if __name__ == "__main__":
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(DB_CONNECTION_STRING, authSource="admin")
    db = client["edgar"]
    data_collection = db[FACTS_COLLECTION]
    meta_collection = db[LOGS_COLLECTION]

    main(db, data_collection, meta_collection)
