from crawler import Crawler
from pymongo import MongoClient
import os
from rich.console import Console

c = Console()


class CrawlerToMongoAdapter:
    def __init__(self, crawler: Crawler, collection) -> None:
        self.crawler = crawler
        self.collection = collection

        # load existing facts. they are stored as ticker_factname strings in a set
        # e.g. "AAPL_Revenues"
        self.existing_facts = set()
        for x in self.collection.find({}, {"ticker": 1, "name": 1}):
            self.existing_facts.add(f"{x['ticker']}_{x['name']}")

    def populate_database(self, ticker: str):
        """Populate databse from fields of crawler. Ticker is injected to be queried later."""
        facts = []
        for fact_name in self.crawler.facts:
            unit = list(self.crawler.facts[fact_name]["units"].keys())[0]
            fact_list = self.crawler.facts[fact_name]["units"][unit]

            # only put facts with "frame" in values array as these are the yearly stats
            fact_list = [f for f in fact_list if f.get("frame", None)]

            # if fact exists, do not re-create it
            if f"{ticker}_{fact_name}" in self.existing_facts:
                continue

            # create fact
            fact = dict(
                # company_name=self.crawler.company_name,  # TODO: Is the full name necessary?
                ticker=ticker,
                name=fact_name,
                values=fact_list,
                unit=unit,  # actual unit, e.g. USD
            )

            facts.append(fact)

            # update existing facts
            self.existing_facts.add(f"{ticker}_{fact_name}")

        if facts:
            self.collection.insert_many(facts)
        else:
            c.print(f"[yellow][WARN][/] No non-existing facts to insert for {ticker}")


if __name__ == "__main__":
    # DB INIT
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(
        f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar?authSource=admin"
        # authSource referrs to admin collection in mongo, this needs to be here as a param otherwise: AuthenticationFailed
    )
    db = client["edgar"]
    collection = db["facts"]

    TICKER = "MPW"
    for TICKER in ["AAPL", "TSLA", "MPW", "JPM", "F"]:
        query_result = db["ciks"].find_one({"ticker": {"$eq": TICKER}})
        if query_result is not None:
            cik = str(query_result["cik"]).zfill(10)
        else:
            raise ValueError(f"Ticker {TICKER} not found in DB")

        # CRAWL
        spider = Crawler(cik)  # 0001318605 = Tesla
        spider.populate_facts()
        adapter = CrawlerToMongoAdapter(spider, collection)
        adapter.populate_database(TICKER)

    c.print("Database population done.", style="green")
