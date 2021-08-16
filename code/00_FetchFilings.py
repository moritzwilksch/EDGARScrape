#%%
import requests
import json


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
}
#%%
edgar_cik = "0000320193" # None
url = f"https://data.sec.gov/submissions/CIK{edgar_cik}.json"
r = requests.get(url, headers=headers)
data = r.json()


#%%
with open("../data/response.json", 'w') as f:
    json.dump(data, f)

#%%