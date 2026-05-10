import telebot
from telebot import types
import yt_dlp
import os
import uuid

# =========================
# 🌐 Flask لـ Render
# =========================

from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "MR.DOWNLOADER is running!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

# =========================
# 🔐 الإعدادات
# =========================

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN not found")

CHANNEL = "@mr_downloader414"

bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# =========================
# 🔍 التحقق من الاشتراك
# =========================

def is_subscribed(user_id):

    try:

        m = bot.get_chat_member(
            CHANNEL,
            user_id
        )

        return m.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:

        return False

# =========================
# 🚫 اشتراك إجباري
# =========================

def force_join(chat_id):

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "📢 اشترك بالقناة",
            url=f"https://t.me/{CHANNEL.replace('@','')}"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "✅ تحقق",
            callback_data="check"
        )
    )

    bot.send_message(
        chat_id,
        "🚫 لازم تشترك أولاً",
        reply_markup=kb
    )

# =========================
# 🚀 START
# =========================

@bot.message_handler(commands=['start'])
def start(m):

    if not is_subscribed(m.from_user.id):

        force_join(m.chat.id)

        return

    bot.send_message(
        m.chat.id,
        "🔥 MR.DOWNLOADER جاهز\n\n📥 أرسل رابط الفيديو"
    )

# =========================
# 🔘 تحقق الاشتراك
# =========================

@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(c):

    if is_subscribed(c.from_user.id):

        bot.answer_callback_query(
            c.id,
            "✔ تم التحقق"
        )

        bot.send_message(
            c.message.chat.id,
            "🎯 أرسل الرابط الآن"
        )

    else:

        bot.answer_callback_query(
            c.id,
            "❌ لم تشترك"
        )

# =========================
# 🧠 التحميل الذكي
# =========================

def download(url, chat_id, mode):

    uid = str(uuid.uuid4())

    base = f"{DOWNLOAD_DIR}/{uid}"

    try:

        # ================= VIDEO =================

        if mode == "video":

            opts = {

                'format': 'bv*+ba/b',

                'outtmpl': base + ".mp4",

                'quiet': True,

                'noplaylist': True,

                'merge_output_format': 'mp4',

                'nocheckcertificate': True,

                'geo_bypass': True,

                'retries': 15,

                'fragment_retries': 15,

                'extractor_retries': 15,

                'http_headers': {

                    'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',

                    'Accept-Language':
                    'en-US,en;q=0.9'
                },

                'extractor_args': {

                    'youtube': {

                        'player_client': [
                            'web',
                            'android'
                        ]
                    }
                }
            }

            with yt_dlp.YoutubeDL(opts) as ydl:

                ydl.extract_info(
                    url,
                    download=True
                )

            file = base + ".mp4"

            if os.path.exists(file):

                with open(file, "rb") as f:

                    bot.send_video(
                        chat_id,
                        f,
                        supports_streaming=True
                    )

                os.remove(file)

            else:

                bot.send_message(
                    chat_id,
                    "❌ فشل تحميل الفيديو"
                )

        # ================= AUDIO =================

        elif mode == "audio":

            opts = {

                'format': 'bestaudio/best',

                'outtmpl': base + ".mp3",

                'quiet': True,

                'noplaylist': True,

                'nocheckcertificate': True,

                'geo_bypass': True,

                'retries': 15,

                'fragment_retries': 15,

                'extractor_retries': 15,

                'http_headers': {

                    'User-Agent':
                    'Mozilla/5.0'
                },

                'extractor_args': {

                    'youtube': {

                        'player_client': [
                            'web',
                            'android'
                        ]
                    }
                }
            }

            with yt_dlp.YoutubeDL(opts) as ydl:

                ydl.extract_info(
                    url,
                    download=True
                )

            file = base + ".mp3"

            if os.path.exists(file):

                with open(file, "rb") as f:

                    bot.send_audio(
                        chat_id,
                        f
                    )

                os.remove(file)

            else:

                bot.send_message(
                    chat_id,
                    "❌ فشل تحميل الصوت"
                )

        # ================= IMAGE =================

        elif mode == "image":

            opts = {

                'quiet': True,

                'skip_download': True
            }

            with yt_dlp.YoutubeDL(opts) as ydl:

                info = ydl.extract_info(
                    url,
                    download=False
                )

            thumb = info.get("thumbnail")

            if thumb:

                bot.send_photo(
                    chat_id,
                    thumb,
                    caption="🖼 صورة الفيديو"
                )

            else:

                bot.send_message(
                    chat_id,
                    "❌ لا توجد صورة"
                )

    except Exception as e:

        print("ERROR:", e)

        bot.send_message(
            chat_id,
            f"❌ خطأ:\n{e}"
        )

# =========================
# 📥 استقبال الروابط
# =========================

@bot.message_handler(func=lambda m: True)
def handle(m):

    if not is_subscribed(m.from_user.id):

        force_join(m.chat.id)

        return

    url = m.text.strip()

    if "http" not in url:

        bot.send_message(
            m.chat.id,
            "📌 أرسل رابط صحيح"
        )

        return

    kb = types.InlineKeyboardMarkup()

    kb.add(

        types.InlineKeyboardButton(
            "🎬 فيديو",
            callback_data=f"video|{url}"
        ),

        types.InlineKeyboardButton(
            "🎵 صوت",
            callback_data=f"audio|{url}"
        )
    )

    kb.add(

        types.InlineKeyboardButton(
            "🖼 صورة",
            callback_data=f"image|{url}"
        )
    )

    bot.send_message(
        m.chat.id,
        "🎯 اختر نوع التحميل:",
        reply_markup=kb
    )

# =========================
# 🔘 الأزرار
# =========================

@bot.callback_query_handler(func=lambda c: True)
def callback(c):

    try:

        data = c.data

        # ================= VIDEO =================

        if data.startswith("video|"):

            url = data.split("|", 1)[1]

            bot.send_message(
                c.message.chat.id,
                "⏳ تحميل الفيديو..."
            )

            download(
                url,
                c.message.chat.id,
                "video"
            )

        # ================= AUDIO =================

        elif data.startswith("audio|"):

            url = data.split("|", 1)[1]

            bot.send_message(
                c.message.chat.id,
                "⏳ تحميل الصوت..."
            )

            download(
                url,
                c.message.chat.id,
                "audio"
            )

        # ================= IMAGE =================

        elif data.startswith("image|"):

            url = data.split("|", 1)[1]

            bot.send_message(
                c.message.chat.id,
                "⏳ استخراج الصورة..."
            )

            download(
                url,
                c.message.chat.id,
                "image"
            )

    except Exception as e:

        print("CALLBACK ERROR:", e)

        bot.send_message(
            c.message.chat.id,
            f"❌ خطأ:\n{e}"
        )

# =========================
# 🚀 تشغيل Flask
# =========================

t = Thread(target=run_web)

t.start()

# =========================
# 🚀 تشغيل البوت
# =========================

print("🚀 MR.DOWNLOADER Running...")

while True:

    try:

        bot.infinity_polling(
            skip_pending=True
        )

    except Exception as e:

        print("Polling Error:", e)
