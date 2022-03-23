import os
import random
import time

import requests
from bs4 import BeautifulSoup
from joblib import Parallel, delayed
from pymongo import MongoClient
from rich import print

from src.common.constants import AUTH_SOURCE, CIK_COLLECTION, DB_CONNECTION_STRING

# DB INIT
mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(DB_CONNECTION_STRING, authSource=AUTH_SOURCE)
db = client["edgar"]
collection = db[CIK_COLLECTION]

with open("data/working_proxies.txt", "r") as f:
    proxies = f.readlines()

print(f"Found {len(proxies)} proxies")


class MarketCapFetcher:
    def __init__(self, ticker: str):
        self.url = f"https://www.google.com/finance/quote/{ticker}"  # needs :EXCHANGE after ticker
        self.ticker = ticker
        self.css_class = "P6K39c"

    def _get(self, exchange):
        proxy = random.choice(proxies)
        page = requests.get(f"{self.url}:{exchange}", proxies={"http": proxy})

        soup = BeautifulSoup(page.content, "lxml")
        try:
            return soup.select(".eYanAe > div:nth-child(5) > div:nth-child(2)")[0].text
        except:
            return None

    def get_data(self):
        for exchange in ["NYSE", "NASDAQ", "OTCMKTS"]:
            result = self._get(exchange)
            if result:
                return result
        return None


# tickers = ["AAPL", "AMZN", "F", "FB", "GOOG", "JPM", "MPW", "MSFT", "TSLA"]
tickers = collection.distinct("ticker")[:100]
with open("data/sp500_tickers.txt") as f:
    tickers = [t.strip() for t in f.readlines()]


def get_market_cap(ticker: str):
    fetcher = MarketCapFetcher(ticker)
    result = fetcher.get_data()
    print(f"{ticker} - {result}")
    return {"ticker": ticker, "marketcap": result}


def number_literal_to_float(num: str) -> float:
    """Convert a number literal to a float, e.g. 1.2M USD -> 1200000.0. Ignores currency."""
    num = num.lower().replace("usd", "").replace("cad", "").replace(",", "").strip()
    suffix = num[-1]
    multiplier = 1
    if suffix == "t":
        multiplier = 1_000_000_000_000
    if suffix == "b":
        multiplier = 1_000_000_000
    elif suffix == "m":
        multiplier = 1_000_000
    elif suffix == "k":
        multiplier = 1_000

    return float(num[:-1]) * multiplier


if __name__ == "__main__":
    tic = time.perf_counter()
    mcs = Parallel(prefer="processes", n_jobs=10, verbose=100)(
        delayed(get_market_cap)(ticker) for ticker in tickers
    )
    tac = time.perf_counter()
    print(mcs)
    print(f"Took {tac-tic} seconds")

    for d in mcs:
        if d.get("marketcap"):
            collection.update_many(
                {"ticker": d.get("ticker")},
                {"$set": {"marketcap": number_literal_to_float(d.get("marketcap"))}},
            )
