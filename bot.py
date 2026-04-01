import telebot
import feedparser
import requests
from bs4 import BeautifulSoup
import time
import json
import os
import random
import re

# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")

try:
    CHANNEL = int(CHANNEL)
except:
    pass

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# ==========================
RSS_FEEDS = [
    "https://www.aljazeera.net/aljazeera/ar/feeds/all.xml",
    "https://feeds.bbci.co.uk/arabic/rss.xml"
]

DATA_FILE = "posted.json"

# ==========================
def load_posted():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_posted(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

posted = load_posted()

# ==========================
def clean(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ==========================
def get_image(entry):
    if "media_content" in entry:
        return entry.media_content[0]["url"]
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0]["url"]
    return None

# ==========================
def extract_summary(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        paragraphs = []
        seen = set()

        # BBC
        for p in soup.select("div[data-component='text-block'] p"):
            txt = clean(p.get_text())
            if len(txt) > 50 and txt not in seen:
                paragraphs.append(txt)
                seen.add(txt)

        # الجزيرة
        if not paragraphs:
            for p in soup.select("article p"):
                txt = clean(p.get_text())
                if len(txt) > 50 and txt not in seen:
                    paragraphs.append(txt)
                    seen.add(txt)

        # أخذ فقط 5–7 فقرات
        summary = "\n".join(paragraphs[:6])

        return summary

    except:
        return None

# ==========================
def emoji():
    return random.choice(["🔥","⚡","🌍","📰"])

# ==========================
def format_news(title, summary):
    return f"""*{emoji()} {title}*

{summary}
"""

# ==========================
def post_news():
    global posted

    for feed in RSS_FEEDS:
        data = feedparser.parse(feed)

        for entry in data.entries[:5]:
            key = entry.title.lower()

            if key in posted:
                continue

            try:
                summary = extract_summary(entry.link)
                if not summary:
                    continue

                img = get_image(entry)
                message = format_news(entry.title, summary)

                if img:
                    bot.send_photo(CHANNEL, img, caption=message[:1000])
                else:
                    bot.send_message(CHANNEL, message[:4000])

                print("✅ SHORT NEWS POSTED")

                posted.append(key)
                if len(posted) > 300:
                    posted = posted[-300:]

                save_posted(posted)
                break

            except Exception as e:
                print("Error:", e)

# ==========================
print("🚀 SHORT NEWS BOT RUNNING...")

while True:
    post_news()
    time.sleep(60)