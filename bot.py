from aigrom import Bot, Dispatcher, types
from pytube import YouTube
import os

TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("🎬 *YouTube Downloader Bot*\n"
                         "Menga YouTube link yubor — men uni yuklab beraman.\n"
                         "Avval sifatini tanlaysan!", parse_mode="Markdown")


@dp.message_handler()
async def get_link(message: types.Message):
    url = message.text.strip()

    # Link tekshirish
    if not ("youtu.be" in url or "youtube.com" in url):
        await message.answer("❌ Bu YouTube link emas! Iltimos, to‘g‘ri link yuboring.")
        return

    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension="mp4")

        # Sifatlar ro‘yxati
        qualities = []
        for s in streams:
            qualities.append(s.resolution)

        qualities = list(dict.fromkeys(qualities))  # takrorlarni o‘chirish

        # Sifat tanlash tugmalari
        buttons = [[types.KeyboardButton(q)] for q in qualities]

        kb = types.ReplyKeyboardMarkup(resize=True)
        kb.keyboard = buttons

        await message.answer(
            f"🎥 *{yt.title}*\n\nQuyidagi sifatlardan birini tanlang:",
            parse_mode="Markdown",
            reply_markup=kb
        )

        # foydalanuvchi linkini saqlash
        message.from_user.data = {"url": url}

    except Exception as e:
        await message.answer("❌ Video yuklab bo‘lmadi. Linkni tekshirib ko‘ring.")


@dp.message_handler()
async def download_quality(message: types.Message):
    # Agar oldin link yuborilmagan bo‘lsa
    if not message.from_user.data:
        return

    url = message.from_user.data.get("url")
    quality = message.text.strip()

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(resolution=quality, progressive=True).first()

        if not stream:
            await message.answer("❌ Bu sifat mavjud emas. Boshqa sifat tanlang.")
            return

        msg = await message.answer("⬇️ Yuklanmoqda...")

        # Faylni yuklab olish
        path = stream.download(filename="video.mp4")

        # Telegramga yuborish
        await bot.send_video(
            chat_id=message.chat.id,
            video=open(path, "rb"),
            caption=f"🎬 *{yt.title}*\nSifat: {quality}",
            parse_mode="Markdown"
        )

        # Faylni o‘chirish
        os.remove(path)

        await msg.delete()

    except:
        await message.answer("❌ Yuklab olishda xatolik!")


dp.run_polling()