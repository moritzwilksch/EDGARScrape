from src.common.logger import log

import requests
from dataclasses import dataclass


@dataclass
class EdgarResult:
    cik: str
    company_name: str
    facts: dict


# -------------------------------------------------------------------------------
class Crawler:
    """Crawler for a single CIKs fact sheet"""

    def __init__(self, cik: str):
        self.cik = cik
        self.company_name = None
        self.url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{self.cik}.json"

        self.headers = {
            "User-Agent": "Duke University info@duke.edu www.duke.edu",  # EDGAR requires basic ID
            "Accept-Encoding": "gzip, deflate",
        }

        self.facts = dict()

    # ------------------------------- Private Methods ------------------------------------
    def _fetch_data(self):
        response = requests.get(self.url, headers=self.headers)
        self.data = response.json()

    # ------------------------------- Public Methods ------------------------------------
    def fetch_facts(self) -> EdgarResult:
        """Fetches data and returns `EdgarResult`"""
        try:
            self._fetch_data()
        except Exception as e:
            log.warning(f"Failed to fetch data for {self.cik}")
            log.exception(e)

        self.company_name = self.data["entityName"]

        result = EdgarResult(cik=self.cik, company_name=self.company_name, facts=dict())
        us_gaap_facts = self.data["facts"]["us-gaap"]
        for fact in us_gaap_facts:
            result.facts[fact] = us_gaap_facts[fact]

        return result


if __name__ == "__main__":
    spider = Crawler("0001318605")
    result = spider.fetch_facts()
    log.info("Done.")
