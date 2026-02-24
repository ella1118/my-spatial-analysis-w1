import math
import json
from datetime import datetime

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    使用 Haversine 公式計算兩點間的球面距離
    
    Args:
        lat1, lon1: 第一點的緯度和經度
        lat2, lon2: 第二點的緯度和經度
    
    Returns:
        距離（公里）
    """
    # 將經緯度從度數轉換為弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine 公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # 地球半徑（公里）
    r = 6371
    distance = c * r
    
    return distance

def calculate_distances_to_taipei_station(weather_data, taipei_lat=25.0478, taipei_lon=121.5170):
    """
    計算所有測站到台北車站的距離
    
    Args:
        weather_data: 氣象數據列表
        taipei_lat: 台北車站緯度 (預設: 25.0478)
        taipei_lon: 台北車站經度 (預設: 121.5170)
    
    Returns:
        包含距離資訊的測站數據列表
    """
    stations_with_distance = []
    
    for station in weather_data:
        try:
            # 獲取測站座標
            lat_str = station['location']['latitude']
            lon_str = station['location']['longitude']
            
            if not lat_str or not lon_str:
                continue
                
            lat = float(lat_str)
            lon = float(lon_str)
            
            # 計算距離
            distance = haversine_distance(lat, lon, taipei_lat, taipei_lon)
            
            # 複製測站資料並新增距離資訊
            station_with_distance = station.copy()
            station_with_distance['distance_to_taipei'] = {
                'kilometers': round(distance, 2),
                'taipei_station_coords': {
                    'latitude': taipei_lat,
                    'longitude': taipei_lon
                }
            }
            
            stations_with_distance.append(station_with_distance)
            
        except (ValueError, TypeError, KeyError) as e:
            print(f"處理測站 {station.get('station_name', 'Unknown')} 時發生錯誤: {e}")
            continue
    
    return stations_with_distance

def save_distance_data(stations_with_distance, filename=None):
    """
    儲存包含距離資訊的測站數據
    
    Args:
        stations_with_distance: 包含距離資訊的測站數據
        filename: 輸出檔案名稱
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stations_with_distance_{timestamp}.json"
    
    output_path = f"outputs/{filename}"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stations_with_distance, f, ensure_ascii=False, indent=2)
    
    print(f"距離數據已儲存至：{output_path}")
    return output_path

def print_distance_summary(stations_with_distance):
    """
    列出距離摘要統計
    
    Args:
        stations_with_distance: 包含距離資訊的測站數據
    """
    if not stations_with_distance:
        print("沒有測站數據可分析")
        return
    
    # 按距離排序
    sorted_stations = sorted(stations_with_distance, 
                          key=lambda x: x['distance_to_taipei']['kilometers'])
    
    distances = [s['distance_to_taipei']['kilometers'] for s in stations_with_distance]
    
    print(f"\n=== 測站到台北車站距離分析 ===")
    print(f"分析時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"台北車站座標：25.0478°N, 121.5170°E")
    print(f"有效測站數量：{len(stations_with_distance)}")
    print("-" * 60)
    
    # 統計資訊
    print(f"📊 距離統計：")
    print(f"   最近距離：{min(distances):.2f} 公里")
    print(f"   最遠距離：{max(distances):.2f} 公里")
    print(f"   平均距離：{sum(distances)/len(distances):.2f} 公里")
    print(f"   中位數距離：{sorted(distances)[len(distances)//2]:.2f} 公里")
    
    print(f"\n📍 最近的前10個測站：")
    for i, station in enumerate(sorted_stations[:10]):
        distance = station['distance_to_taipei']['kilometers']
        temp = station['weather_elements'].get('temperature', 'N/A')
        location = f"{station['location']['county']}{station['location']['town']}"
        
        print(f"   {i+1:2d}. {station['station_name']:12s} | {location:15s} | "
              f"距離: {distance:6.2f}km | 氣溫: {temp:5s}°C")
    
    print(f"\n📍 最遠的前5個測站：")
    for i, station in enumerate(sorted_stations[-5:], 1):
        distance = station['distance_to_taipei']['kilometers']
        temp = station['weather_elements'].get('temperature', 'N/A')
        location = f"{station['location']['county']}{station['location']['town']}"
        
        print(f"   {i}. {station['station_name']:12s} | {location:15s} | "
              f"距離: {distance:6.2f}km | 氣溫: {temp:5s}°C")

if __name__ == "__main__":
    import os
    from weather_api import load_weather_data
    
    # 查找最新的氣溫數據檔案
    output_dir = 'outputs'
    json_files = [f for f in os.listdir(output_dir) 
                if f.startswith('temperature_data_') and f.endswith('.json')]
    
    if not json_files:
        print("找不到氣溫數據檔案，請先執行 weather_api.py 獲取數據")
        exit(1)
    
    # 使用最新的檔案
    latest_file = sorted(json_files)[-1]
    json_path = os.path.join(output_dir, latest_file)
    
    print(f"載入氣溫數據：{json_path}")
    
    # 載入數據
    with open(json_path, 'r', encoding='utf-8') as f:
        weather_data = json.load(f)
    
    # 計算距離
    print("計算各測站到台北車站的距離...")
    stations_with_distance = calculate_distances_to_taipei_station(weather_data)
    
    # 顯示摘要
    print_distance_summary(stations_with_distance)
    
    # 儲存結果
    save_distance_data(stations_with_distance)
    
    print(f"\n✅ 距離分析完成！共分析了 {len(stations_with_distance)} 個測站")
