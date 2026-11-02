from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from bot.config import MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB
from bot.utils.file_manager import format_size
from bot.utils.format_detector import detect_category, normalize_extension
from bot.utils.keyboard import get_action_keyboard

async def file_receiver_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and analyze incoming files, images, videos, and audio."""
    msg = update.message
    if not msg:
        return

    tg_file = None
    file_name = "unknown_file"
    file_size = 0

    if msg.document:
        tg_file = msg.document
        file_name = msg.document.file_name or "file.bin"
        file_size = msg.document.file_size or 0
    elif msg.photo:
        tg_file = msg.photo[-1]  # Highest resolution
        file_name = f"photo_{tg_file.file_unique_id}.jpg"
        file_size = tg_file.file_size or 0
    elif msg.video:
        tg_file = msg.video
        file_name = msg.video.file_name or f"video_{tg_file.file_unique_id}.mp4"
        file_size = msg.video.file_size or 0
    elif msg.audio:
        tg_file = msg.audio
        file_name = msg.audio.file_name or f"audio_{tg_file.file_unique_id}.mp3"
        file_size = msg.audio.file_size or 0
    elif msg.voice:
        tg_file = msg.voice
        file_name = f"voice_{tg_file.file_unique_id}.ogg"
        file_size = msg.voice.file_size or 0
    else:
        await msg.reply_text("⚠️ Unsupported attachment type. Please send a document, photo, video, or audio file.")
        return

    # Check size limit
    if file_size > MAX_FILE_SIZE_BYTES:
        await msg.reply_text(
            f"❌ File too large ({format_size(file_size)}).\n"
            f"The maximum allowed size is {MAX_FILE_SIZE_MB} MB due to Telegram Bot API limits."
        )
        return

    # Extract extension and category
    ext = Path(file_name).suffix.lstrip(".").lower()
    if not ext and msg.photo:
        ext = "jpg"
    category = detect_category(ext) or "other"

    # Store file context in user session
    context.user_data["active_file"] = {
        "file_id": tg_file.file_id,
        "file_unique_id": tg_file.file_unique_id,
        "file_name": file_name,
        "file_size": file_size,
        "extension": ext,
        "category": category,
        "local_path": None,
        "workspace_dir": None
    }

    category_badge = {
        "image": "🖼️ Image",
        "audio": "🎵 Audio",
        "video": "🎬 Video",
        "document": "📄 Document",
        "data": "📊 Data File",
        "archive": "📦 Archive",
        "other": "📁 General File"
    }.get(category, "📁 File")

    caption = (
        f"📥 *Received File:*\n"
        f"• *Name:* `{file_name}`\n"
        f"• *Size:* `{format_size(file_size)}`\n"
        f"• *Type:* {category_badge} (`.{ext}`)\n\n"
        f"What would you like to do with this file?"
    )

    await msg.reply_text(
        caption,
        parse_mode="Markdown",
        reply_markup=get_action_keyboard(category, ext)
    )
