import json
import folium
from folium.plugins import HeatMap
import pandas as pd
import os
from datetime import datetime

def load_weather_data(json_file):
    """
    載入氣溫數據
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_temperature_color(temperature):
    """
    根據氣溫返回對應的顏色
    """
    try:
        temp = float(temperature)
        if temp < 20:
            return 'blue'  # 藍色：氣溫 < 20°C
        elif temp <= 28:
            return 'green'  # 綠色：20°C ≤ 氣溫 ≤ 28°C
        else:
            return 'orange'  # 橘色：氣溫 > 28°C
    except (ValueError, TypeError):
        return 'gray'  # 灰色：無效數據

def create_weather_map(weather_data, output_file=None):
    """
    建立氣溫地圖
    """
    # 計算台灣中心點作為地圖初始中心
    valid_stations = [station for station in weather_data 
                     if station['location']['latitude'] and station['location']['longitude']
                     and station['weather_elements'].get('temperature') 
                     and station['weather_elements']['temperature'] != '-99']
    
    if not valid_stations:
        print("沒有有效的測站數據")
        return None
    
    # 計算中心點
    lats = [float(station['location']['latitude']) for station in valid_stations]
    lons = [float(station['location']['longitude']) for station in valid_stations]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # 建立地圖
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # 建立圖例
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 150px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>氣溫圖例</h4>
    <i class="fa fa-circle" style="color:blue"></i> < 20°C<br>
    <i class="fa fa-circle" style="color:green"></i> 20-28°C<br>
    <i class="fa fa-circle" style="color:orange"></i> > 28°C<br>
    <i class="fa fa-circle" style="color:gray"></i> 無效數據
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # 統計數據
    total_stations = len(weather_data)
    valid_temp_stations = len(valid_stations)
    
    # 添加測站標記
    for station in weather_data:
        lat = station['location']['latitude']
        lon = station['location']['longitude']
        
        if not lat or not lon:
            continue
            
        try:
            lat_float = float(lat)
            lon_float = float(lon)
        except (ValueError, TypeError):
            continue
        
        # 獲取氣象數據
        temp = station['weather_elements'].get('temperature', 'N/A')
        humidity = station['weather_elements'].get('humidity', 'N/A')
        weather = station['weather_elements'].get('weather', 'N/A')
        wind_speed = station['weather_elements'].get('wind_speed', 'N/A')
        
        # 獲取顏色
        color = get_temperature_color(temp)
        
        # 建立彈出視窗內容
        popup_content = f"""
        <b>{station['station_name']}</b><br>
        <b>測站ID:</b> {station['station_id']}<br>
        <b>位置:</b> {station['location']['county']}{station['location']['town']}<br>
        <b>氣溫:</b> {temp}°C<br>
        <b>濕度:</b> {humidity}%<br>
        <b>天氣:</b> {weather}<br>
        <b>風速:</b> {wind_speed} m/s<br>
        <b>更新時間:</b> {station['observation_time']}
        """
        
        # 建立標記
        folium.CircleMarker(
            location=[lat_float, lon_float],
            radius=8,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{station['station_name']}: {temp}°C",
            color='black',
            fillColor=color,
            fillOpacity=0.7,
            weight=1
        ).add_to(m)
    
    # 添加標題
    title_html = f'''
    <h3 align="center" style="font-size:16px"><b>台灣氣象站即時氣溫分布圖</b></h3>
    <p align="center" style="font-size:12px">更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
    有效測站: {valid_temp_stations}/{total_stations}</p>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # 儲存地圖
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"outputs/weather_map_{timestamp}.html"
    
    # 確保 outputs 資料夾存在
    os.makedirs('outputs', exist_ok=True)
    
    m.save(output_file)
    print(f"氣溫地圖已儲存至：{output_file}")
    
    return m

def create_temperature_heatmap(weather_data, output_file=None):
    """
    建立氣溫熱力圖
    """
    # 過濾有效數據
    heat_data = []
    for station in weather_data:
        lat = station['location']['latitude']
        lon = station['location']['longitude']
        temp = station['weather_elements'].get('temperature')
        
        if not lat or not lon or not temp or temp == '-99':
            continue
            
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            temp_float = float(temp)
            # 熱力圖權重使用氣溫值
            heat_data.append([lat_float, lon_float, temp_float])
        except (ValueError, TypeError):
            continue
    
    if not heat_data:
        print("沒有有效的數據可建立熱力圖")
        return None
    
    # 計算中心點
    lats = [point[0] for point in heat_data]
    lons = [point[1] for point in heat_data]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # 建立地圖
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # 添加熱力圖
    HeatMap(
        heat_data,
        min_opacity=0.4,
        radius=15,
        blur=10,
        gradient={
            0.0: 'blue',
            0.3: 'cyan',
            0.5: 'lime',
            0.7: 'yellow',
            0.9: 'orange',
            1.0: 'red'
        }
    ).add_to(m)
    
    # 添加標題
    title_html = '''
    <h3 align="center" style="font-size:16px"><b>台灣氣象站氣溫熱力圖</b></h3>
    <p align="center" style="font-size:12px">更新時間: {}</p>
    '''.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    m.get_root().html.add_child(folium.Element(title_html))
    
    # 儲存地圖
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"outputs/weather_heatmap_{timestamp}.html"
    
    # 確保 outputs 資料夾存在
    os.makedirs('outputs', exist_ok=True)
    
    m.save(output_file)
    print(f"氣溫熱力圖已儲存至：{output_file}")
    
    return m

def main():
    """
    主函數
    """
    # 查找最新的氣溫數據檔案
    output_dir = 'outputs'
    json_files = [f for f in os.listdir(output_dir) if f.startswith('temperature_data_') and f.endswith('.json')]
    
    if not json_files:
        print("找不到氣溫數據檔案，請先執行 weather_api.py 獲取數據")
        return
    
    # 使用最新的檔案
    latest_file = sorted(json_files)[-1]
    json_path = os.path.join(output_dir, latest_file)
    
    print(f"載入氣溫數據：{json_path}")
    
    # 載入數據
    weather_data = load_weather_data(json_path)
    
    # 建立氣溫分布地圖
    print("建立氣溫分布地圖...")
    create_weather_map(weather_data)
    
    # 建立氣溫熱力圖
    print("建立氣溫熱力圖...")
    create_temperature_heatmap(weather_data)
    
    print("地圖建立完成！")

if __name__ == "__main__":
    main()
