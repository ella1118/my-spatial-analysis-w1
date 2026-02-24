import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 載入環境變數
load_dotenv()

def get_weather_data():
    """
    獲取中央氣象局自動氣象觀測站即時數據
    API: O-A0003-001 (自動氣象站-氣象觀測資料)
    """
    # 從環境變數讀取 API 金鑰
    api_key = os.getenv('CWA_API_KEY')
    if not api_key:
        print("錯誤：請在 .env 檔案中設定 CWA_API_KEY")
        return None
    
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
        
        # 檢查 API 回應狀態
        if data.get('success') != 'true':
            print(f"API 錯誤：{data.get('message', '未知錯誤')}")
            print(f"完整回應：{json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
            return None
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"網路請求錯誤：{e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤：{e}")
        return None

def extract_temperature_data(weather_data):
    """
    從氣象數據中提取氣溫資訊
    """
    if not weather_data:
        return []
    
    temperature_data = []
    stations = weather_data.get('records', {}).get('Station', [])
    
    for station in stations:
        try:
            # 基本站點資訊
            station_info = {
                'station_id': station.get('StationId'),
                'station_name': station.get('StationName', ''),
                'location': {
                    'county': station.get('GeoInfo', {}).get('CountyName', ''),
                    'town': station.get('GeoInfo', {}).get('TownName', ''),
                    'latitude': None,
                    'longitude': None
                },
                'observation_time': station.get('ObsTime', {}).get('DateTime', ''),
                'weather_elements': {}
            }
            
            # 提取座標 (使用 WGS84)
            coordinates = station.get('GeoInfo', {}).get('Coordinates', [])
            for coord in coordinates:
                if coord.get('CoordinateName') == 'WGS84':
                    station_info['location']['latitude'] = coord.get('StationLatitude')
                    station_info['location']['longitude'] = coord.get('StationLongitude')
                    break
            
            # 提取氣象要素
            weather_elements = station.get('WeatherElement', {})
            
            station_info['weather_elements']['temperature'] = weather_elements.get('AirTemperature')
            station_info['weather_elements']['humidity'] = weather_elements.get('RelativeHumidity')
            station_info['weather_elements']['pressure'] = weather_elements.get('AirPressure')
            station_info['weather_elements']['wind_speed'] = weather_elements.get('WindSpeed')
            station_info['weather_elements']['wind_direction'] = weather_elements.get('WindDirection')
            station_info['weather_elements']['weather'] = weather_elements.get('Weather')
            station_info['weather_elements']['precipitation'] = weather_elements.get('Now', {}).get('Precipitation')
            
            temperature_data.append(station_info)
            
        except Exception as e:
            print(f"處理站點 {station.get('StationId', 'Unknown')} 資料時發生錯誤：{e}")
            continue
    
    return temperature_data

def save_temperature_data(temperature_data, filename=None):
    """
    將氣溫數據儲存到檔案
    """
    if not temperature_data:
        print("沒有資料可儲存")
        return
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temperature_data_{timestamp}.json"
    
    output_path = os.path.join('outputs', filename)
    
    # 確保 outputs 資料夾存在
    os.makedirs('outputs', exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(temperature_data, f, ensure_ascii=False, indent=2)
    
    print(f"氣溫數據已儲存至：{output_path}")

def print_temperature_summary(temperature_data):
    """
    列出氣溫數據摘要
    """
    if not temperature_data:
        print("沒有氣溫數據可顯示")
        return
    
    print(f"\n=== 全台氣象站氣溫數據摘要 ===")
    print(f"總計 {len(temperature_data)} 個測站")
    print(f"更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    # 過濾有效氣溫數據
    valid_temps = []
    for d in temperature_data:
        temp = d['weather_elements'].get('temperature')
        if temp and temp != '-99':
            try:
                valid_temps.append((float(temp), d))
            except ValueError:
                continue
    
    if valid_temps:
        valid_temps.sort(key=lambda x: x[0])
        print(f"最高氣溫：{valid_temps[-1][0]}°C - {valid_temps[-1][1]['station_name']} ({valid_temps[-1][1]['location']['county']}{valid_temps[-1][1]['location']['town']})")
        print(f"最低氣溫：{valid_temps[0][0]}°C - {valid_temps[0][1]['station_name']} ({valid_temps[0][1]['location']['county']}{valid_temps[0][1]['location']['town']})")
    
    print("\n前15個測站資料：")
    for i, station in enumerate(temperature_data[:15]):
        temp = station['weather_elements'].get('temperature', 'N/A')
        humidity = station['weather_elements'].get('humidity', 'N/A')
        weather = station['weather_elements'].get('weather', 'N/A')
        location = f"{station['location']['county']}{station['location']['town']}"
        
        print(f"{i+1:2d}. {station['station_name']:12s} | {location:15s} | 氣溫: {temp:5s}°C | 濕度: {humidity:5s}% | 天氣: {weather:4s}")

if __name__ == "__main__":
    print("正在獲取中央氣象局即時氣溫數據...")
    
    # 獲取氣象數據
    weather_data = get_weather_data()
    
    if weather_data:
        # 提取氣溫資料
        temperature_data = extract_temperature_data(weather_data)
        
        # 顯示摘要
        print_temperature_summary(temperature_data)
        
        # 儲存數據
        save_temperature_data(temperature_data)
        
        print(f"\n成功獲取 {len(temperature_data)} 個氣象站的數據")
    else:
        print("無法獲取氣象數據")
