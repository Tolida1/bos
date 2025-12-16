import requests
import json
from bs4 import BeautifulSoup

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

# --------------------------------------------------
# 1️⃣ Aktif BossSports domainini bul
# --------------------------------------------------
def find_active_site(start=267, end=300):
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

# --------------------------------------------------
# 2️⃣ Ana sayfayı al
# --------------------------------------------------
soup = BeautifulSoup(
    requests.get(BASE_SITE, headers=HEADERS, timeout=10).text,
    "html.parser"
)

football_tab = soup.find("div", id="pills-football")
if not football_tab:
    print("❌ Football tab bulunamadı")
    exit()

items = []

# --------------------------------------------------
# 3️⃣ MAÇLAR
# --------------------------------------------------
for block in football_tab.find_all("div", class_="match-block"):
    teams = block.find_all("div", class_="name")
    time_div = block.find("div", class_="time")
    watch_id = block.get("data-watch")

    if len(teams) < 2 or not time_div or not watch_id:
        continue

    title = f"{teams[0].text.strip()} - {teams[1].text.strip()}"
    match_time = time_div.text.strip()

    real_links = []

    # --------------------------------------------------
    # 4️⃣ DOMAIN + GERÇEK PATH ÇÖZ
    # --------------------------------------------------
    try:
        rx = requests.get(
            f"{BASE_SITE}/x?id={watch_id}",
            headers=HEADERS,
            timeout=8
        ).json()

        for row in rx:
            domain = row[0]

            # 🔑 eski yol SADECE tetiklemek için
            probe_url = f"https://{domain}/f6e33e69e0fdec0a7780e174f3c8b2c2/-/{watch_id}/playlist.m3u8"

            r = requests.get(
                probe_url,
                headers=HEADERS,
                timeout=8,
                allow_redirects=True
            )

            # ✅ GERÇEK URL (redirect sonrası)
            if r.status_code == 200 and "playlist.m3u8" in r.url:
                real_links.append(r.url)

    except Exception as e:
        print("Çözüm hatası:", e)

    if not real_links:
        continue

    # --------------------------------------------------
    # 5️⃣ JSON ITEM
    # --------------------------------------------------
    items.append({
        "service": "iptv",
        "title": title,
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

    print(f"✔ {title} → gerçek link bulundu")

# --------------------------------------------------
# 6️⃣ JSON YAZ
# --------------------------------------------------
with open("bosssports.json", "w", encoding="utf-8") as f:
    json.dump({
        "list": {
            "service": "iptv",
            "title": "BossSports",
            "item": items
        }
    }, f, ensure_ascii=False, indent=2)

print(f"\n🎯 bosssports.json oluşturuldu ({len(items)} maç)")
