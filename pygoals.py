from playwright.sync_api import sync_playwright
import json
import time

START_DOMAIN = 267
END_DOMAIN = 300

THUMB = "https://i.hizliresim.com/gm27zjl.png"

items = []

def scrape_site(base_url: str):
    print(f"🔍 Taranıyor: {base_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(base_url, timeout=60000)
            page.wait_for_selector(".match-block", timeout=15000)
        except:
            print("❌ Ana sayfa yüklenemedi")
            browser.close()
            return

        matches = page.query_selector_all(".match-block")

        for m in matches:
            match_id = m.get_attribute("data-watch")
            teams = m.query_selector_all(".name")
            time_div = m.query_selector(".time")

            if not match_id or len(teams) < 2 or not time_div:
                continue

            title = f"{teams[0].inner_text()} - {teams[1].inner_text()}"
            match_time = time_div.inner_text()

            play_url = f"{base_url}/play.html?b=1&_3={match_id}"

            m3u8_url = None

            def catch_response(resp):
                nonlocal m3u8_url
                if "playlist.m3u8" in resp.url:
                    m3u8_url = resp.url

            page.on("response", catch_response)

            try:
                page.goto(play_url, timeout=60000)
                page.wait_for_timeout(4000)
            except:
                continue

            if not m3u8_url:
                print(f"❌ M3U8 yok: {title}")
                continue

            items.append({
                "service": "iptv",
                "title": title,
                "playlistURL": "",
                "media_url": m3u8_url,
                "url": m3u8_url,
                "h1Key": "accept",
                "h1Val": "*/*",
                "h2Key": "referer",
                "h2Val": base_url + "/",
                "h3Key": "origin",
                "h3Val": base_url,
                "h4Key": "0",
                "h4Val": "0",
                "h5Key": "0",
                "h5Val": "0",
                "thumb_square": THUMB,
                "group": match_time
            })

            print(f"✅ {title} | {match_time}")

            page.remove_listener("response", catch_response)

        browser.close()


# 🔁 DOMAIN DÖNGÜSÜ
for i in range(START_DOMAIN, END_DOMAIN + 1):
    site = f"https://bosssports{i}.com"
    scrape_site(site)

# 💾 JSON YAZ
output = {
    "list": {
        "service": "iptv",
        "title": "bosssports",
        "item": items
    }
}

with open("bosssports.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n🎯 TAMAMLANDI | Toplam {len(items)} yayın bulundu")
