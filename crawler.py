import requests
import json
import re
import time
import os

BASE_URL = "https://ssr1.scrape.center"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
IMAGE_DIR = "images"


def fetch_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
    resp.encoding = "utf-8"
    return resp.text


def parse_list(html):
    items = html.split('<div data-v-7f856186="" class="el-card item m-t is-hover-shadow">')[1:]
    movies = []
    for item in items:
        item = item.split('</div>\n        </div>\n      </div>')[0]
        detail_path = re.search(r'href="(/detail/\d+)"', item).group(1)
        name = re.search(r'<h2[^>]*>(.*?)</h2>', item).group(1)
        categories = re.findall(r'<button[^>]*>\s*<span>(.*?)</span>\s*</button>', item)
        info = re.findall(r'<span data-v-7f856186="">(.*?)</span>', item)
        region = info[0] if len(info) > 0 else ""
        duration = info[2] if len(info) > 2 else ""
        release = re.search(r'(\d{4}-\d{2}-\d{2}) 上映', item)
        release = release.group(1) if release else ""
        score = re.search(r'class="score[^"]*">\s*([\d.]+)', item)
        score = score.group(1) if score else ""
        cover = re.search(r'src="(.*?)"', item)
        cover = cover.group(1) if cover else ""
        movies.append({
            "id": int(detail_path.split("/")[-1]),
            "name": name,
            "categories": categories,
            "region": region,
            "duration": duration,
            "release": release,
            "score": float(score) if score else 0,
            "cover": cover,
            "detail_url": BASE_URL + detail_path
        })
    return movies


def parse_detail(html):
    summary = re.search(r'<p data-v-63864230="">\n\s*(.*?)\n\s*</p></div>', html, re.S)
    summary = summary.group(1).strip() if summary else ""
    return {"summary": summary}


def download_image(url, filepath):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"    圖片下載失敗: {e}")
    return False


def main():
    requests.packages.urllib3.disable_warnings()
    all_movies = []
    total_pages = 11
    for page in range(1, total_pages + 1):
        print(f"正在爬取第 {page} 頁...")
        html = fetch_page(f"{BASE_URL}/page/{page}")
        movies = parse_list(html)
        all_movies.extend(movies)
        time.sleep(0.5)
    print(f"列表頁爬取完成，共 {len(all_movies)} 部電影")
    os.makedirs(IMAGE_DIR, exist_ok=True)
    for i, m in enumerate(all_movies, 1):
        print(f"  正在爬取詳情 ({i}/{len(all_movies)}): {m['id']}")
        html = fetch_page(m["detail_url"])
        detail = parse_detail(html)
        m["summary"] = detail["summary"]
        ext = os.path.splitext(m["cover"].split("@")[0])[1] or ".jpg"
        img_path = os.path.join(IMAGE_DIR, f"{m['id']}{ext}")
        if not os.path.exists(img_path):
            download_image(m["cover"], img_path)
        m["image_file"] = img_path
        time.sleep(0.3)
    with open("movies.json", "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=2)
    print(f"已儲存 {len(all_movies)} 部電影到 movies.json")


if __name__ == "__main__":
    main()
