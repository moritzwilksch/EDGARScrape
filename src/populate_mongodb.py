from crawler import Crawler
from pymongo import MongoClient
import os


class CrawlerToMongoAdapter:
    def __init__(self, crawler: Crawler, collection) -> None:
        self.crawler = crawler
        self.collection = collection

        # load existing facts
        self.existing_facts = set()
        for x in self.collection.find({"company_name": 1, "name": 1, "period": 1}):
            self.existing_facts.add(f"{x['company_name']}_{x['name']}_{x['period']}")

    def populate_database(self, ticker: str):
        """ Populate databse from fields of crawler. Ticker is injected to be queried later. """
        facts = []
        for fact_name in self.crawler.facts:
            unit = list(self.crawler.facts[fact_name]["units"].keys())[0]
            for period in self.crawler.facts[fact_name]["units"][unit]:

                # if fact exists, do not re-create it
                if (
                    f"{self.crawler.company_name}_{fact_name}_{period}"
                    in self.existing_facts
                ) or "frame" not in period:  # only the important periods contain the "frame" key
                    continue

                # create fact
                fact = dict(
                    # company_name=self.crawler.company_name,  # TODO: Is the full name necessary?
                    ticker=ticker,
                    name=fact_name,
                    period=period.get("frame"),
                    value=period["val"],
                    unit=unit,  # actual unit, e.g. USD
                )

                facts.append(fact)

                # update existing facts
                self.existing_facts.add(
                    f"{self.crawler.company_name}_{fact_name}_{period}"
                )

        self.collection.insert_many(facts)


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

        # TODO: DB contains duplicate entries for the same fact
    print("done")
