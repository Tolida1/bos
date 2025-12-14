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

container = soup.find("div", id="pills-tabContent")
items = []
seen = set()

if container:
    for a in container.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#"):
            continue

        full_url = urljoin(BASE_SITE, href)
        if full_url in seen:
            continue
        seen.add(full_url)

        text = a.get_text(" ", strip=True)

        time_match = re.search(r"\b\d{1,2}:\d{2}\b", text)
        match_time = time_match.group(0) if time_match else ""

        title = re.sub(r"\b\d{1,2}:\d{2}\b", "", text).strip()
        if not title:
            continue

        items.append({
            "title": title,
            "group": match_time,
            "url": full_url
        })

output = {
    "list": {
        "service": "iptv",
        "title": "bosssports",
        "item": items
    }
}

with open("bosssports.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"OK → {len(items)} kayıt")
