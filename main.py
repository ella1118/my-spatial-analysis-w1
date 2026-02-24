#!/usr/bin/env python3
"""
台灣氣象數據空間分析主程式
Spatial Analysis of Taiwan Weather Data

功能：
1. 獲取中央氣象局即時氣象數據
2. 建立互動式溫度分布地圖
3. 生成溫度熱力圖
"""

import os
import sys
import argparse
from datetime import datetime

# 導入自定義模組
from weather_api import get_weather_data, extract_temperature_data, save_temperature_data
from weather_map import create_weather_map, create_temperature_heatmap
from distance_calculator import calculate_distances_to_taipei_station, save_distance_data, print_distance_summary


def main():
    """
    主函數 - 執行完整的氣象數據分析流程
    """
    parser = argparse.ArgumentParser(description='台灣氣象數據空間分析')
    parser.add_argument('--skip-api', action='store_true', 
                      help='跳過 API 請求，使用現有數據')
    parser.add_argument('--map-only', action='store_true',
                      help='只生成地圖，不獲取新數據')
    parser.add_argument('--distance-only', action='store_true',
                      help='只計算距離分析，不生成地圖')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌡️  台灣氣象數據空間分析系統")
    print("=" * 60)
    
    # 步驟 1: 獲取氣象數據
    if not args.skip_api and not args.map_only:
        print("\n📡 步驟 1: 獲取中央氣象局氣象數據...")
        weather_data = get_weather_data()
        
        if weather_data:
            # 提取溫度數據
            temperature_data = extract_temperature_data(weather_data)
            
            # 儲存原始數據
            save_temperature_data(temperature_data)
            
            print(f"✅ 成功獲取 {len(temperature_data)} 個測站數據")
        else:
            print("❌ 無法獲取氣象數據，程式終止")
            sys.exit(1)
    
    # 步驟 2: 建立地圖視覺化
    if not args.distance_only:
        print("\n🗺️  步驟 2: 建立地圖視覺化...")
        
        # 載入最新的氣象數據
        output_dir = 'outputs'
        json_files = [f for f in os.listdir(output_dir) 
                    if f.startswith('temperature_data_') and f.endswith('.json')]
        
        if not json_files:
            print("❌ 找不到氣象數據檔案")
            sys.exit(1)
        
        latest_file = sorted(json_files)[-1]
        json_path = os.path.join(output_dir, latest_file)
        
        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            weather_data = json.load(f)
        
        # 建立溫度分布地圖
        print("   📍 建立溫度分布地圖...")
        create_weather_map(weather_data)
        
        # 建立溫度熱力圖
        print("   🔥 建立溫度熱力圖...")
        create_temperature_heatmap(weather_data)
    
    # 步驟 3: 計算距離分析
    print("\n📏 步驟 3: 計算測站到台北車站距離...")
    
    # 載入最新的氣象數據
    output_dir = 'outputs'
    json_files = [f for f in os.listdir(output_dir) 
                if f.startswith('temperature_data_') and f.endswith('.json')]
    
    if not json_files:
        print("❌ 找不到氣象數據檔案")
        sys.exit(1)
    
    latest_file = sorted(json_files)[-1]
    json_path = os.path.join(output_dir, latest_file)
    
    import json
    with open(json_path, 'r', encoding='utf-8') as f:
        weather_data = json.load(f)
    
    # 計算距離
    stations_with_distance = calculate_distances_to_taipei_station(weather_data)
    
    # 顯示距離摘要
    print_distance_summary(stations_with_distance)
    
    # 儲存距離數據
    save_distance_data(stations_with_distance)
    
    # 步驟 4: 顯示結果摘要
    if not args.distance_only:
        print("\n📊 步驟 4: 分析結果摘要")
        print("-" * 40)
        
        valid_stations = [station for station in weather_data 
                       if station['weather_elements'].get('temperature') 
                       and station['weather_elements']['temperature'] != '-99']
        
        if valid_stations:
            temps = [float(s['weather_elements']['temperature']) for s in valid_stations]
            print(f"有效測站數量: {len(valid_stations)}")
            print(f"平均溫度: {sum(temps)/len(temps):.1f}°C")
            print(f"最高溫度: {max(temps):.1f}°C")
            print(f"最低溫度: {min(temps):.1f}°C")
    
    print(f"\n📁 輸出檔案位置: {os.path.abspath(output_dir)}")
    print("\n✅ 分析完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
