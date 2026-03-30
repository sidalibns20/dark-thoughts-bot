import telebot
import requests
import schedule
import time
import os

# ==========================
# إعدادات البوت
# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")  # @darkthu9hts
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

bot = telebot.TeleBot(TOKEN)

# ==========================
# تخزين الأخبار المنشورة
# ==========================
posted_news = []

# ==========================
# جلب الأخبار
# ==========================
def get_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=10&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        articles = data.get("articles", [])
        news_list = []

        for article in articles:
            title = article.get("title")
            source = article.get("source", {}).get("name", "")
            
            if title:
                news = f"🌍 {title}\n📰 {source}"
                news_list.append(news)

        return news_list

    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

# ==========================
# نشر الأخبار بدون تكرار
# ==========================
def post_news():
    news_list = get_news()

    for news in news_list:
        if news not in posted_news:
            try:
                bot.send_message(CHANNEL, news)
                print("✅ News posted")

                posted_news.append(news)

                # الاحتفاظ بآخر 20 خبر فقط
                if len(posted_news) > 20:
                    posted_news.pop(0)

                break  # نشر خبر واحد فقط كل مرة

            except Exception as e:
                print(f"❌ Error sending: {e}")

# ==========================
# الجدولة (كل 5 دقائق)
# ==========================
schedule.every(5).minutes.do(post_news)

# ==========================
# التشغيل
# ==========================
print("🚀 News Bot is running...")

post_news()  # نشر فوري عند التشغيل

while True:
    schedule.run_pending()
    time.sleep(10)