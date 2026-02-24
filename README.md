# Spatial Analysis Project - Weather Data Visualization

## 📋 專案概述

這是一個空間分析專案，用於獲取和視覺化台灣各地氣象站的即時氣溫數據。

## 🌟 主要功能

- 🌡️ 串接中央氣象局 API 獲取即時氣象數據
- 🗺️ 使用 Folium 建立互動式地圖視覺化
- 🎨 依氣溫分色顯示（藍色 <20°C、綠色 20-28°C、橘色 >28°C）
- 📊 生成氣溫熱力圖
- 📍 包含 336 個台灣氣象站數據

## 🚀 快速開始

### 1. 環境設定

```bash
# 克隆專案
git clone https://github.com/ella1118/my-spatial-analysis-w1.git
cd my-spatial-analysis-w1

# 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# 或 .venv\Scripts\activate  # Windows

# 安裝依賴套件
pip install -r requirements.txt
```

### 2. 設定 API 金鑰

建立 `.env` 檔案並設定你的中央氣象局 API 金鑰：

```bash
# .env 檔案內容
CWA_API_KEY=your_cwa_api_key_here
```

**API 金鑰取得方式**：
1. 前往 [中央氣象局開放資料平台](https://opendata.cwa.gov.tw/)
2. 註冊帳號並申請 API 金鑰
3. 將金鑰填入 `.env` 檔案

### 3. 執行程式

```bash
# 獲取氣象數據
python3 weather_api.py

# 建立地圖視覺化
python3 weather_map.py
```

## 專案結構

```
my-spatial-analysis-w1/
├── 📄 main.py              ✅ 統一程式入口點
├── 📄 weather_api.py        ✅ API 模組
├── 📄 weather_map.py        ✅ 地圖視覺化模組  
├── 📄 distance_calculator.py ✅ 距離計算模組
├── 📄 .env                ✅ 環境變數設定 (不上傳 GitHub)
├── 📄 requirements.txt     ✅ 依賴套件
├── 📄 README.md           ✅ 專案說明
├── 📁 data/               ✅ 原始資料資料夾
└── 📁 outputs/            ✅ 輸出檔案資料夾
    ├── temperature_data_*.json    # 氣象數據
    ├── weather_map_*.html         # 氣溫分布地圖
    └── weather_heatmap_*.html    # 氣溫熱力圖
```

## 🎯 輸出檔案

執行程式後會在 `outputs/` 資料夾中生成：

- **temperature_data_*.json** - 包含所有氣象站的詳細數據
- **weather_map_*.html** - 互動式氣溫分布地圖
- **weather_heatmap_*.html** - 氣溫熱力圖

## 🗺️ 地圖功能

### 氣溫分布地圖
- 🔵 藍色標記：氣溫 < 20°C
- 🟢 綠色標記：氣溫 20-28°C  
- 🟠 橘色標記：氣溫 > 28°C
- ⚫ 灰色標記：無效數據

### 互動功能
- 點擊測站圓點查看詳細資訊
- 滑鼠懸停顯示測站名稱和氣溫
- 支援縮放和拖曳

## 📊 API 資料來源

- **中央氣象局開放資料平台**
- **API 端點**：O-A0003-001 (自動氣象站-氣象觀測資料)
- **更新頻率**：即時

## 🛠️ 開發環境

- Python 3.13+
- 主要套件：
  - `requests` - HTTP 請求
  - `python-dotenv` - 環境變數管理
  - `folium` - 地圖視覺化
  - `pandas` - 數據處理
  - `numpy` - 數值計算

## 📝 注意事項

1. 需要申請中央氣象局 API 金鑰
2. `.env` 檔案已加入 `.gitignore`，不會上傳到 GitHub
3. 地圖檔案為 HTML 格式，可直接在瀏覽器中開啟

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License
