from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.file_manager import format_size
from bot.utils.keyboard import get_action_keyboard
from bot.utils.session_recovery import resolve_active_file

async def cancel_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command."""
    context.user_data.pop("active_file", None)
    await update.message.reply_text("❌ Action cancelled. Send another file whenever you are ready!")

async def act_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel button click."""
    query = update.callback_query
    await query.answer()
    context.user_data.pop("active_file", None)
    await query.edit_message_text("❌ Operation cancelled. Send any file whenever you want!")

async def act_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back button click to return to main action menu."""
    query = update.callback_query
    await query.answer()

    active = resolve_active_file(update, context)
    if not active:
        await query.edit_message_text("⚠️ Session expired. Please send the file again.")
        return

    cat = active["category"]
    ext = active["extension"]
    caption = (
        f"📥 *Received File:*\n"
        f"• *Name:* `{active['file_name']}`\n"
        f"• *Size:* `{format_size(active['file_size'])}`\n"
        f"• *Type:* `.{ext}`\n\n"
        f"What would you like to do with this file?"
    )
    await query.edit_message_text(
        caption,
        parse_mode="Markdown",
        reply_markup=get_action_keyboard(cat, ext)
    )

async def act_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed file info."""
    query = update.callback_query
    await query.answer()

    active = resolve_active_file(update, context)
    if not active:
        await query.edit_message_text("⚠️ Session expired. Please send the file again.")
        return

    info_text = (
        f"ℹ️ *File Information:*\n\n"
        f"• *Filename:* `{active['file_name']}`\n"
        f"• *Extension:* `.{active['extension']}`\n"
        f"• *Category:* `{active['category'].capitalize()}`\n"
        f"• *Raw Size:* `{active['file_size']} bytes` ({format_size(active['file_size'])})\n\n"
        f"Select an operation below:"
    )

    cat = active["category"]
    ext = active["extension"]
    await query.edit_message_text(
        info_text,
        parse_mode="Markdown",
        reply_markup=get_action_keyboard(cat, ext)
    )
