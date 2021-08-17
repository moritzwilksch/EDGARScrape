#%%
import requests
import json
import crawler
import pandas as pd
from importlib import reload
reload(crawler)

#%%
spider = crawler.Crawler("0000320193")
spider.populate_facts()

subset = {k: v for k, v in spider.facts['usGaap'].items() if k in crawler.keys_to_extract}

#%%
pd.DataFrame(subset['EarningsPerShareDiluted']['units']['USD'])[['end', 'val']].rolling(4).mean().plot()