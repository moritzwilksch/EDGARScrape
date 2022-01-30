import requests
import logging
from rich.logging import RichHandler

logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")
# -------------------------------------------------------------------------------

with open("data/usGaapKeys.txt", "r") as f:
    all_keys = [line.strip() for line in f.readlines()]

keys_of_interest = [
    "AccountsPayable",
    "AdvertisingExpense",
    "Assets",
    "AssetsCurrent",
    "AssetsNoncurrent",
    "Cash",
    "CostOfGoodsAndServicesSold",
    "DepreciationAndAmortization",
    "Dividends",
    "EarningsPerShareDiluted",
    "EffectiveIncomeTaxRateContinuingOperations",
    "Goodwill",
    "GrossProfit",
    "IncomeTaxesPaidNet",
    "InterestExpense",
    "InventoryNet",
    "Liabilities",
    "LiabilitiesAndStockholdersEquity",
    "LiabilitiesCurrent",
    "LiabilitiesNoncurrent",
    "LongTermDebt",
    "MarketingExpense",
    "NetCashProvidedByUsedInFinancingActivities",
    "NetCashProvidedByUsedInInvestingActivities",
    "NetCashProvidedByUsedInOperatingActivities",
    "NetIncomeLoss",
    "NoncurrentAssets",
    "OperatingExpenses",
    "OperatingIncomeLoss",
    "OtherAssetsCurrent",
    "OtherAssetsNoncurrent",
    "PaymentsOfDividends",
    "PropertyPlantAndEquipmentGross",
    "PropertyPlantAndEquipmentNet",
    "ResearchAndDevelopmentExpense",
    "Revenues",
    "SellingGeneralAndAdministrativeExpense",
    "ShareBasedCompensation",
    "ShortTermDebtWeightedAverageInterestRate",
    "StockholdersEquity",
    "WeightedAverageNumberOfDilutedSharesOutstanding",
]


class Crawler:
    """Crawler for a single CIKs fact sheet"""

    def __init__(self, cik: str):
        self.cik = cik
        self.company_name = None
        self.url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{self.cik}.json"

        self.headers = {
            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/43.4",
            "User-Agent": "Duke University info@duke.edu www.duke.edu",
            "Accept-Encoding": "gzip, deflate",
        }

        self.facts = dict()

    # ------------------------------- Private Methods ------------------------------------
    def _request_data(self) -> requests.Response:
        return requests.get(self.url, headers=self.headers)

    def _fetch_data(self):
        response = self._request_data()
        self.data = response.json()

    # ------------------------------- Public Methods ------------------------------------
    def populate_facts(self):
        """Fetches data and populates `facts` field"""
        try:
            self._fetch_data()
        except Exception as e:
            log.warning(f"Failed to fetch data for {self.cik}")
            log.exception(e)

        us_gaap_facts = self.data["facts"]["us-gaap"]
        for fact in us_gaap_facts:
            self.facts[fact] = us_gaap_facts[fact]

        self.company_name = self.data["entityName"]


if __name__ == "__main__":
    spider = Crawler("0001318605")
    spider.populate_facts()
