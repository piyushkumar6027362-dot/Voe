import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable set nahi hai!")

# ─── COMMANDS ────────────────────────────────────────────────────────────────

def start(update: Update, context: CallbackContext):
    name = update.effective_user.first_name
    update.message.reply_text(
        f"👋 Hello {name}!\n\n"
        "🗂 Mujhe koi bhi file bhejo aur main aapko ek download link de dunga!\n\n"
        "📄 Documents\n🖼 Photos\n🎵 Audio\n🎥 Video — sab supported hai!\n\n"
        "⚠️ Max size: 20MB"
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📖 Help\n\n"
        "1. Bot ko koi bhi file bhejo\n"
        "2. Bot aapko ek download link dega\n"
        "3. Woh link kisi ke saath bhi share karo!\n\n"
        "Files Telegram ke servers par hoti hain."
    )

# ─── FILE HANDLER ─────────────────────────────────────────────────────────────

def format_size(size):
    if not size:
        return "Unknown"
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"

def handle_file(update: Update, context: CallbackContext):
    msg = update.message

    if msg.document:
        file = msg.document
        file_name = file.file_name
        file_size = file.file_size
        file_id = file.file_id

    elif msg.photo:
        file = msg.photo[-1]
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
        msg.reply_text("⚠️ Ye file type support nahi hota.")
        return

    if file_size and file_size > 20 * 1024 * 1024:
        msg.reply_text("❌ File 20MB se badi hai!")
        return

    processing = msg.reply_text("⏳ Link ban raha hai...")

    try:
        tg_file = context.bot.get_file(file_id)
        download_url = tg_file.file_path
        size_str = format_size(file_size)

        processing.delete()

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬇️ Download Karo", url=download_url)]
        ])

        msg.reply_text(
            f"✅ File Ready!\n\n"
            f"📄 Name: {file_name}\n"
            f"📦 Size: {size_str}\n\n"
            f"🔗 Download Link:\n{download_url}",
            reply_markup=keyboard
        )

    except Exception as e:
        logging.error(f"Error: {e}")
        processing.edit_text("❌ Kuch error aaya. Dobara try karo.")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    updater = Updater(token=BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.document, handle_file))
    dp.add_handler(MessageHandler(Filters.photo, handle_file))
    dp.add_handler(MessageHandler(Filters.audio, handle_file))
    dp.add_handler(MessageHandler(Filters.video, handle_file))
    dp.add_handler(MessageHandler(Filters.voice, handle_file))

    print("🤖 Bot chal raha hai...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
