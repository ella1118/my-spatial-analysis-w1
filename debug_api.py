import os
import requests
import json
from dotenv import load_dotenv
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入環境變數
load_dotenv()

# 從環境變數讀取 API 金鑰
api_key = os.getenv('CWA_API_KEY')

# API 端點
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"

# 請求參數
params = {
    'Authorization': api_key,
    'format': 'JSON'
}

try:
    # 發送請求 (忽略 SSL 憑證驗證)
    response = requests.get(url, params=params, verify=False)
    response.raise_for_status()
    
    # 解析 JSON 數據
    data = response.json()
    
    print(f"Success: {data.get('success')}")
    print(f"Keys: {list(data.keys())}")
    print(f"Result keys: {list(data.get('result', {}).keys())}")
    
    records = data.get('records', {})
    print(f"Records type: {type(records)}")
    print(f"Records keys: {list(records.keys())}")
    
    # 檢查是否有 Station 資料
    if 'Station' in records:
        stations = records['Station']
        print(f"Stations length: {len(stations)}")
        if stations:
            print(f"First station keys: {list(stations[0].keys())}")
            print(f"Sample station data: {json.dumps(stations[0], ensure_ascii=False, indent=2)[:800]}...")
    else:
        print("No 'Station' key found in records")
        print(f"Complete records: {json.dumps(records, ensure_ascii=False, indent=2)[:1000]}...")
    
except Exception as e:
    print(f"Error: {e}")
