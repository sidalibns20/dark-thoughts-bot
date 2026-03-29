import telebot
import requests
import random
from bs4 import BeautifulSoup
import schedule
import time
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# ==========================
# إعدادات البوت
# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")  # @darkthu9hts
bot = telebot.TeleBot(TOKEN)

# ==========================
# قائمة لتخزين آخر المنشورات
# ==========================
posted_quotes = []

# ==========================
# جلب اقتباس إنجليزي
# ==========================
def get_english_quote():
    try:
        response = requests.get("https://api.quotable.io/random?tags=dark,philosophy")
        data = response.json()
        text = data.get("content", "")
        author = data.get("author", "")
        return f"{text}\n— {author}"
    except:
        return "Dark thoughts never fade… 🖤"

# ==========================
# جلب اقتباس عربي
# ==========================
def get_arabic_quotes():
    quotes = []
    try:
        res = requests.get("https://hekmah.online/")
        soup = BeautifulSoup(res.text, "html.parser")
        quotes += [q.text.strip() for q in soup.select(".quote-text") if q.text.strip()]
    except:
        pass
    try:
        res = requests.get("https://www.ekhtaboot.com/ar/quotes")
        soup = BeautifulSoup(res.text, "html.parser")
        quotes += [q.text.strip() for q in soup.select(".quote") if q.text.strip()]
    except:
        pass
    if quotes:
        return random.choice(quotes)
    else:
        return "الأفكار الداكنة تعكس العمق الداخلي… 🌑"

# ==========================
# إضافة إيموجيات
# ==========================
def add_emoji(text):
    emojis = ["🖤","🌑","💀","🔥","🌫️","🕷️"]
    return random.choice(emojis) + " " + text

# ==========================
# إنشاء صورة للاقتباس
# ==========================
def create_quote_image(eng, ara):
    width, height = 800, 800
    background_color = (15, 15, 15)
    text_color = (255, 255, 255)

    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # قد تحتاج تعديل على المنصة
        font = ImageFont.truetype(font_path, 28)
    except:
        font = ImageFont.load_default()

    # نصوص
    full_text = f"{add_emoji(eng)}\n\n{add_emoji(ara)}\n\n🌑 @darkthu9hts"

    # تقسيم النص لتجنب التجاوز
    lines = []
    for line in full_text.split('\n'):
        if len(line) > 50:
            for i in range(0, len(line), 50):
                lines.append(line[i:i+50])
        else:
            lines.append(line)

    y_text = 50
    for line in lines:
        draw.text((50, y_text), line, font=font, fill=text_color)
        y_text += 50

    # حفظ الصورة في بايت
    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio

# ==========================
# تنسيق المنشور ومنع التكرار
# ==========================
def format_post():
    max_tries = 10
    for _ in range(max_tries):
        eng = get_english_quote()
        ara = get_arabic_quotes()
        post_text = f"{eng}\n{ara}"
        if post_text not in posted_quotes:
            posted_quotes.append(post_text)
            if len(posted_quotes) > 5:
                posted_quotes.pop(0)
            img = create_quote_image(eng, ara)
            return img
    # إذا تكرر كل شيء
    eng = get_english_quote()
    ara = get_arabic_quotes()
    return create_quote_image(eng, ara)

# ==========================
# النشر
# ==========================
def post_quotes():
    try:
        img = format_post()
        bot.send_photo(CHANNEL, img)
        print("✅ تم النشر في القناة!")
    except Exception as e:
        print(f"❌ خطأ: {e}")

# ==========================
# الجدولة كل 30 دقيقة
# ==========================
schedule.every(30).minutes.do(post_quotes)

# ==========================
# التشغيل
# ==========================
print("🚀 Bot is running...")
post_quotes()  # نشر فوري

while True:
    schedule.run_pending()
    time.sleep(10)