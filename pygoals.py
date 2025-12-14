import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_SITE = "https://bosssports268.com/"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE_SITE
}

r = requests.get(BASE_SITE, headers=headers, timeout=20)
soup = BeautifulSoup(r.text, "html.parser")

items = []
seen = set()

# 🔑 TÜM TAB PANE'LERİ TARA
tab_container = soup.find("div", id="pills-tabContent")
if not tab_container:
    print("pills-tabContent yok")
else:
    for pane in tab_container.find_all("div", class_="tab-pane"):
        for a in pane.find_all("a", href=True):
            href = a.get("href", "").strip()
            if not href or href.startswith("#"):
                continue

            full_url = urljoin(BASE_SITE, href)
            if full_url in seen:
                continue
            seen.add(full_url)

            text = a.get_text(" ", strip=True)

            # ⏰ saat
            time_match = re.search(r"\b\d{1,2}:\d{2}\b", text)
            match_time = time_match.group(0) if time_match else ""

            # 🏷️ başlık (saat temiz)
            title = re.sub(r"\b\d{1,2}:\d{2}\b", "", text).strip()
            if not title:
                continue

            items.append({
                "service": "iptv",
                "title": title,
                "playlistURL": "",
                "media_url": "",
                "url": full_url,
                "group": match_time
            })

print(f"Bulunan kayıt: {len(items)}")

output = {
    "list": {
        "service": "iptv",
        "title": "bosssports",
        "item": items
    }
}

with open("bosssports.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
