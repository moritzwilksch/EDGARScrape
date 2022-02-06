import requests
import joblib
from rich import print
from bs4 import BeautifulSoup
import json


class RoicaiCrawler:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.url = f"https://roic.ai/company/{ticker}"

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Alt-Used": "roic.ai",
            "Connection": "keep-alive",
            "Referer": "https://roic.ai/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "TE": "trailers",
        }

    def get_html(self, load_from_cache=True):
        if load_from_cache:
            response = joblib.load(f"./{self.ticker}_response.joblib")
        else:
            response = requests.request("GET", self.url, headers=self.headers)
            joblib.dump(response, f"./{self.ticker}_response.joblib")

        return response.content


spider = RoicaiCrawler("AAPL")
html = spider.get_html(load_from_cache=True)

soup = BeautifulSoup(html, "lxml")
data = json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).text)

with open("datadump.json", "w") as f:
    json.dump(data, f, indent=4)
