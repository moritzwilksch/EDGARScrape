import time
import requests
from bs4 import BeautifulSoup
from joblib import Parallel, delayed

from src.common.constants import CIK_COLLECTION
import os
from pymongo import MongoClient
from rich import print
import random
# DB INIT
mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

client = MongoClient(
    f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar?authSource=admin"
)
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


tickers = ["AAPL", "AMZN", "F", "FB", "GOOG", "JPM", "MPW", "MSFT", "TSLA"]
# tickers = collection.distinct("ticker")[:100]
# with open("data/sp500_tickers.txt") as f:
#     tickers = [t.strip() for t in f.readlines()]



def get_market_cap(ticker: str):
    fetcher = MarketCapFetcher(ticker)
    result = fetcher.get_data()
    print(f"{ticker} - {result}")
    return {"ticker": ticker, "marketcap": result}


tic = time.perf_counter()
mcs = Parallel(prefer="processes", n_jobs=10, verbose=100)(
    delayed(get_market_cap)(ticker) for ticker in tickers
)
tac = time.perf_counter()
print(mcs)
print(f"Took {tac-tic} seconds")


# for d in mcs:
#     if d.get("marketcap"):
#         collection.update_many({"ticker": d.get("ticker")}, {"$set": {"marketcap": d.get("marketcap")}})