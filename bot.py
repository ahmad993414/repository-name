import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

BOT_TOKEN = "8754396318:AAG5BBwX7S67Vy2LC8z-uURIc45WmaX0elY"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply("⚡ أهلاً بك يا أحمد! بوت التحميل الذكي المطور يعمل الآن بنظام التوجيه المباشر ومحصن 100% ضد الحظر.")

@dp.message()
async def download_link(message: types.Message):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        await message.reply("❌ يرجى إرسال رابط صحيح يبدأ بـ http أو https.")
        return
        
    url_lower = url.lower()
    
    if "instagram.com" in url_lower:
        clean_url = url.split('?')
        download_gateway = clean_url[0].replace("instagram.com", "ddinstagram.com").replace("Instagram.com", "ddinstagram.com")
        await message.reply_text(f"🎬 **المقطع جاهز للمشاهدة والحفظ الفوري بداخل الشات!**\n\n🔗 {download_gateway}")
        return
    elif "tiktok.com" in url_lower:
        clean_url = url.split('?')
        download_gateway = clean_url[0].replace("tiktok.com", "vxtiktok.com")
        await message.reply_text(f"🎬 **المقطع جاهز للمشاهدة والحفظ الفوري بداخل الشات!**\n\n🔗 {download_gateway}")
        return
        
    await message.reply_text(f"🔗 اضغط هنا للمشاهدة والحفظ الفوري عبر متصفح جوالك الآمن:\n\n{url}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
