import telebot
import feedparser
import schedule
import time
import os
import json
import random

# ==========================
# إعدادات البوت
# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = int(os.environ.get("CHANNEL_ID"))

bot = telebot.TeleBot(TOKEN)

# ==========================
# RSS الأخبار
# ==========================
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

# ==========================
# التخزين لتجنب التكرار
# ==========================
DATA_FILE = "posted.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

posted = load_data()

# ==========================
# اختيار إيموجي جذاب
# ==========================
def add_emoji():
    emojis = ["🔥","⚡","🧠","🌍","🚨"]
    return random.choice(emojis)

# ==========================
# جلب الأخبار
# ==========================
def get_news():
    news = []
    for feed in RSS_FEEDS:
        parsed = feedparser.parse(feed)
        for entry in parsed.entries[:5]:
            news.append({
                "title": entry.title,
                "link": entry.link
            })
    return news

# ==========================
# نشر الأخبار
# ==========================
def post_news():
    global posted
    news_list = get_news()

    for item in news_list:
        key = item["title"].lower()
        if key not in posted:
            try:
                message = f"{add_emoji()} {item['title']}"
                bot.send_message(CHANNEL, message)
                print("✅ News posted:", item['title'])

                posted.append(key)
                if len(posted) > 200:
                    posted = posted[-200:]
                save_data(posted)
                break
            except Exception as e:
                print("Error posting:", e)

# ==========================
# الجدولة
# ==========================
schedule.every(3).minutes.do(post_news)  # كل 3 دقائق
# يمكنك تعديل الوقت حسب رغبتك

print("🚀 Lightweight News Bot Running...")

post_news()  # نشر أولي عند التشغيل

while True:
    schedule.run_pending()
    time.sleep(10)