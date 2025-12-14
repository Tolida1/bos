from playwright.sync_api import sync_playwright
import json
import time

SITE = "bosssports268.com"
RESULT = []

def extract_m3u8(page, watch_id):
    m3u8s = set()

    def on_response(resp):
        if "playlist.m3u8" in resp.url:
            m3u8s.add(resp.url)

    page.on("response", on_response)

    page.goto(
        f"https://{SITE}/play.html?b=1&_3={watch_id}",
        wait_until="networkidle",
        timeout=60000
    )

    time.sleep(3)
    page.off("response", on_response)

    return list(m3u8s)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    print(f"🔍 Site açılıyor: https://{SITE}")
    page.goto(f"https://{SITE}", wait_until="domcontentloaded", timeout=60000)

    matches = page.locator("div.match-block").all()

    for m in matches:
        try:
            watch_id = m.get_attribute("data-watch")
            teams = m.locator(".name").all_text_contents()
            match_time = m.locator(".time").inner_text()
            title = " - ".join(teams)

            print(f"🎯 {title} ({watch_id})")

            m3u8_links = extract_m3u8(page, watch_id)

            for m3u8 in m3u8_links:
                RESULT.append({
                    "service": "iptv",
                    "title": title,
                    "playlistURL": "",
                    "media_url": m3u8,
                    "url": m3u8,
                    "h1Key": "accept",
                    "h1Val": "*/*",
                    "h2Key": "referer",
                    "h2Val": f"https://{SITE}/",
                    "h3Key": "origin",
                    "h3Val": f"https://{SITE}",
                    "thumb_square": "https://i.hizliresim.com/gm27zjl.png",
                    "group": match_time
                })

            if not m3u8_links:
                print("❌ m3u8 bulunamadı")

        except Exception as e:
            print("⚠️ Hata:", e)

    browser.close()

final_json = {
    "list": {
        "service": "iptv",
        "title": "iptv",
        "item": RESULT
    }
}

with open("bosssports.json", "w", encoding="utf-8") as f:
    json.dump(final_json, f, ensure_ascii=False, indent=2)

print(f"✅ Toplam m3u8: {len(RESULT)}")
