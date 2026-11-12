import sys
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pandas as pd

if len(sys.argv) > 1:
    INPUT_FILE = f"{sys.argv[1]}"

session = requests.Session()
TIMEOUT = 15

def gen_header(PORTAL, MAC):
    return {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C)",
        "X-User-Agent": "Model: MAG250; Link: WiFi",
        "Referer": f"{PORTAL}/c/",
        "Cookie": f"mac={MAC}; stb_lang=en; timezone=UTC",
    }

def handshake(PORTAL, MAC):
    url = f"{PORTAL}/portal.php"
    params = {"type": "stb", "action": "handshake", "token": "", "JsHttpRequest": "1-xml"}
    r = session.get(url, headers=gen_header(PORTAL, MAC), params=params, timeout=TIMEOUT, verify=False)
    r.raise_for_status()
    data = r.json()
    token = data["js"]["token"]
    return token

def get_account_info(PORTAL, MAC, token):
    url = f"{PORTAL}/portal.php"
    headers = gen_header(PORTAL, MAC)
    headers["Authorization"] = f"Bearer {token}"
    params = {"type": "account_info", "action": "get_main_info", "JsHttpRequest": "1-xml"}
    r = session.get(url, headers=headers, params=params, timeout=TIMEOUT, verify=False)
    r.raise_for_status()
    return r.json()

def get_expiry(PORTAL, MAC):
    token = handshake(PORTAL, MAC)
    account = get_account_info(PORTAL, MAC, token)
    js = account.get("js", {})
    return (js.get("end_date") or js.get("phone") or js.get("tariff_plan") or js.get("account_expiration"))

df = pd.read_csv(INPUT_FILE, dtype=str)
results = []
for _, row in df.iterrows():
    result = row.copy()
    try:
        result['Expiry'] = get_expiry(row['PORTAL'], row['MAC'])
    except:
        result['Expiry'] = "Invalid"
    results.append(result)

result_df = pd.DataFrame(results)

# Sort by Expiry from furthest to closest (descending order)
result_df['Expiry_dt'] = pd.to_datetime(result_df['Expiry'], errors='coerce')
result_df = result_df.sort_values(by='Expiry_dt', ascending=False, na_position='last')
result_df = result_df.drop(columns=['Expiry_dt'])

result_df.to_csv(INPUT_FILE, index=False)