from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

from bot.converters.dispatcher import execute_compression
from bot.converters.archive_converter import compress_to_zip
from bot.utils.file_manager import create_user_workspace, cleanup_workspace, format_size
from bot.utils.keyboard import get_compress_keyboard

async def act_compress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle click on 'Compress File' button."""
    query = update.callback_query
    await query.answer()

    active = context.user_data.get("active_file")
    if not active:
        await query.edit_message_text("⚠️ No active file found. Please send your file again.")
        return

    cat = active["category"]
    ext = active["extension"]
    label = active["file_name"]

    await query.edit_message_text(
        f"Select compression mode for `{label}`:",
        reply_markup=get_compress_keyboard(cat, ext),
        parse_mode="Markdown"
    )

async def perform_compression_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform file compression and return the compressed file."""
    query = update.callback_query
    await query.answer()

    mode = query.data
    active = context.user_data.get("active_file")
    if not active:
        await query.edit_message_text("⚠️ File session expired. Please re-send the file.")
        return

    user_id = update.effective_user.id

    # Branch: Album / Multi-file compression
    if active.get("is_album"):
        album_files = active["files"]
        unique_id = str(active.get("album_id", "album"))
        orig_size = active["file_size"]
        workspace = create_user_workspace(user_id, unique_id)

        try:
            await query.edit_message_text(f"⏳ Downloading {len(album_files)} files in album...", parse_mode="Markdown")

            downloaded_paths = []
            for item in album_files:
                p = workspace / item["file_name"]
                tg_f = await context.bot.get_file(item["file_id"])
                await tg_f.download_to_drive(custom_path=p)
                downloaded_paths.append(p)

            await query.edit_message_text(f"🗜️ Compressing {len(album_files)} files...\nPlease wait.", parse_mode="Markdown")

            comp_dir = workspace / "compressed"
            comp_dir.mkdir(exist_ok=True)
            for p in downloaded_paths:
                try:
                    execute_compression(p, mode, comp_dir)
                except Exception:
                    pass

            zip_out = compress_to_zip(comp_dir, workspace)
            output_path = workspace / "compressed_album.zip"
            if zip_out.exists():
                zip_out.rename(output_path)

            if not output_path.exists():
                raise FileNotFoundError("Compressed album file was not generated.")

            new_size = output_path.stat().st_size
            savings_bytes = orig_size - new_size
            pct = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0
            savings_str = f"-{pct:.1f}% ({format_size(abs(savings_bytes))} saved)" if savings_bytes >= 0 else f"+{abs(pct):.1f}%"

            caption = (
                f"🗜️ *Album Compression Complete!*\n\n"
                f"• *Files Processed:* `{len(album_files)}`\n"
                f"• *Output:* `{output_path.name}`\n"
                f"• *Original Total:* `{format_size(orig_size)}`\n"
                f"• *Compressed Size:* `{format_size(new_size)}`\n"
                f"• *Reduction:* *{savings_str}*\n"
            )

            await query.edit_message_text("📤 Uploading compressed album...")

            with open(output_path, "rb") as out_f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=out_f,
                    filename=output_path.name,
                    caption=caption,
                    parse_mode="Markdown"
                )

            await query.edit_message_text("🎉 *All done!* Feel free to send another file or album anytime.", parse_mode="Markdown")

        except Exception as e:
            await query.edit_message_text(f"❌ Compression failed:\n`{str(e)}`", parse_mode="Markdown")
        finally:
            cleanup_workspace(workspace)
        return

    # Branch: Single file compression
    file_id = active["file_id"]
    unique_id = active["file_unique_id"]
    file_name = active["file_name"]
    orig_size = active["file_size"]

    workspace = create_user_workspace(user_id, unique_id)
    input_path = workspace / file_name

    try:
        await query.edit_message_text(f"⏳ Downloading `{file_name}`...", parse_mode="Markdown")

        tg_file = await context.bot.get_file(file_id)
        await tg_file.download_to_drive(custom_path=input_path)

        await query.edit_message_text(
            f"🗜️ Compressing `{file_name}`...\nPlease wait.",
            parse_mode="Markdown"
        )

        output_path = execute_compression(input_path, mode, workspace)

        if not output_path.exists():
            raise FileNotFoundError("Compressed file was not generated.")

        new_size = output_path.stat().st_size
        savings_bytes = orig_size - new_size
        pct_savings = ((orig_size - new_size) / orig_size * 100) if orig_size > 0 else 0

        savings_str = f"-{pct_savings:.1f}% ({format_size(abs(savings_bytes))} saved)" if savings_bytes >= 0 else f"+{abs(pct_savings):.1f}% (file grew)"

        caption = (
            f"🗜️ *Compression Complete!*\n\n"
            f"• *File:* `{output_path.name}`\n"
            f"• *Original Size:* `{format_size(orig_size)}`\n"
            f"• *Compressed Size:* `{format_size(new_size)}`\n"
            f"• *Reduction:* *{savings_str}*\n"
        )

        await query.edit_message_text("📤 Uploading compressed file...")

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
        await query.edit_message_text(f"❌ Compression failed:\n`{str(e)}`", parse_mode="Markdown")
    finally:
        cleanup_workspace(workspace)
