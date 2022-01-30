from typing import final
from crawler import Crawler
from pymongo import MongoClient
import os
from rich.console import Console
from field_aliases import FIELD_ALIASES
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")
# -------------------------------------------------------------------------------



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
        facts_for_db: dict[str, dict] = dict()  # maps fact_name -> dict of fact details
        for fact_name in self.crawler.facts:
            unit = list(self.crawler.facts[fact_name]["units"].keys())[0]
            fact_list = self.crawler.facts[fact_name]["units"][unit]

            # only put facts with "frame" in values array as these are the yearly stats
            fact_list = [f for f in fact_list if f.get("frame", None) and len(f.get("frame", ())) == 6]
            fact_list.sort(key=lambda x: x["frame"])

            # if fact exists do not re-create it
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

            facts_for_db[fact_name] = fact

            # update existing facts
            self.existing_facts.add(f"{ticker}_{fact_name}")

        # handle aliases: merge all facts with strange names into the "values" field of the real fact
        for alias, final_field_name in FIELD_ALIASES.items():
            try:
                values_of_alias = facts_for_db[alias].get("values", [])
            except KeyError:
                log.warning(f"No fact with name {alias} found for {ticker}.")
                continue

            final_fact = facts_for_db.get(final_field_name, None)
            if final_fact is None:
                final_fact = {
                    "ticker": ticker,
                    "name": final_field_name,
                    "values": [],
                    "unit": "",
                }

            final_fact["values"].extend(values_of_alias)
            final_fact["unit"] = facts_for_db[alias]["unit"]
            final_fact["values"].sort(key=lambda x: x["frame"])
            del facts_for_db[
                alias
            ]  # do not insert the facts with weird name: duplicates!

        if facts_for_db:
            self.collection.insert_many(
                list(facts_for_db.values())
            )  # TODO: refactor to update w/ upsert
        else:
            log.warning(f"No existing facts to insert for {ticker}")


if __name__ == "__main__":
    # DB INIT
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(
        f"mongodb://{mongo_user}:{mongo_pass}@localhost:27017/edgar?authSource=admin"
        # authSource referrs to admin collection in mongo, this needs to be here as a param otherwise: AuthenticationFailed
    )
    db = client["edgar"]
    collection = db["dev_facts"]
    collection.drop()

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

    log.info("Database population done.")
