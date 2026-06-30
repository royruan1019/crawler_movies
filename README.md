# 🎬 Scrape Movies — Streamlit 版本

[ssr1.scrape.center](https://ssr1.scrape.center/) 爬蟲練習案的電影目錄，改寫為 **Streamlit** 應用，整合 **DeepSeek V4 Flash** 聊天機器人（透過 NVIDIA NIM API），需登入才能使用聊天功能。

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
