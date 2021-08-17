# %%

from nbformat import current_nbformat
import requests


keys_to_extract = [
    'AccountsPayable',
    'AdvertisingExpense',
    'Assets',
    'AssetsCurrent',
    'AssetsNoncurrent',
    'Cash',
    'CostOfGoodsAndServicesSold',
    'DepreciationAndAmortization',
    'Dividends',
    'EarningsPerShareDiluted',
    'EffectiveIncomeTaxRateContinuingOperations',
    'Goodwill',
    'GrossProfit',
    'IncomeTaxesPaidNet',
    'InterestExpense',
    'InventoryNet',
    'Liabilities',
    'LiabilitiesAndStockholdersEquity',
    'LiabilitiesCurrent',
    'LiabilitiesNoncurrent',
    'LongTermDebt',
    'MarketingExpense',
    'NetCashProvidedByUsedInFinancingActivities',
    'NetCashProvidedByUsedInInvestingActivities',
    'NetCashProvidedByUsedInOperatingActivities',
    'NetIncomeLoss',
    'NoncurrentAssets',
    'OperatingExpenses',
    'OperatingIncomeLoss',
    'OtherAssetsCurrent',
    'OtherAssetsNoncurrent',
    'PaymentsOfDividends',
    'PropertyPlantAndEquipmentGross',
    'PropertyPlantAndEquipmentNet',
    'ResearchAndDevelopmentExpense',
    'Revenues',
    'SellingGeneralAndAdministrativeExpense',
    'ShareBasedCompensation',
    'ShortTermDebtWeightedAverageInterestRate',
    'StockholdersEquity',
    'WeightedAverageNumberOfDilutedSharesOutstanding',
]







class Crawler:
    """Crawler for a single CIKs fact sheet"""

    def __init__(self, cik: str):
        self.cik = cik
        self.url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{self.cik}.json"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
        }

        self.facts = dict()

    def _request_data(self) -> requests.Response:
        return requests.get(self.url, headers=self.headers)

    def _fetch_data(self):
        response = self._request_data()
        self.data = response.json()

    def _extract_from_data(self, path: str) -> dict:
        keys = path.split(".")
        current_level_json = self.data
        try:
            for key in keys:
                current_level_json = current_level_json[key]
            return current_level_json
        except KeyError:
            return {keys[-1]: 'KeyError'}

    def populate_facts(self):
        """Fetches data and populates `facts` field"""
        try:
            self._fetch_data()
        except Exception as e:
            print("Fetching data failed.")
            print(e)
        
        self.facts['sharesOutstanding'] = self._extract_from_data("facts.dei.EntityCommonStockSharesOutstanding.units.shares")
        self.facts['usGaap'] = self._extract_from_data("facts.us-gaap")
        print(self.facts)

        


