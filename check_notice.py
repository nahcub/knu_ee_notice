import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
NOTICE_URL = "https://see.knu.ac.kr/content/board/notice.html"

print("BOT_TOKEN prefix:", BOT_TOKEN[:10])
print("CHAT_ID:", CHAT_ID)

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

        # 오늘 날짜 공지만 가져오기
        if date_text == today_kst:
            title = link_tag.get_text(strip=True)
            href = link_tag.get("href", "").strip()
            if href and not href.startswith("http"):
                href = "https://see.knu.ac.kr" + href
            notices.append((title, href))
    return notices

def send_telegram(notices):
    if not notices:
        return
    bot = Bot(token=BOT_TOKEN)
    msg = "📢 <b>오늘의 새로운 공지사항</b>\n\n"
    for title, link in notices:
        msg += f"• <a href='{link}'>{title}</a>\n"
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")

if __name__ == "__main__":
    today_notices = fetch_today_notices()

    # ✅ 테스트용: 오늘 공지가 없더라도 메시지 한 번 보내기
    if not today_notices:
        today_notices = [("테스트 메시지 (공지 없음)", NOTICE_URL)]

    send_telegram(today_notices)
