import requests
from dataclasses import dataclass
import pandas as pd
from joblib import Parallel, delayed
from rich import print
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Host": "www.sec.gov",

}


@dataclass
class Proxy:
    ip: str
    port: str
    https: str


# response = requests.get("https://proxybase.de")
response = requests.get("https://free-proxy-list.net")
try:
    df = pd.read_html(response.content)[0]
except:
    print("No table found. Exiting.")

df = df.query("Https == 'no'")#.query("Google == 'yes'")
print(df)



proxies = []
for _, ip, port, https in df[["IP Address", "Port", "Https"]].itertuples():
    # print(f"{ip}:{port}")
    proxies.append(Proxy(ip=ip, port=port, https=https))

print(f"Found {len(proxies)} proxies")

# proxies = [Proxy(ip="196.0.111.194", port="34638")]






# def is_working(proxy: Proxy):
#     # print(f"----- {proxy.ip}:{proxy.port} -----")
#     try:
#         response = requests.get(
#             # "http://api.ipify.org",
#             # "http://ipinfo.io/ip",
#             "https://www.google.com/",
#             proxies={
#                 "http" if proxy.https == "no" else "https": f"https://{proxy.ip}:{proxy.port}",
#                 # "https": f"socks5://{proxy.ip}:{proxy.port}",
#             },
#             timeout=2,
#             headers=headers,
#         )
#     except requests.exceptions.Timeout:
#         print("Timeout")
#         return False
#     except requests.exceptions.ProxyError:
#         print("Proxy error")
#         return False
#     except:
#         print("Generic error")
#         return False
    
#     if "google" in response.text and "robot" in response.text:
#         return proxy
#     else:
#         print("Doesn't work")
#         return False

def is_working(proxy: Proxy):
    protocol = "http" if proxy.https == "no" else "https"
    try:
        response = requests.get(
            f"{protocol}://api.ipify.org",
            proxies={
                protocol: f"{protocol}://{proxy.ip}:{proxy.port}",
            },
            timeout=3,
            headers=headers,
        )
    except:
        return False
    
    if re.match("^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$", response.text):
        print(f"{proxy.ip}:{proxy.port}")
        return proxy
    
    return False



working = Parallel(n_jobs=100, prefer="threads")(delayed(is_working)(proxy) for proxy in proxies)

print(working)

for p in working:
    if p:
        print(f"{p.ip}:{p.port}")