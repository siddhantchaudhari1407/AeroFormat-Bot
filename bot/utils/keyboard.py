from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils.format_detector import get_available_conversions, detect_category

def get_action_keyboard(category: str, extension: str) -> InlineKeyboardMarkup:
    """Main menu after receiving a file."""
    buttons = []
    
    conversions = get_available_conversions(extension)
    if conversions:
        buttons.append([InlineKeyboardButton("🔄 Convert Format", callback_data="act_convert")])
    
    # Always allow compression (either media compression or archive compression)
    buttons.append([InlineKeyboardButton("🗜️ Compress File", callback_data="act_compress")])
    buttons.append([InlineKeyboardButton("ℹ️ File Info", callback_data="act_info")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="act_cancel")])
    
    return InlineKeyboardMarkup(buttons)

def get_converters_keyboard(extension: str) -> InlineKeyboardMarkup:
    """Inline keyboard for available target conversion formats."""
    targets = get_available_conversions(extension)
    keyboard = []
    row = []
    
    for i, target in enumerate(targets):
        btn_text = f"➡️ {target.upper()}"
        # Telegram callback data format: conv:<target>
        row.append(InlineKeyboardButton(btn_text, callback_data=f"conv_{target}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
        
    keyboard.append([
        InlineKeyboardButton("⬅️ Back", callback_data="act_back"),
        InlineKeyboardButton("❌ Cancel", callback_data="act_cancel")
    ])
    return InlineKeyboardMarkup(keyboard)

def get_compress_keyboard(category: str, extension: str) -> InlineKeyboardMarkup:
    """Inline keyboard for compression options."""
    norm_ext = extension.lower().lstrip(".")
    keyboard = []
    
    if category == "image":
        keyboard.append([
            InlineKeyboardButton("🍃 Light (85% Quality)", callback_data="cmp_img_light"),
            InlineKeyboardButton("⚖️ Medium (60% Quality)", callback_data="cmp_img_medium")
        ])
        keyboard.append([
            InlineKeyboardButton("🔥 High (30% Quality)", callback_data="cmp_img_high"),
            InlineKeyboardButton("📐 Resize 50%", callback_data="cmp_img_half")
        ])
    elif category == "video":
        keyboard.append([
            InlineKeyboardButton("🍃 Light Compress (CRF 26)", callback_data="cmp_vid_light"),
            InlineKeyboardButton("⚖️ Medium Compress (CRF 30)", callback_data="cmp_vid_medium")
        ])
        keyboard.append([
            InlineKeyboardButton("🔥 High Compress (720p CRF 34)", callback_data="cmp_vid_high")
        ])
    elif category == "audio":
        keyboard.append([
            InlineKeyboardButton("📻 64 kbps (Voice/Podcast)", callback_data="cmp_aud_64"),
            InlineKeyboardButton("🎵 128 kbps (Standard)", callback_data="cmp_aud_128")
        ])
        keyboard.append([
            InlineKeyboardButton("🎧 192 kbps (High Quality)", callback_data="cmp_aud_192")
        ])
    elif norm_ext == "pdf":
        keyboard.append([
            InlineKeyboardButton("⚖️ Standard PDF Compress", callback_data="cmp_pdf_std"),
            InlineKeyboardButton("🔥 Aggressive PDF Compress", callback_data="cmp_pdf_agg")
        ])
    else:
        # Default archive compression
        keyboard.append([
            InlineKeyboardButton("📦 Compress to ZIP", callback_data="cmp_arch_zip"),
            InlineKeyboardButton("🗜️ Compress to TAR.GZ", callback_data="cmp_arch_targz")
        ])
        
    keyboard.append([
        InlineKeyboardButton("⬅️ Back", callback_data="act_back"),
        InlineKeyboardButton("❌ Cancel", callback_data="act_cancel")
    ])
    return InlineKeyboardMarkup(keyboard)
