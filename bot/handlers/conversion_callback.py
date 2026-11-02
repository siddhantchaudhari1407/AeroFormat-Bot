from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from bot.converters.dispatcher import execute_conversion
from bot.utils.file_manager import create_user_workspace, cleanup_workspace, format_size
from bot.utils.keyboard import get_converters_keyboard

async def act_convert_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle click on 'Convert Format' button."""
    query = update.callback_query
    await query.answer()

    active = context.user_data.get("active_file")
    if not active:
        await query.edit_message_text("⚠️ No active file found. Please send your file again.")
        return

    ext = active["extension"]
    await query.edit_message_text(
        f"Select the target format for `{active['file_name']}`:",
        reply_markup=get_converters_keyboard(ext),
        parse_mode="Markdown"
    )

async def perform_conversion_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform format conversion and return the converted file."""
    query = update.callback_query
    await query.answer()

    target_format = query.data.replace("conv_", "")
    active = context.user_data.get("active_file")
    if not active:
        await query.edit_message_text("⚠️ File session expired. Please re-send the file.")
        return

    user_id = update.effective_user.id
    file_id = active["file_id"]
    unique_id = active["file_unique_id"]
    file_name = active["file_name"]
    orig_size = active["file_size"]

    # Setup isolated workspace
    workspace = create_user_workspace(user_id, unique_id)
    input_path = workspace / file_name

    try:
        await query.edit_message_text(f"⏳ Downloading `{file_name}`...", parse_mode="Markdown")
        
        # Download file from Telegram
        tg_file = await context.bot.get_file(file_id)
        await tg_file.download_to_drive(custom_path=input_path)

        await query.edit_message_text(
            f"⚙️ Converting `{file_name}` to *{target_format.upper()}*...\nPlease wait.",
            parse_mode="Markdown"
        )

        # Convert
        output_path = execute_conversion(input_path, target_format, workspace)
        
        if not output_path.exists():
            raise FileNotFoundError("Target converted file was not generated.")

        new_size = output_path.stat().st_size
        caption = (
            f"✅ *Conversion Complete!*\n\n"
            f"• *Output:* `{output_path.name}`\n"
            f"• *Original Size:* `{format_size(orig_size)}`\n"
            f"• *New Size:* `{format_size(new_size)}`\n"
        )

        await query.edit_message_text("📤 Uploading converted file...")

        # Send file back to user
        with open(output_path, "rb") as out_f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=out_f,
                filename=output_path.name,
                caption=caption,
                parse_mode="Markdown"
            )

        await query.edit_message_text("🎉 *All done!* Feel free to send another file anytime.", parse_mode="Markdown")

    except Exception as e:
        await query.edit_message_text(f"❌ Conversion failed:\n`{str(e)}`", parse_mode="Markdown")
    finally:
        # Clean workspace
        cleanup_workspace(workspace)
