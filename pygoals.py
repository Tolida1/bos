import requests
import json
from bs4 import BeautifulSoup

# ==============================
# TAM USER-AGENT
# ==============================
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Connection": "keep-alive"
}

# ==============================
# 1️⃣ AKTİF BOSSSPORTS BUL
# ==============================
def find_active_site(start=267, end=300):
    for i in range(start, end + 1):
        url = f"https://bosssports{i}.com/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=6)
            if r.status_code == 200 and "match-list" in r.text:
                print(f"✅ Aktif site: {url}")
                return url.rstrip("/")
        except:
            pass
    return None

BASE_SITE = find_active_site()
if not BASE_SITE:
    print("❌ Aktif BossSports bulunamadı")
    exit()

REFERER = BASE_SITE + "/"
ORIGIN = BASE_SITE

# ==============================
# 2️⃣ ANA SAYFA
# ==============================
html = requests.get(BASE_SITE, headers=HEADERS, timeout=10).text
soup = BeautifulSoup(html, "html.parser")

football_tab = soup.find("div", id="pills-football")
if not football_tab:
    print("❌ Football tab yok")
    exit()

items = []

# ==============================
# 3️⃣ MAÇLAR
# ==============================
for block in football_tab.find_all("div", class_="match-block"):
    teams = block.find_all("div", class_="name")
    time_div = block.find("div", class_="time")
    watch_id = block.get("data-watch")

    if len(teams) < 2 or not time_div or not watch_id:
        continue

    title = f"{teams[0].text.strip()} - {teams[1].text.strip()}"
    match_time = time_div.text.strip()

    real_links = []

    # ==============================
    # 4️⃣ DOMAINLERİ AL
    # ==============================
    try:
        rx = requests.get(
            f"{BASE_SITE}/x?id={watch_id}",
            headers=HEADERS,
            timeout=8
        ).json()
    except:
        continue

    if not isinstance(rx, list):
        continue

    for row in rx:
        if not row or not isinstance(row[0], str):
            continue

        domain = row[0]

        # ==============================
        # 5️⃣ OLASI YOLLAR (SIRAYLA)
        # ==============================
        probe_paths = [
            f"https://{domain}/{watch_id}/playlist.m3u8",                 # YENİ (en sık)
            f"https://{domain}/-/{watch_id}/playlist.m3u8",               # ARA
            f"https://{domain}/f6e33e69e0fdec0a7780e174f3c8b2c2/-/{watch_id}/playlist.m3u8",  # ESKİ
        ]

        for probe_url in probe_paths:
            try:
                r = requests.get(
                    probe_url,
                    headers=HEADERS,
                    timeout=8,
                    allow_redirects=True
                )

                # ✅ REDIRECT SONRASI GERÇEK URL
                if r.status_code == 200 and r.url.endswith("playlist.m3u8"):
                    real_links.append(r.url)
                    break  # bu domain için yeterli
            except:
                pass

    if not real_links:
        continue

    # ==============================
    # 6️⃣ JSON ITEM (HEADER'LAR TAM)
    # ==============================
    items.append({
        "service": "iptv",
        "title": title,
        "playlistURL": "",
        "media_url": real_links[0],
        "url": real_links[0],
        "backup_links": real_links[1:],

        "h1Key": "user-agent",
        "h1Val": USER_AGENT,

        "h2Key": "referer",
        "h2Val": REFERER,

        "h3Key": "origin",
        "h3Val": ORIGIN,

        "h4Key": "accept",
        "h4Val": "*/*",

        "group": match_time
    })

    print(f"✔ {title} → {len(real_links)} gerçek link")

# ==============================
# 7️⃣ JSON YAZ
# ==============================
output = {
    "list": {
        "service": "iptv",
        "title": "BossSports",
        "item": items
    }
}

with open("bosssports.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n🎯 bosssports.json oluşturuldu ({len(items)} maç)")
