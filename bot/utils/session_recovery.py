from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.format_detector import detect_category

def resolve_active_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> dict:
    """
    Returns the active file from user_data, or automatically recovers it
    from the original Telegram message (via reply_to_message) if the server restarted.
    """
    active = context.user_data.get("active_file")
    if active:
        return active

    query = update.callback_query
    if not query or not query.message or not query.message.reply_to_message:
        return None

    orig_msg = query.message.reply_to_message
    tg_file = None
    file_name = "unknown_file"
    file_size = 0

    if orig_msg.document:
        tg_file = orig_msg.document
        file_name = orig_msg.document.file_name or "file.bin"
        file_size = orig_msg.document.file_size or 0
    elif orig_msg.photo:
        tg_file = orig_msg.photo[-1]
        file_name = f"photo_{tg_file.file_unique_id}.jpg"
        file_size = tg_file.file_size or 0
    elif orig_msg.video:
        tg_file = orig_msg.video
        file_name = orig_msg.video.file_name or f"video_{tg_file.file_unique_id}.mp4"
        file_size = orig_msg.video.file_size or 0
    elif orig_msg.audio:
        tg_file = orig_msg.audio
        file_name = orig_msg.audio.file_name or f"audio_{tg_file.file_unique_id}.mp3"
        file_size = orig_msg.audio.file_size or 0
    elif orig_msg.voice:
        tg_file = orig_msg.voice
        file_name = f"voice_{tg_file.file_unique_id}.ogg"
        file_size = orig_msg.voice.file_size or 0
    else:
        return None

    ext = Path(file_name).suffix.lstrip(".").lower()
    if not ext and orig_msg.photo:
        ext = "jpg"
    cat = detect_category(ext) or "other"

    recovered = {
        "is_album": False,
        "file_id": tg_file.file_id,
        "file_unique_id": tg_file.file_unique_id,
        "file_name": file_name,
        "file_size": file_size,
        "extension": ext,
        "category": cat
    }

    # Store recovered session so subsequent callbacks work instantly
    context.user_data["active_file"] = recovered
    return recovered
