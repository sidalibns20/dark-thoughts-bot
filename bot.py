import telebot
import feedparser
import schedule
import time
import os
import json
import requests

# ==========================
# إعدادات
# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")
TRANSLATE_URL = os.environ.get("TRANSLATE_URL")

bot = telebot.TeleBot(TOKEN)

# ==========================
# مصادر الأخبار
# ==========================
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

# ==========================
# كلمات الفلترة (محتوى قوي)
# ==========================
KEYWORDS = [
    "war", "ai", "technology", "robot", "economy",
    "china", "usa", "russia", "israel", "crypto",
    "tesla", "google", "openai", "military"
]

# ==========================
# ملف التخزين
# ==========================
DATA_FILE = "posted_news.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

posted_news = load_data()

# ==========================
# تنظيف النص
# ==========================
def clean_text(text):
    return text.lower().strip()

# ==========================
# فلترة الأخبار
# ==========================
def is_relevant(title):
    title = title.lower()
    return any(word in title for word in KEYWORDS)

# ==========================
# ترجمة للعربية
# ==========================
def translate(text):
    try:
        response = requests.post(TRANSLATE_URL, json={
            "q": text,
            "source": "en",
            "target": "ar",
            "format": "text"
        })
        return response.json()["translatedText"]
    except:
        return text  # fallback

# ==========================
# جلب الأخبار
# ==========================
def get_news():
    news_items = []

    for feed in RSS_FEEDS:
        parsed = feedparser.parse(feed)

        for entry in parsed.entries[:5]:
            title = entry.title
            link = entry.link

            if is_relevant(title):
                news_items.append({
                    "title": title,
                    "link": link
                })

    return news_items

# ==========================
# نشر الأخبار
# ==========================
def post_news():
    global posted_news

    news_list = get_news()

    for news in news_list:
        clean = clean_text(news["title"])

        if clean not in posted_news:
            try:
                arabic = translate(news["title"])

                message = f"""🌍 {arabic}

🧠 {news['title']}

🔗 المصدر:
{news['link']}

📰 @darkthu9hts"""

                bot.send_message(CHANNEL, message)

                print("✅ News posted")

                posted_news.append(clean)

                # حفظ آخر 200 خبر
                if len(posted_news) > 200:
                    posted_news = posted_news[-200:]

                save_data(posted_news)

                break

            except Exception as e:
                print(f"❌ Error: {e}")

# ==========================
# الجدولة
# ==========================
schedule.every(3).minutes.do(post_news)

# ==========================
# التشغيل
# ==========================
print("🚀 Ultimate News Bot Running...")

post_news()

while True:
    schedule.run_pending()
    time.sleep(10)