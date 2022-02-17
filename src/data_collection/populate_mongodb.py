import os

from pymongo import MongoClient

from src.common.constants import DB_CONNECTION_STRING, FACTS_COLLECTION
from src.common.field_aliases import FIELD_ALIASES
from src.common.logger import log
from src.data_collection.edgar_collector import Crawler, EdgarResult

# -------------------------------------------------------------------------------


class DatabaseAdapter:
    def __init__(self, result: EdgarResult, collection) -> None:
        self.result = result
        self.collection = collection

        # load existing facts. they are stored as ticker_factname strings in a set
        # e.g. "AAPL_Revenues"
        self.existing_facts = set()
        for x in self.collection.find({}, {"ticker": 1, "name": 1}):
            self.existing_facts.add(f"{x['ticker']}_{x['name']}")

    def populate_database(self, ticker: str):
        """Populate databse from fields of crawler. Ticker is injected to be queried later."""
        facts_for_db = dict()
        for fact_name in self.result.facts:
            unit = list(self.result.facts[fact_name]["units"].keys())[0]
            fact_list = self.result.facts[fact_name]["units"][unit]

            # only put facts with "frame" in values array as these are the yearly stats
            fact_list = [
                f
                for f in fact_list
                if f.get("frame", None) and len(f.get("frame", ())) == 6
            ]
            fact_list.sort(key=lambda x: x["frame"])

            # do not write fact with empty values (this can be up to 50% of facts)
            if not fact_list:
                continue

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
            log.debug(f"Inserted {len(facts_for_db)} facts for {ticker}")
        else:
            log.info(f"No existing facts to insert for {ticker}")


if __name__ == "__main__":
    # DB INIT
    mongo_user = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    mongo_pass = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

    client = MongoClient(DB_CONNECTION_STRING, authSource="admin")
    db = client["edgar"]
    collection = db[FACTS_COLLECTION]

    ticker = "MPW"
    for ticker in ["AAPL", "TSLA", "MPW", "JPM", "F", "MSFT", "GOOG", "FB", "AMZN"]:
        query_result = db["ciks"].find_one({"ticker": {"$eq": ticker}})
        if query_result is not None:
            cik = str(query_result["cik"]).zfill(10)
        else:
            raise ValueError(f"Ticker {ticker} not found in DB")

        # CRAWL
        spider = Crawler(cik)  # 0001318605 = Tesla
        result = spider.fetch_facts()
        adapter = DatabaseAdapter(result, collection)
        adapter.populate_database(ticker)

    log.info("Database population done.")
