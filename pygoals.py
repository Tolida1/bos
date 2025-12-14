import json
from playwright.sync_api import sync_playwright

BASE_SITE = "https://bosssports268.com/"
PLAY_TEMPLATE = "https://bosssports268.com/play.html?b=1&_1=bo.096f27bf2d8048091c.workers.dev&_2=f6e33e69e0fdec0a7780e174f3c8b2c2&_3={id}"

items = []
seen = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(BASE_SITE, timeout=60000)
    page.wait_for_selector("#pills-football .match-block", timeout=60000)

    blocks = page.query_selector_all("#pills-football .match-block")

    for block in blocks:
        watch_id = block.get_attribute("data-watch")
        if not watch_id:
            continue

        # saat
        time_el = block.query_selector(".time")
        match_time = time_el.inner_text().strip() if time_el else ""

        # takımlar
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

        play_url = PLAY_TEMPLATE.format(id=watch_id)

        items.append({
            "service": "iptv",
            "title": title,
            "playlistURL": "",
            "media_url": play_url,    # buraya play link
            "url": play_url,          # aynı playuRL
            "group": match_time
        })

    browser.close()

output = {
    "list": {
        "service": "iptv",
        "title": "bosssports",
        "item": items
    }
}

with open("bosssports.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✔ Toplam maç: {len(items)}")
