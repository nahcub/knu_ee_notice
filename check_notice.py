import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
NOTICE_URL = "https://see.knu.ac.kr/content/board/notice.html"

def fetch_today_notices():
    today_kst = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d")
    res = requests.get(NOTICE_URL, timeout=15)
    res.raise_for_status()
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("table tbody tr")

    notices = []
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 4:
            continue
        link_tag = tds[1].find("a")
        date_text = tds[3].get_text(strip=True)
        if not link_tag or not date_text:
            continue
        if date_text == today_kst:
            title = link_tag.get_text(strip=True)
            href = link_tag.get("href", "").strip()
            if href and not href.startswith("http"):
                href = "https://see.knu.ac.kr" + href
            notices.append((title, href))
    return notices

def send_telegram(notices):
    if not notices:
        text = "✅ 오늘은 새로운 공지가 없습니다."
    else:
        text = "📢 <b>오늘의 새로운 공지사항</b>\n\n"
        for title, link in notices:
            text += f"• <a href='{link}'>{title}</a>\n"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, data=data)
    print("Telegram response:", response.text)

if __name__ == "__main__":
    today_notices = fetch_today_notices()
    send_telegram(today_notices)
