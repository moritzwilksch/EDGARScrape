import pymongo
from pymongo import MongoClient
import os
from crawler import Crawler
from populate_mongodb import CrawlerToMongoAdapter
import time
from joblib import Parallel, delayed
from rich.console import Console

c = Console()


def read_cik_from_db(ticker: str) -> str:
    """ Read and return CIK for ticker from DB. """
    query_result = db["ciks"].find_one({"ticker": {"$eq": ticker}})
    if query_result is not None:
        cik = str(query_result["cik"]).zfill(10)
    else:
        raise ValueError(f"Ticker {ticker} not found in DB")

    return cik


def scrape_one_ticker(
    ticker: str,
    data_collection: pymongo.collection.Collection,
    meta_collection: pymongo.collection.Collection,
):
    """ Scrape one ticker and populate DB. Logs to `scrape_meta` collection"""
    metadata = {
        "ticker": ticker,
        "status": "pending",
    }  # optional: msg field with error message
    c.print(f"Scraping {ticker}...")
    try:
        # CRAWL
        cik = read_cik_from_db(ticker)
        spider = Crawler(cik)  # 0001318605 = Tesla
        spider.populate_facts()
        adapter = CrawlerToMongoAdapter(spider, data_collection)
        adapter.populate_database(ticker)
        metadata["status"] = "success"
        c.print(f"{ticker:<5} -> Success", style="green")
    except ValueError as e:
        metadata["status"] = "error"
        metadata["msg"] = "cik not found"
        c.print(f"{ticker:<5} -> CIK not found", style="yellow")

    except Exception as e:
        metadata["status"] = "error"
        metadata["msg"] = "unknown error"
        c.print(f"{ticker:<5} -> Unkown error", style="red")

    finally:
        meta_collection.insert_one(metadata)

    time.sleep(0.75)


def main(
    data_collection: pymongo.collection.Collection,
    meta_collection: pymongo.collection.Collection,
):
    with open("data/sp500_tickers.txt") as f:
        tickers = f.read().splitlines()

    Parallel(n_jobs=5, prefer="threads")(
        delayed(scrape_one_ticker)(ticker, data_collection, meta_collection)
        for ticker in tickers
    )


if __name__ == "__main__":
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(
        f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar", authSource="admin"
    )
    db = client["edgar"]
    data_collection = db["facts"]
    meta_collection = db["scrape_meta"]

    main(data_collection, meta_collection)
