from pymongo.database import Database
import os
from pymongo import MongoClient


class Metric:
    FACTS_COLLECTION = "facts"
    METRICS_COLLECTION = "metrics"

    def __init__(
        self,
        name: str,
        ticker: str,
        period: str,
        raw_fields_needed: list[str],
        database: Database,
    ) -> None:
        self.name = name
        self.ticker = ticker
        self.period = period
        self.raw_fields_needed = raw_fields_needed
        self.database = database
        self.value = None

    def __repr__(self) -> str:
        obj_representation = f"Metric({self.name}, {self.ticker}, {self.period}, {self.value})"
        requires_representation = f"requires: {self.raw_fields_needed}"
        return f"{obj_representation} --> {requires_representation}"

    def __str__(self):
        return self.__repr__()

    def _pull_data_from_db(self):
        facts = {k: None for k in self.raw_fields_needed}

        for fact in self.raw_fields_needed:
            facts[fact] = self.database[Metric.FACTS_COLLECTION].find_one(
                {"ticker": self.ticker, "name": fact, "period": self.period}
            )

        return facts

    def calculate(self):
        raise NotImplementedError


class RevenueProfitMargin(Metric):
    def calculate(self):
        facts = self._pull_data_from_db()
        gross_profit = facts["GrossProfit"]["value"]
        revenues = facts["Revenues"]["value"]
        self.value = gross_profit / revenues
