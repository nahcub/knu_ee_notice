import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
NOTICE_URL = "https://see.knu.ac.kr/content/board/notice.html"
STATE_FILE = "seen_notices.txt"

def get_notices():
    res = requests.get(NOTICE_URL)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")
    notices = soup.select("table tbody tr")

    results = []
    for row in notices:
        link_tag = row.select_one("td:nth-child(2) a")
        if not link_tag:
            continue
        title = link_tag.text.strip()
        href = link_tag["href"]
        if not href.startswith("http"):
            href = "https://see.knu.ac.kr" + href
        notice_id = href.split("no=")[-1]
        results.append((notice_id, title, href))
    return results

def load_seen_ids():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_seen_ids(ids):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(ids))

def send_telegram_message(new_notices):
    if not new_notices:
        return
    bot = Bot(token=BOT_TOKEN)
    msg = "📢 <b>새로운 공지사항</b>\n\n"
    for _, title, link in new_notices:
        msg += f"• <a href='{link}'>{title}</a>\n"
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")


if __name__ == "__main__":
    today_notices = fetch_today_notices()

    # 테스트용 코드: 새 공지가 없어도 테스트 메시지 발송
    if not today_notices:
        today_notices = [("테스트 메시지 (공지 없음)", NOTICE_URL)]

    send_telegram(today_notices)