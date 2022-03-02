import os

from pymongo import MongoClient
from pymongo.database import Database

from src.common.constants import FACTS_COLLECTION, METRICS_COLLECTION


# ------------------------------ GENERIC PARENT CLASS -------------------------------------
class Metric:
    def __init__(
        self,
        name: str,
        ticker: str,
        raw_fields_needed: list[str],
        database: Database,
    ) -> None:
        self.name = name
        self.ticker = ticker
        self.raw_fields_needed = raw_fields_needed
        self.database = database
        self.values = dict()
        self.is_populated = False

    def __repr__(self) -> str:
        obj_representation = f"Metric({self.name}, {self.ticker})"
        requires_representation = f"requires: {self.raw_fields_needed}"
        return f"{obj_representation} --> {requires_representation}\n{self.values}"

    def __str__(self):
        s = "-" * 80 + "\n"
        s += f"Metric({self.name}, {self.ticker})"
        s += " --> "
        s += f"requires: {self.raw_fields_needed}\n"
        s += "{\n"
        for period, val in sorted(self.values.items(), key=lambda x: x[0]):
            s += f"\t{period}: {val},\n"
        s += "}"
        return s

    def _pull_data_from_db(self):
        facts = {k: None for k in self.raw_fields_needed}

        for fact in self.raw_fields_needed:
            query_result = self.database[FACTS_COLLECTION].find_one(
                {"ticker": self.ticker, "name": fact}
            )

            filtered_values = [
                val for val in query_result["values"] if len(val["frame"]) == 6
            ]
            # filtered_values.sort(key=lambda x: x["frame"])  # sort not necessary here
            query_result["values"] = filtered_values
            facts[fact] = query_result

        return facts

    def calculation(self):
        raise NotImplementedError

    def get_values_period_overlap(self, facts_dict: dict[str, dict]):
        """Returns the intersection of the periods of all values in the list."""
        period_intersection = []
        for periods in facts_dict.values():
            period_intersection.append(set(period for period in periods))
        return set.intersection(*period_intersection)

    def pull_facts_from_db(self, *fact_names) -> dict[str, dict]:
        """Returns mapping fact_name -> {period: value, ...}"""
        facts = self._pull_data_from_db()

        facts_to_return = {}
        for fact_name in fact_names:
            facts_to_return[fact_name] = {
                entry.get("frame"): entry.get("val")
                for entry in facts[fact_name]["values"]
            }

        return facts_to_return

    def populate(self):
        """Populates self.values based on self.raw_fields_needed and self.calculation()"""
        # maps fact_name -> list of value dicts
        facts = self.pull_facts_from_db(*self.raw_fields_needed)
        # metric calculation only possible when ALL facts are available for a period
        possible_metric_periods = self.get_values_period_overlap(facts)

        for period in possible_metric_periods:
            try:
                self.values[period] = self.calculation(period, facts)
            except KeyError:
                self.values[period] = None
            except ZeroDivisionError:
                self.values[period] = 0.0

        if self.values:
            self.is_populated = True

    def write_to_db(self):
        """Writes self.values to the database."""
        if not self.is_populated:
            raise ValueError("Metric must be populated before writing to database.")
        key = {"ticker": self.ticker, "name": self.name}
        self.database[METRICS_COLLECTION].update_one(
            key, {"$set": {"values": self.values}}, upsert=True
        )


# ------------------------------- SPECIFIC METRICS ------------------------------------


class RevenueProfitMargin(Metric):
    def __init__(self, ticker, database):
        super().__init__(
            name="RevenueProfitMargin",  # CHANGE THIS
            ticker=ticker,
            raw_fields_needed=["Revenues", "GrossProfit"],  # CHANGE THIS
            database=database,
        )

    def calculation(self, period, facts):
        return facts["GrossProfit"][period] / facts["Revenues"][period]  # CHANGE THIS


class AdsToRevenue(Metric):
    def __init__(self, ticker, database):
        super().__init__(
            name="AdsToRevenue",  # CHANGE THIS
            ticker=ticker,
            raw_fields_needed=["Revenues", "AdvertisingExpense"],  # CHANGE THIS
            database=database,
        )

    def calculation(self, period, facts):
        return (
            facts["AdvertisingExpense"][period] / facts["Revenues"][period]
        )  # CHANGE THIS


class FreeCashFlow(Metric):
    def __init__(self, ticker, database):
        super().__init__(
            name="FreeCashFlow",  # CHANGE THIS
            ticker=ticker,
            raw_fields_needed=[
                "NetCashProvidedByUsedInOperatingActivities",
                "PaymentsToAcquirePropertyPlantAndEquipment",
            ],  # CHANGE THIS
            database=database,
        )

    def calculation(self, period, facts):
        return (
            facts["NetCashProvidedByUsedInOperatingActivities"][period]
            - facts["PaymentsToAcquirePropertyPlantAndEquipment"][period]
        )  # CHANGE THIS
