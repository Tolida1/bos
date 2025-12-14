import requests
import json
from bs4 import BeautifulSoup

BASE_SITE = "https://bosssports268.com/"
CHANNEL_URL = BASE_SITE + "channel.html?id={}"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE_SITE
}

r = requests.get(BASE_SITE, headers=headers, timeout=20)
soup = BeautifulSoup(r.text, "html.parser")

items = []
seen = set()

# ✅ FUTBOL TAB'I
football_tab = soup.find("div", id="pills-football")
if not football_tab:
    print("❌ pills-football bulunamadı")
else:
    for block in football_tab.find_all("div", class_="match-block"):
        watch_id = block.get("data-watch")
        if not watch_id:
            continue

        # ⏰ Saat
        time_div = block.find("div", class_="time")
        match_time = time_div.get_text(strip=True) if time_div else ""

        # 👥 Takımlar
        teams = block.find_all("div", class_="name")
        if len(teams) < 2:
            continue

        team1 = teams[0].get_text(strip=True)
        team2 = teams[1].get_text(strip=True)

        title = f"{team1} - {team2}"

        # 🔁 Aynı maç + saat tekrarını engelle
        uniq_key = f"{watch_id}_{match_time}"
        if uniq_key in seen:
            continue
        seen.add(uniq_key)

        items.append({
            "service": "iptv",
            "title": title,
            "playlistURL": "",
            "media_url": "",
            "url": CHANNEL_URL.format(watch_id),
            "group": match_time
        })

print(f"✔ Bulunan maç sayısı: {len(items)}")

output = {
    "list": {
        "service": "iptv",
        "title": "bosssports",
        "item": items
    }
}

with open("bosssports.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("🎯 bosssports.json başarıyla oluşturuldu")
