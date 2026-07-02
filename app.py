import json
import requests
import streamlit as st
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────
DEEPSEEK_API_KEY = DEEPSEEK_BASE_URL = DEEPSEEK_MODEL = None
USERS = {}

if "deepseek" in st.secrets:
    DEEPSEEK_API_KEY = st.secrets["deepseek"]["api_key"]
    DEEPSEEK_BASE_URL = st.secrets["deepseek"]["base_url"]
    DEEPSEEK_MODEL = st.secrets["deepseek"]["model"]
    USERS = dict(st.secrets["users"])
else:
    cfg_path = Path("config.json")
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        DEEPSEEK_API_KEY = cfg["deepseek"]["api_key"]
        DEEPSEEK_BASE_URL = cfg["deepseek"]["base_url"]
        DEEPSEEK_MODEL = cfg["deepseek"]["model"]
        USERS = {u["username"]: u["password"] for u in cfg["users"]}

# ── Data ────────────────────────────────────────────────────────────
@st.cache_data
def load_movies():
    return json.loads(Path("movies.json").read_text(encoding="utf-8"))

movies = load_movies()
all_cats = sorted(set(c for m in movies for c in m["categories"]))

# ── State ──────────────────────────────────────────────────────────
defaults = {
    "auth": False, "msgs": [], "page": 1, "view": "movies",
    "q": "", "cat": "",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


def filter_movies(q, cat, pg, per=30):
    res = movies
    if q:
        ql = q.lower()
        res = [m for m in res if
               ql in m["name"].lower() or
               ql in " ".join(m["categories"]).lower() or
               ql in m["region"].lower() or
               ql in str(m["score"]) or
               ql in m.get("summary", "").lower()]
    if cat:
        res = [m for m in res if cat in m["categories"]]
    total = len(res)
    tp = max(1, (total + per - 1) // per)
    pg = max(1, min(pg, tp))
    s = (pg - 1) * per
    return res[s:s + per], total, tp


# ── UI ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Scrape Movies", page_icon="🎬", layout="wide")
st.markdown("""
<style>
.m-card { background:#fff; border-radius:10px; padding:0; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,.08); margin-bottom:16px }
.m-card img { width:100%; height:270px; object-fit:cover }
.m-body { padding:8px 12px 12px }
.m-title { font-size:14px; font-weight:600; margin-bottom:4px; line-height:1.3 }
.m-cat { display:inline-block; background:#e8f0fe; color:#1a73e8; font-size:10px; padding:2px 7px; border-radius:4px; margin-right:3px; margin-bottom:3px }
.m-meta { display:flex; justify-content:space-between; font-size:12px; color:#888; margin-top:4px }
.m-score { font-weight:700; color:#fa0; font-size:16px }
.chat-msg { margin-bottom:10px }
.stApp { background:#f5f5f5 }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 Scrape Movies")
    if not st.session_state.auth:
        with st.form("login"):
            st.markdown("### 🔒 登入使用聊天")
            u = st.text_input("帳號")
            p = st.text_input("密碼", type="password")
            if st.form_submit_button("登入", use_container_width=True):
                if u in USERS and USERS[u] == p:
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤")
    else:
        st.success("✅ 已登入")
        c1, c2 = st.columns(2)
        if c1.button("🎬 電影", use_container_width=True, type="primary" if st.session_state.view == "movies" else "secondary"):
            st.session_state.view = "movies"; st.rerun()
        if c2.button("💬 聊天", use_container_width=True, type="primary" if st.session_state.view == "chat" else "secondary"):
            st.session_state.view = "chat"; st.rerun()
        if st.button("🚪 登出", use_container_width=True):
            st.session_state.auth = False; st.session_state.msgs = []; st.rerun()

# ── Chat View ───────────────────────────────────────────────────────
if st.session_state.view == "chat" and st.session_state.auth:
    st.markdown("## 💬 電影小幫手")
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    if prompt := st.chat_input("輸入問題..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("思考中…"):
                try:
                    resp = requests.post(
                        f"{DEEPSEEK_BASE_URL}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": DEEPSEEK_MODEL,
                            "messages": [{"role": "system", "content": "你是電影助手，用繁體中文回答。"},
                                         {"role": "user", "content": prompt}],
                        },
                        timeout=120,
                    )
                    resp.raise_for_status()
                    reply = resp.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    reply = f"⚠️ 錯誤：{e}"
            st.markdown(reply)
            st.session_state.msgs.append({"role": "assistant", "content": reply})

# ── Movies View ─────────────────────────────────────────────────────
else:
    # Search
    q = st.text_input("🔍", placeholder="搜尋電影名稱、分類、產地…", label_visibility="collapsed",
                      value=st.session_state.q)
    if q != st.session_state.q:
        st.session_state.q = q; st.session_state.page = 1; st.rerun()

    # Categories
    cols = st.columns(9)
    for i, c in enumerate([""] + all_cats):
        lbl = "全部" if c == "" else c
        active = c == st.session_state.cat
        if cols[i % 9].button(lbl, key=f"c_{c}", type="primary" if active else "secondary", use_container_width=True):
            st.session_state.cat = c; st.session_state.page = 1; st.rerun()

    items, total, tp = filter_movies(st.session_state.q, st.session_state.cat, st.session_state.page)
    st.markdown(f"<div style='color:#888;margin:8px 0'>共 {total} 筆結果</div>", unsafe_allow_html=True)

    # Grid
    cols = st.columns(4, gap="small")
    for i, m in enumerate(items):
        with cols[i % 4]:
            img = f"images/{m['id']}.jpg"
            nm = m["name"].split(" - ")
            cats = "".join(f"<span class='m-cat'>{c}</span>" for c in m["categories"][:3])
            yr = m["release"][:4] if m["release"] else "—"
            st.markdown(
                f"<div class='m-card'>"
                f"<img src='https://raw.githubusercontent.com/royruan1019/crawler_movies/main/images/{m['id']}.jpg' "
                f"onerror='this.style.display=\"none\"'>"
                f"<div class='m-body'>"
                f"<div class='m-title'>{nm[0]}</div>"
                f"<div>{cats}</div>"
                f"<div class='m-meta'><span>{yr}</span><span class='m-score'>{m['score']}</span></div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )
            with st.popover("詳情", use_container_width=True):
                st.markdown(f"**{m['name']}**")
                st.markdown(f"產地：{m['region']} | 時長：{m['duration']} | 上映：{m['release'] or '—'}")
                if m.get("summary"):
                    st.markdown(f"_{m['summary'][:200]}…_")

    # Pagination
    if tp > 1:
        pg = st.session_state.page
        start = max(1, min(pg - 4, tp - 9))
        end = min(tp, start + 9)
        pages = list(range(start, end + 1))
        cols = st.columns(len(pages) + 2)
        with cols[0]:
            if st.button("◀", disabled=pg <= 1, use_container_width=True):
                st.session_state.page -= 1; st.rerun()
        for i, p in enumerate(pages):
            with cols[i + 1]:
                if st.button(str(p), key=f"p{p}", type="primary" if p == pg else "secondary", use_container_width=True):
                    st.session_state.page = p; st.rerun()
        with cols[-1]:
            if st.button("▶", disabled=pg >= tp, use_container_width=True):
                st.session_state.page += 1; st.rerun()
