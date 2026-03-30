import telebot
import feedparser
import schedule
import time
import os
import json
import random
from transformers import pipeline

# ==========================
# إعدادات البوت
# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")

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
# نموذج التلخيص المجاني (HuggingFace)
# ==========================
summarizer = pipeline("summarization", model="facebook/mbart-large-50-many-to-many-mmt")

def ai_summarize(text):
    try:
        result = summarizer(text, max_length=60, min_length=30, do_sample=False)
        return result[0]['summary_text']
    except:
        return text

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
                summary = ai_summarize(item["title"])
                emoji = add_emoji()
                message = f"{emoji} {summary}"

                bot.send_message(CHANNEL, message)
                print("✅ News posted")

                posted.append(key)
                if len(posted) > 200:
                    posted = posted[-200:]

                save_data(posted)
                break

            except Exception as e:
                print(e)

# ==========================
# الجدولة
# ==========================
schedule.every(3).minutes.do(post_news)

print("🚀 Elite Free AI News Bot Running...")

post_news()

while True:
    schedule.run_pending()
    time.sleep(10)