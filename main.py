import telebot
from telebot import types
import yt_dlp
import os
import uuid

# =========================
# 🔐 الإعدادات
# =========================

TOKEN = os.environ.get("TOKEN")
CHANNEL = "@mr_downloader414"

bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# =========================
# 🔍 التحقق من الاشتراك
# =========================

def is_subscribed(user_id):
    try:
        m = bot.get_chat_member(CHANNEL, user_id)
        return m.status in ["member", "administrator", "creator"]
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

    bot.send_message(chat_id, "🚫 لازم تشترك أولاً", reply_markup=kb)

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
        "🔥 بوت برو ماكس جاهز\n\n"
        "📥 أرسل رابط (يوتيوب / تيك توك / أي فيديو)"
    )

# =========================
# 🔘 التحقق
# =========================

@bot.callback_query_handler(func=lambda c: c.data == "check")
def check(c):

    if is_subscribed(c.from_user.id):
        bot.answer_callback_query(c.id, "✔ تم التحقق")
        bot.send_message(c.message.chat.id, "🎯 أرسل الرابط الآن")
    else:
        bot.answer_callback_query(c.id, "❌ لم تشترك")

# =========================
# 🧠 التحميل الذكي
# =========================

def download(url, chat_id, mode):

    uid = str(uuid.uuid4())
    base = f"{DOWNLOAD_DIR}/{uid}"

    try:

        # 🎬 فيديو (أفضل جودة)
        if mode == "video":
            opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': base + ".mp4",
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'quiet': True
            }

        # 🎵 صوت
        elif mode == "audio":
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': base,
                'noplaylist': True,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }

        # 🖼 صورة
        else:
            opts = {'quiet': True, 'skip_download': True}

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=(mode != "image"))

        # ================= VIDEO =================
        if mode == "video":
            file = base + ".mp4"
            if os.path.exists(file):
                with open(file, "rb") as f:
                    bot.send_video(chat_id, f, supports_streaming=True)
                os.remove(file)
            else:
                bot.send_message(chat_id, "❌ فشل تحميل الفيديو")

        # ================= AUDIO =================
        elif mode == "audio":
            file = base + ".mp3"
            if os.path.exists(file):
                with open(file, "rb") as f:
                    bot.send_audio(chat_id, f)
                os.remove(file)
            else:
                bot.send_message(chat_id, "❌ فشل تحميل الصوت")

        # ================= IMAGE =================
        elif mode == "image":
            thumb = info.get("thumbnail")
            if thumb:
                bot.send_photo(chat_id, thumb, caption="🖼 صورة الفيديو")
            else:
                bot.send_message(chat_id, "❌ لا توجد صورة")

    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ:\n{e}")
        print("ERROR:", e)

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
        bot.send_message(m.chat.id, "📌 أرسل رابط صحيح")
        return

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton("🎬 فيديو", callback_data=f"video|{url}"),
        types.InlineKeyboardButton("🎵 صوت", callback_data=f"audio|{url}")
    )

    kb.add(
        types.InlineKeyboardButton("🖼 صورة", callback_data=f"image|{url}")
    )

    bot.send_message(m.chat.id, "🎯 اختر نوع التحميل:", reply_markup=kb)

# =========================
# 🔘 الأزرار
# =========================

@bot.callback_query_handler(func=lambda c: True)
def callback(c):

    try:
        data = c.data

        if data.startswith("video|"):
            url = data.split("|", 1)[1]
            bot.send_message(c.message.chat.id, "⏳ تحميل الفيديو...")
            download(url, c.message.chat.id, "video")

        elif data.startswith("audio|"):
            url = data.split("|", 1)[1]
            bot.send_message(c.message.chat.id, "⏳ تحميل الصوت...")
            download(url, c.message.chat.id, "audio")

        elif data.startswith("image|"):
            url = data.split("|", 1)[1]
            bot.send_message(c.message.chat.id, "⏳ استخراج الصورة...")
            download(url, c.message.chat.id, "image")

    except Exception as e:
        bot.send_message(c.message.chat.id, f"❌ خطأ:\n{e}")

# =========================
# 🚀 تشغيل
# =========================

print("🚀 Bot Pro Max Running...")

bot.infinity_polling(skip_pending=True)