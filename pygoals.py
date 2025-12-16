import requests
import json
import re
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

# 1️⃣ ÇALIŞAN BOSSSPORTS SİTESİNİ BUL
def find_base_site():
    for i in range(276, 301):
        url = f"https://bosssports{i}.com/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=5)
            if r.status_code == 200 and "pills-football" in r.text:
                print(f"✅ Aktif site bulundu: {url}")
                return url
        except:
            pass
    return None


# 2️⃣ GERÇEK M3U8 ÇÖZ
def resolve_m3u8(base_site, watch_id, token_2):
    try:
        x_url = f"{base_site}x?id={watch_id}"
        r = requests.get(x_url, headers=HEADERS, timeout=6)
        data = r.json()

        rx = data[0][0]
        if not rx:
            return None

        return f"https://{rx}/{token_2}/-/{watch_id}/playlist.m3u8"
    except:
        return None


# 3️⃣ ANA İŞLEM
def main():
    base_site = find_base_site()
    if not base_site:
        print("❌ Aktif bosssports sitesi bulunamadı")
        return

    r = requests.get(base_site, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    football = soup.find("div", id="pills-football")
    if not football:
        print("❌ pills-football bulunamadı")
        return

    items = []
    seen = set()

    for block in football.select(".match-block"):
        watch_id = block.get("data-watch")
        if not watch_id or watch_id in seen:
            continue
        seen.add(watch_id)

        teams = block.select(".team .name")
        if len(teams) < 2:
            continue

        title = f"{teams[0].text.strip()} - {teams[1].text.strip()}"

        time_div = block.find("div", class_="time")
        match_time = time_div.text.strip() if time_div else ""

        # play.html linkini üret
        play_url = f"{base_site}play.html?_3={watch_id}"
        play_html = requests.get(play_url, headers=HEADERS).text

        token_2_match = re.search(r"_2=([a-zA-Z0-9]+)", play_html)
        if not token_2_match:
            continue

        token_2 = token_2_match.group(1)

        m3u8 = resolve_m3u8(base_site, watch_id, token_2)
        if not m3u8:
            continue

        items.append({
            "service": "iptv",
            "title": title,
            "playlistURL": "",
            "media_url": m3u8,
            "url": m3u8,
            "h1Key": "accept",
            "h1Val": "*/*",
            "h2Key": "referer",
            "h2Val": base_site,
            "h3Key": "origin",
            "h3Val": base_site.rstrip("/"),
            "h4Key": "0",
            "h4Val": "0",
            "h5Key": "0",
            "h5Val": "0",
            "thumb_square": "https://i.hizliresim.com/gm27zjl.png",
            "group": match_time
        })

        print(f"✔ {title} [{match_time}]")

    output = {
        "list": {
            "service": "iptv",
            "title": "iptv",
            "item": items
        }
    }

    with open("bosssports.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 bosssports.json oluşturuldu ({len(items)} kayıt)")


if __name__ == "__main__":
    main()
