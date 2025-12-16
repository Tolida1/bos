import requests
import json
from bs4 import BeautifulSoup

# ==================================================
# TAM USER-AGENT (GERÇEK TARAYICI)
# ==================================================
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

# ==================================================
# 1️⃣ AKTİF BOSSSPORTS SİTESİNİ BUL
# ==================================================
def find_active_site(start=276, end=300):
    for i in range(start, end + 1):
        url = f"https://bosssports{i}.com/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=6)
            if r.status_code == 200 and "match-list" in r.text:
                print(f"✅ Aktif site bulundu: {url}")
                return url.rstrip("/")
        except:
            pass
    return None


BASE_SITE = find_active_site()
if not BASE_SITE:
    print("❌ Aktif BossSports sitesi bulunamadı")
    exit()

REFERER = BASE_SITE + "/"
ORIGIN = BASE_SITE

# ==================================================
# 2️⃣ ANA SAYFAYI ÇEK
# ==================================================
r = requests.get(BASE_SITE, headers=HEADERS, timeout=10)
soup = BeautifulSoup(r.text, "html.parser")

football_tab = soup.find("div", id="pills-football")
if not football_tab:
    print("❌ Football tab bulunamadı")
    exit()

items = []

# ==================================================
# 3️⃣ MAÇLARI + M3U8 LİNKLERİNİ ÇEK
# ==================================================
for block in football_tab.find_all("div", class_="match-block"):
    teams = block.find_all("div", class_="name")
    time_div = block.find("div", class_="time")
    watch_id = block.get("data-watch")

    if len(teams) < 2 or not time_div or not watch_id:
        continue

    title = f"{teams[0].text.strip()} - {teams[1].text.strip()}"
    match_time = time_div.text.strip()

    m3u8_links = []

    try:
        rx = requests.get(
            f"{BASE_SITE}/x?id={watch_id}",
            headers=HEADERS,
            timeout=8
        ).json()

        if isinstance(rx, list):
            for row in rx:
                if (
                    isinstance(row, list)
                    and row
                    and isinstance(row[0], str)
                    and row[0].startswith("bo.")
                    and row[0].endswith(".workers.dev")
                ):
                    m3u8_links.append(
                        f"https://{row[0]}/{watch_id}/playlist.m3u8"
                    )
    except:
        pass

    if not m3u8_links:
        continue

    # ==================================================
    # 4️⃣ JSON ITEM (HEADER'LAR TAM VE OTOMATİK)
    # ==================================================
    items.append({
        "service": "iptv",
        "title": title,
        "playlistURL": "",
        "media_url": m3u8_links[0],
        "url": m3u8_links[0],

        "h1Key": "user-agent",
        "h1Val": USER_AGENT,

        "h2Key": "referer",
        "h2Val": REFERER,

        "h3Key": "origin",
        "h3Val": ORIGIN,

        "h4Key": "accept",
        "h4Val": "*/*",

        "backup_links": m3u8_links[1:],
        "thumb_square": "https://i.hizliresim.com/gm27zjl.png",
        "group": match_time
    })

    print(f"✔ {title} [{match_time}] → {len(m3u8_links)} link")

# ==================================================
# 5️⃣ JSON YAZ
# ==================================================
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
