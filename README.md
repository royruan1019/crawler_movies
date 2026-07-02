# 🎬 Scrape Movies — Streamlit 版本

[ssr1.scrape.center](https://ssr1.scrape.center/) 爬蟲練習案的電影目錄，改寫為 **Streamlit** 應用，整合 **DeepSeek V4 Flash** 聊天機器人（透過 NVIDIA NIM API），需登入才能使用聊天功能。

---

> 🚀 **線上 Demo**：https://crawlermovies-jhwnpxkvlrzydhdjewwpyx.streamlit.app/

## 🧭 製作流程

### 1. 爬取電影列表
從爬蟲練習網站 https://ssr1.scrape.center 逐頁瀏覽所有電影列表頁（共 11 頁），取得每部電影的基本資料：名稱、分類標籤、產地、時長、上映日期、評分、封面圖片網址。

### 2. 爬取電影詳情
逐一進入每部電影的獨立詳情頁，抓取劇情簡介（summary）。

### 3. 下載封面圖片
將每部電影的封面圖片下載到本地 `images/` 資料夾，以電影 ID 命名。

### 4. 整理與儲存
所有電影資料彙整成結構化的 JSON 檔案（`movies.json`），包含 id、名稱、分類、產地、時長、上映日期、評分、封面路徑、簡介等欄位。

### 5. 建立網頁應用
- **初版**：使用 FastAPI + Jinja2 模板建立傳統多頁網頁，支援列表瀏覽、分頁、搜尋、分類篩選、詳情頁。
- **改寫版**：改用 Streamlit 單頁應用，簡化開發與部署流程，加入更多互動功能。

### 6. 加入聊天機器人
整合 DeepSeek V4 Flash 模型（透過 NVIDIA NIM API），提供電影相關問答功能，並加入登入機制保護聊天功能。

### 7. 部署
可部署至 Streamlit Cloud 或在本機執行，電影瀏覽功能無需設定即可使用。

---

## 🚀 快速開始

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 設定金鑰與帳密

**方法 A：使用 `.streamlit/secrets.toml`（本機開發）**

```toml
[deepseek]
api_key = "nvapi-你的金鑰"
base_url = "https://integrate.api.nvidia.com/v1"
model = "deepseek-ai/deepseek-v4-flash"

[users]
admin = "admin123"
```

**方法 B：使用 `config.json`**

```json
{
  "users": [{"username": "admin", "password": "admin123"}],
  "deepseek": {
    "api_key": "nvapi-你的金鑰",
    "base_url": "https://integrate.api.nvidia.com/v1",
    "model": "deepseek-ai/deepseek-v4-flash"
  }
}
```

> 取得 NVIDIA API Key：https://build.nvidia.com/deepseek-ai/deepseek-v4-flash → 註冊 → 設定 → Generate API Key

### 3. 啟動應用

```bash
streamlit run app.py --server.port 8501
```

開啟 http://localhost:8501

---

## ☁️ 部署到 Streamlit Cloud

1. **Push 到 GitHub**
   ```bash
   git add .
   git commit -m "init"
   git push -u origin main
   ```

2. **到 Streamlit Cloud** https://streamlit.io/cloud
   - New app → 選你的 repo → 主檔案 `app.py`

3. **設定 Secrets**（Settings → Secrets）：
   ```toml
   [deepseek]
   api_key = "nvapi-你的金鑰"
   base_url = "https://integrate.api.nvidia.com/v1"
   model = "deepseek-ai/deepseek-v4-flash"

   [users]
   admin = "admin123"
   ```

4. **Deploy！** 🚀

---

## 🧩 功能

| 功能 | 說明 |
|------|------|
| 🎬 電影列表 | 搜尋、分類篩選、分頁（4 欄卡片） |
| 💬 聊天機器人 | 使用 DeepSeek V4 Flash 模型回答電影問題 |
| 🔒 登入保護 | 聊天功能需輸入帳密才能使用（電影瀏覽公開） |

## 📁 專案結構

```
├── app.py                 # Streamlit 主程式
├── requirements.txt       # 相依套件
├── movies.json            # 電影資料
├── images/                # 封面圖片
├── config.json            # 金鑰設定（不提交）
└── .streamlit/
    └── secrets.toml       # Streamlit secrets（不提交）
```

## 📋 待辦事項

- [ ] 測試聊天功能在 Streamlit Cloud 上是否正常運作
- [ ] 調整 NVIDIA API timeout（目前設 120 秒，視網路狀況調整）
- [ ] 美化電影卡片 UI（更接近原版設計）
- [ ] 加入電影詳情彈窗（目前使用 st.popover）
- [ ] 考慮加入記憶對話歷史（API 端）
- [ ] 壓力測試：多使用者同時使用時的效能

## 📜 原始專案

Scrape Center 爬蟲練習 — https://ssr1.scrape.center/
