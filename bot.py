import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = os.environ.get("BASE_URL")  # https://your-app.railway.app

# ─── COMMANDS ────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Hello {name}!\n\n"
        "🗂 Mujhe koi bhi file bhejo aur main aapko ek *download link* de dunga!\n\n"
        "📄 Documents\n🖼 Photos\n🎵 Audio\n🎥 Video — sab supported hai!\n\n"
        "Max size: *20MB*",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Help*\n\n"
        "1️⃣ Bot ko koi bhi file bhejo\n"
        "2️⃣ Bot file Telegram par store kar lega\n"
        "3️⃣ Aapko ek download link milega\n"
        "4️⃣ Woh link kisi ke saath bhi share karo!\n\n"
        "⚠️ Files Telegram ke servers par hoti hain — hamesha available rahti hain.",
        parse_mode="Markdown"
    )

# ─── FILE HANDLER ─────────────────────────────────────────────────────────────

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    # Kaunsi file aayi — detect karo
    if msg.document:
        file = msg.document
        file_name = file.file_name
        file_size = file.file_size
        file_id = file.file_id

    elif msg.photo:
        file = msg.photo[-1]  # Sabse badi quality
        file_name = f"photo_{file.file_unique_id}.jpg"
        file_size = file.file_size
        file_id = file.file_id

    elif msg.audio:
        file = msg.audio
        file_name = file.file_name or f"audio_{file.file_unique_id}.mp3"
        file_size = file.file_size
        file_id = file.file_id

    elif msg.video:
        file = msg.video
        file_name = file.file_name or f"video_{file.file_unique_id}.mp4"
        file_size = file.file_size
        file_id = file.file_id

    elif msg.voice:
        file = msg.voice
        file_name = f"voice_{file.file_unique_id}.ogg"
        file_size = file.file_size
        file_id = file.file_id

    else:
        await msg.reply_text("⚠️ Ye file type support nahi hota. Document, Photo, Audio ya Video bhejo.")
        return

    # Size check (20MB limit)
    if file_size and file_size > 20 * 1024 * 1024:
        await msg.reply_text("❌ File 20MB se badi hai! Telegram Bot API 20MB tak hi support karta hai.")
        return

    # Processing message
    processing = await msg.reply_text("⏳ Link ban raha hai...")

    try:
        # Telegram file object lo
        tg_file = await context.bot.get_file(file_id)

        # Download link banao
        # Format: https://api.telegram.org/file/bot{TOKEN}/{file_path}
        download_url = tg_file.file_path  # ye already full URL hota hai

        # Size format karo
        size_str = format_size(file_size)

        # Processing message delete karo
        await processing.delete()

        # Button banao
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬇️ Download Karo", url=download_url)]
        ])

        await msg.reply_text(
            f"✅ *File Ready!*\n\n"
            f"📄 *Name:* `{file_name}`\n"
            f"📦 *Size:* {size_str}\n\n"
            f"🔗 *Download Link:*\n`{download_url}`",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        await processing.edit_text("❌ Kuch error aaya. Dobara try karo.")

# ─── HELPER ───────────────────────────────────────────────────────────────────

def format_size(size):
    if not size:
        return "Unknown"
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable set nahi hai!")

    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # File handlers
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(MessageHandler(filters.PHOTO, handle_file))
    app.add_handler(MessageHandler(filters.AUDIO, handle_file))
    app.add_handler(MessageHandler(filters.VIDEO, handle_file))
    app.add_handler(MessageHandler(filters.VOICE, handle_file))

    print("🤖 Bot chal raha hai...")
    app.run_polling()

if __name__ == "__main__":
    main()
