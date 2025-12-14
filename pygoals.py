import json
from playwright.sync_api import sync_playwright

BASE_SITE = "https://bosssports268.com/"
CHANNEL_URL = BASE_SITE + "channel.html?id={}"

items = []
seen = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(BASE_SITE, timeout=60000)

    # ⏳ JS YÜKLENSİN
    page.wait_for_selector("#pills-football .match-block", timeout=60000)

    blocks = page.query_selector_all("#pills-football .match-block")

    for block in blocks:
        watch_id = block.get_attribute("data-watch")
        if not watch_id:
            continue

        time_el = block.query_selector(".time")
        match_time = time_el.inner_text().strip() if time_el else ""

        teams = block.query_selector_all(".team .name")
        if len(teams) < 2:
            continue

        team1 = teams[0].inner_text().strip()
        team2 = teams[1].inner_text().strip()

        title = f"{team1} - {team2}"
        uniq = f"{watch_id}_{match_time}"
        if uniq in seen:
            continue
        seen.add(uniq)

        items.append({
            "service": "iptv",
            "title": title,
            "playlistURL": "",
            "media_url": "",
            "url": CHANNEL_URL.format(watch_id),
            "group": match_time
        })

    browser.close()

print(f"✔ Playwright ile bulunan maç: {len(items)}")

output = {
    "list": {
        "service": "iptv",
        "title": "bosssports",
        "item": items
    }
}

with open("bosssports.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
