from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from PIL import Image

from bot.converters.dispatcher import execute_conversion
from bot.converters.archive_converter import compress_to_zip
from bot.utils.file_manager import create_user_workspace, cleanup_workspace, format_size
from bot.utils.keyboard import get_converters_keyboard
from bot.utils.session_recovery import resolve_active_file

async def act_convert_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle click on 'Convert Format' button."""
    query = update.callback_query
    await query.answer()

    active = resolve_active_file(update, context)
    if not active:
        await query.edit_message_text("⚠️ No active file found. Please send your file again.")
        return

    ext = active["extension"]
    label = active["file_name"]
    await query.edit_message_text(
        f"Select the target format for `{label}`:",
        reply_markup=get_converters_keyboard(ext),
        parse_mode="Markdown"
    )

async def perform_conversion_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perform format conversion and return the converted file."""
    query = update.callback_query
    await query.answer()

    target_format = query.data.replace("conv_", "")
    active = resolve_active_file(update, context)
    if not active:
        await query.edit_message_text("⚠️ File session expired. Please re-send the file.")
        return

    user_id = update.effective_user.id

    # Branch: Album / Multi-file conversion
    if active.get("is_album"):
        album_files = active["files"]
        unique_id = str(active.get("album_id", "album"))
        workspace = create_user_workspace(user_id, unique_id)

        try:
            await query.edit_message_text(f"⏳ Downloading {len(album_files)} files in album...", parse_mode="Markdown")

            downloaded_paths = []
            for item in album_files:
                p = workspace / item["file_name"]
                tg_f = await context.bot.get_file(item["file_id"])
                await tg_f.download_to_drive(custom_path=p)
                downloaded_paths.append(p)

            # Option A: Merge all images into a single multi-page PDF
            if target_format in {"merge_pdf", "pdf"}:
                await query.edit_message_text("⚙️ Merging album images into a single PDF...", parse_mode="Markdown")
                images = []
                for p in downloaded_paths:
                    try:
                        im = Image.open(p)
                        if im.mode != "RGB":
                            im = im.convert("RGB")
                        images.append(im)
                    except Exception:
                        pass
                if not images:
                    raise ValueError("No convertible images found in album.")

                output_path = workspace / "merged_album.pdf"
                images[0].save(output_path, "PDF", save_all=True, append_images=images[1:])

            # Option B: Convert all files into target format and bundle into ZIP
            else:
                await query.edit_message_text(f"⚙️ Converting {len(album_files)} files to *{target_format.upper()}*...", parse_mode="Markdown")
                conv_dir = workspace / "converted"
                conv_dir.mkdir(exist_ok=True)
                for p in downloaded_paths:
                    try:
                        execute_conversion(p, target_format, conv_dir)
                    except Exception:
                        pass
                zip_out = compress_to_zip(conv_dir, workspace)
                output_path = workspace / f"converted_album_{target_format}.zip"
                if zip_out.exists():
                    zip_out.rename(output_path)

            if not output_path.exists():
                raise FileNotFoundError("Target converted file was not generated.")

            new_size = output_path.stat().st_size
            caption = (
                f"✅ *Album Conversion Complete!*\n\n"
                f"• *Files Processed:* `{len(album_files)}`\n"
                f"• *Output:* `{output_path.name}`\n"
                f"• *Size:* `{format_size(new_size)}`\n"
            )

            await query.edit_message_text("📤 Uploading converted file...")

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
            await query.edit_message_text(f"❌ Conversion failed:\n`{str(e)}`", parse_mode="Markdown")
        finally:
            cleanup_workspace(workspace)
        return

    # Branch: Single File conversion
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
            f"⚙️ Converting `{file_name}` to *{target_format.upper()}*...\nPlease wait.",
            parse_mode="Markdown"
        )

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
        cleanup_workspace(workspace)
