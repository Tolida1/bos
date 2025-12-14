import re
import json
from playwright.sync_api import sync_playwright

START = 267
END = 300

OUTPUT_FILE = "bosssports.json"
THUMB = "https://i.hizliresim.com/gm27zjl.png"

items = []


def save_item(title, m3u8, site, time_text):
    items.append({
        "service": "iptv",
        "title": title,
        "playlistURL": "",
        "media_url": m3u8,
        "url": m3u8,
        "h1Key": "accept",
        "h1Val": "*/*",
        "h2Key": "referer",
        "h2Val": site,
        "h3Key": "origin",
        "h3Val": site.rstrip("/"),
        "h4Key": "0",
        "h4Val": "0",
        "h5Key": "0",
        "h5Val": "0",
        "thumb_square": THUMB,
        "group": time_text
    })


def scrape_site(site):
    print(f"🔍 Taranıyor: {site}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()

        try:
            page.goto(site, timeout=30000, wait_until="domcontentloaded")
        except:
            print("❌ Ana sayfa açılamadı")
            browser.close()
            return

        matches = page.locator("[data-watch]")
        count = matches.count()

        if count == 0:
            print("❌ Maç bulunamadı")
            browser.close()
            return

        for i in range(count):
            try:
                m = matches.nth(i)

                title = m.inner_text(timeout=3000).strip()
                match_id = m.get_attribute("data-watch")

                if not match_id:
                    continue

                time_el = m.locator(".channel-status, .match-time")
                time_text = time_el.inner_text().strip() if time_el.count() else ""

                play_url = f"{site}/play.html?b=1&_3={match_id}"

                p2 = browser.new_page()
                p2.goto(play_url, timeout=30000, wait_until="domcontentloaded")

                html = p2.content()
                p2.close()

                r = re.search(r"https://[^\"']+/playlist\.m3u8", html)
                if not r:
                    print(f"❌ M3U8 yok: {title}")
                    continue

                m3u8 = r.group(0)
                print(f"✅ {title} → {m3u8}")

                save_item(title, m3u8, site, time_text)

            except Exception as e:
                print(f"⚠️ Atlandı: {e}")
                continue

        browser.close()


# 🔁 Site taraması
for i in range(START, END + 1):
    site = f"https://bosssports{i}.com"
    scrape_site(site)


# 💾 JSON yaz
output = {
    "list": {
        "service": "iptv",
        "title": "iptv",
        "item": items
    }
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n🎯 {OUTPUT_FILE} oluşturuldu ({len(items)} kayıt)")
