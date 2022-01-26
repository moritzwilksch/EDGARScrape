from pymongo.database import Database
import os
from pymongo import MongoClient


class Metric:
    FACTS_COLLECTION = "facts"
    METRICS_COLLECTION = "metrics"

    def __init__(
        self, name: str, ticker: str, raw_fields_needed: list[str], database: Database,
    ) -> None:
        self.name = name
        self.ticker = ticker
        self.raw_fields_needed = raw_fields_needed
        self.database = database
        self.values = dict()

    def __repr__(self) -> str:
        obj_representation = f"Metric({self.name}, {self.ticker}, {self.values})"
        requires_representation = f"requires: {self.raw_fields_needed}"
        return f"{obj_representation} --> {requires_representation}"

    def __str__(self):
        return self.__repr__()

    def _pull_data_from_db(self):
        facts = {k: None for k in self.raw_fields_needed}

        for fact in self.raw_fields_needed:
            facts[fact] = self.database[Metric.FACTS_COLLECTION].find_one(
                {"ticker": self.ticker, "name": fact}
            )

        return facts

    def pull_facts_from_db(self, *fact_names) -> dict[str, dict]:
        """ Returns mapping fact_name -> {period: value, ...} """
        facts = self._pull_data_from_db()

        facts_to_return = {}
        for fact_name in fact_names:
            facts_to_return[fact_name] = {
                entry.get("frame"): entry.get("val")
                for entry in facts[fact_name]["values"]
            }

        return facts_to_return

    def get_values_period_overlap(self, facts_dict: dict[str, dict]):
        """ Returns the intersection of the periods of all values in the list. """
        period_intersection = []
        for periods in facts_dict.values():
            period_intersection.append(set(period for period in periods))
        return set.intersection(*period_intersection)

    def calculate(self):
        # Blueprint:
        # 1. Pull data from DB:         self._pull_data_from_db()
        # 2. Pull out required fields:  facts[FIELD_NAME]["values"]
        # 3. Find period overlap:       self.get_values_period_overlap([v1, v2, v3])
        # 4. Calculate metric
        raise NotImplementedError


class RevenueProfitMargin(Metric):
    def calculate(self):
        # maps fact_name -> list of value dicts
        facts = self.pull_facts_from_db("Revenues", "GrossProfit")
        # metric calculation only possible when ALL facts are available for a period
        possible_metric_periods = self.get_values_period_overlap(facts)

        for period in possible_metric_periods:
            self.values[period] = facts["GrossProfit"][period] / facts["Revenues"][period]
