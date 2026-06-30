import json
import re
import secrets
import httpx
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

config = json.loads(Path("config.json").read_text(encoding="utf-8"))

DEEPSEEK_API_KEY = config["deepseek"]["api_key"]
DEEPSEEK_BASE_URL = config["deepseek"]["base_url"]
DEEPSEEK_MODEL = config["deepseek"]["model"]
USERS = {u["username"]: u["password"] for u in config["users"]}

sessions: set[str] = set()

movies = json.loads(Path("movies.json").read_text(encoding="utf-8"))
by_id = {m["id"]: m for m in movies}
all_categories = sorted(set(c for m in movies for c in m["categories"]))

pages = {}
for m in movies:
    pg = (m["id"] - 1) // 10 + 1
    pages.setdefault(pg, []).append(m)

app = FastAPI(title="Scrape Movies")
app.mount("/images", StaticFiles(directory="images"), name="images")

env = Environment(loader=FileSystemLoader("templates"), auto_reload=False, cache_size=0)


def render(name, **ctx):
    tpl = env.get_template(name)
    return HTMLResponse(tpl.render(**ctx))


def filter_movies(q: str = "", cat: str = "", pg: int = 0):
    result = movies
    if q:
        ql = q.lower()
        result = [m for m in result if
                  ql in m["name"].lower() or
                  ql in " ".join(m["categories"]).lower() or
                  ql in m["region"].lower() or
                  ql in str(m["score"]) or
                  ql in m.get("summary", "").lower()]
    if cat:
        result = [m for m in result if cat in m["categories"]]
    total = len(result)
    per_page = 30
    total_pages = max(1, (total + per_page - 1) // per_page)
    if pg < 1:
        pg = 1
    if pg > total_pages:
        pg = total_pages
    start = (pg - 1) * per_page
    end = start + per_page
    page_items = result[start:end]
    return page_items, total, total_pages, pg


def require_auth(request: Request):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    if token not in sessions:
        raise HTTPException(status_code=401, detail="請先登入")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, q: str = "", cat: str = "", pg: int = 1):
    items, total, total_pages, cur_page = filter_movies(q, cat, pg)
    return render("index.html",
                  movies=items, total=total,
                  page=cur_page, total_pages=total_pages,
                  q=q, cat=cat, categories=all_categories,
                  movies_json=json.dumps(movies, ensure_ascii=False))


@app.get("/page/{pg}", response_class=HTMLResponse)
async def page_view(request: Request, pg: int):
    data = pages.get(pg, [])
    return render("page.html", movies=data, page=pg, total=len(pages))


@app.get("/detail/{mid}", response_class=HTMLResponse)
async def detail_view(request: Request, mid: int):
    m = by_id.get(mid)
    if not m:
        return HTMLResponse("Not Found", status_code=404)
    return render("detail.html", m=m, categories=all_categories)


@app.post("/api/login")
async def login(request: Request):
    body = await request.json()
    username = body.get("username", "").strip()
    password = body.get("password", "").strip()
    if USERS.get(username) != password:
        return JSONResponse({"ok": False, "error": "帳號或密碼錯誤"}, status_code=401)
    token = secrets.token_hex(32)
    sessions.add(token)
    return JSONResponse({"ok": True, "token": token})


@app.post("/api/logout")
async def logout(request: Request):
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    sessions.discard(token)
    return JSONResponse({"ok": True})


@app.post("/api/chat")
async def chat_api(request: Request):
    try:
        require_auth(request)
    except HTTPException:
        return JSONResponse({"reply": "🔒 請先登入才能使用聊天功能"}, status_code=401)

    body = await request.json()
    msg = body.get("message", "").strip()
    if not msg:
        return JSONResponse({"reply": "請輸入問題"})

    system_prompt = (
        "你是一個專業的電影助手，擅長回答關於電影的各種問題，包括推薦、評分、劇情、演員等。"
        "請用繁體中文回答，盡量簡潔有幫助。"
    )

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": msg},
                    ],
                    "stream": False,
                },
            )
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse({"reply": f"⚠️ 連線錯誤：{str(e)}"})
