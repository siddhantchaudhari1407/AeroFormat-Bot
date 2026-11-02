from telegram import Update
from telegram.ext import ContextTypes

START_TEXT = """
⚡ *AeroFormat — Universal File Converter & Compressor*

Welcome! Send me any file, photo, video, document, or audio, and I will instantly convert it to your desired format or compress its size with high precision.

🚀 *Key Capabilities:*
• 🔄 *Format Conversion:* Convert images, audio, video, documents, and data.
• 🗜️ *Smart Compression:* Shrink file sizes with customizable quality tiers.
• ⚡ *Fast & Secure:* Automatic cleanup of files after conversion.

📂 *How to Use:*
1. Send or forward any file into this chat.
2. Select *🔄 Convert Format* or *🗜️ Compress File*.
3. Choose your desired output format or compression preset.
4. Download your converted file immediately!

Type /formats to view all supported extensions.
Type /help for usage guidance.
"""

HELP_TEXT = """
💡 *Bot Help & Instructions*

*How to use:*
• Just upload any file (up to 50MB).
• The bot will detect the type and show available conversions and compression options.

*Supported Conversions:*
• *Images:* JPG, PNG, WEBP, BMP, TIFF, ICO, PDF
• *Documents:* PDF ↔ DOCX, PDF ↔ TXT, CSV ↔ XLSX, TXT → PDF, Extract PDF images to ZIP
• *Audio:* MP3, WAV, OGG, AAC, FLAC, M4A
• *Video:* MP4, AVI, MKV, MOV, WEBM, GIF, Video to MP3
• *Data:* JSON ↔ YAML ↔ XML ↔ CSV
• *Archives:* Any file/folder to ZIP, TAR.GZ

*Compression Options:*
• *Images:* 80% (Light), 60% (Medium), 30% (High), 50% Resize
• *Videos:* H.264 compression with CRF control & 720p downscaling
• *Audio:* 64 kbps, 128 kbps, 192 kbps
• *PDF:* Standard stream compression or Aggressive image downscale
• *Other Files:* ZIP / TAR.GZ high compression

Need to cancel? Tap the ❌ Cancel button anytime or send /cancel.
"""

FORMATS_TEXT = """
📋 *Supported File Formats*

🖼️ *Images:*
• Inputs: `JPG`, `PNG`, `WEBP`, `BMP`, `TIFF`, `ICO`, `GIF`
• Targets: `JPG`, `PNG`, `WEBP`, `BMP`, `TIFF`, `ICO`, `PDF`

📄 *Documents:*
• `PDF` ➔ `DOCX`, `TXT`, `Images (ZIP)`
• `DOCX` ➔ `PDF`, `TXT`
• `TXT` ➔ `PDF`, `DOCX`
• `CSV` ➔ `XLSX`, `JSON`, `PDF`
• `XLSX` ➔ `CSV`, `JSON`

🎵 *Audio:*
• `MP3`, `WAV`, `OGG`, `AAC`, `FLAC`, `M4A`
• Bitrates: 64k, 128k, 192k

🎬 *Video:*
• `MP4`, `MKV`, `AVI`, `MOV`, `WEBM`, `GIF`
• Extract Audio: Video ➔ `MP3`

📊 *Data:*
• `JSON` ↔ `YAML` ↔ `XML` ↔ `CSV`

📦 *Archives:*
• Compress any file to `ZIP`, `TAR.GZ`
"""

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(START_TEXT, parse_mode="Markdown")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")

async def formats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /formats command."""
    await update.message.reply_text(FORMATS_TEXT, parse_mode="Markdown")
