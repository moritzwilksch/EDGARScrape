from crawler import Crawler
from pymongo import MongoClient
import pymongo

client = MongoClient("localhost", 27017)
db = client["edgar"]
collection = db["facts"]

print("Initialized.")

class CrawlerToMongoAdapter:
    def __init__(self, crawler: Crawler, collection) -> None:
        self.crawler = crawler
        self.collection = collection

        # load existing facts
        self.existing_facts = set()
        for x in self.collection.find({'company_name': 1, 'name': 1, 'period': 1}):
            self.existing_facts.add(f"{x['company_name']}_{x['name']}_{x['period']}")

    def populate_database(self):
        facts = []
        for fact_name in self.crawler.facts:
            unit = list(self.crawler.facts[fact_name]["units"].keys())[0]
            for period in self.crawler.facts[fact_name]["units"][unit]:

                # if fact exists, do not re-create it
                if (
                    f"{self.crawler.company_name}_{fact_name}_{period}"
                    in self.existing_facts
                ):
                    continue

                # create fact
                fact = dict(
                    company_name=self.crawler.company_name,
                    name=fact_name,
                    period=f"{period['fp']}{period['fy']}",
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
    spider = Crawler("0001318605")
    spider.populate_facts()
    adapter = CrawlerToMongoAdapter(spider, collection)
    adapter.populate_database()
    print("done")