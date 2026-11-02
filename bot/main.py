import logging
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

class RenderHealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler to satisfy Render web service health checks."""
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "online", "bot": "AeroFormat", "message": "24/7 operational"}')

    def log_message(self, format, *args):
        return

def start_health_check_server():
    """Starts a lightweight web server in background thread for Render."""
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), RenderHealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"[Render Healthcheck] Listening on port {port}")
    except Exception as e:
        print(f"[Render Healthcheck] Warning: Could not bind port {port}: {e}")

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.config import TELEGRAM_BOT_TOKEN, CLEANUP_INTERVAL_SECONDS
from bot.handlers import (
    start_handler,
    help_handler,
    formats_handler,
    file_receiver_handler,
    act_convert_callback,
    perform_conversion_callback,
    act_compress_callback,
    perform_compression_callback,
    cancel_command_handler,
    act_cancel_callback,
    act_back_callback,
    act_info_callback
)
from bot.utils.file_manager import periodic_temp_cleanup

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def scheduled_cleanup_job(context):
    """Background job to clean old temporary files."""
    periodic_temp_cleanup(max_age_seconds=3600)

async def error_handler(update, context):
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")

def run():
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        print("\n" + "="*70)
        print("❌ ERROR: TELEGRAM_BOT_TOKEN is not set!")
        print("Please configure your TELEGRAM_BOT_TOKEN in the .env file or environment.")
        print("Example:")
        print("  TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ")
        print("="*70 + "\n")
        sys.exit(1)

    print("🤖 Starting Telegram File Converter & Compressor Bot...")
    start_health_check_server()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("formats", formats_handler))
    app.add_handler(CommandHandler("cancel", cancel_command_handler))

    # Action buttons
    app.add_handler(CallbackQueryHandler(act_convert_callback, pattern="^act_convert$"))
    app.add_handler(CallbackQueryHandler(act_compress_callback, pattern="^act_compress$"))
    app.add_handler(CallbackQueryHandler(act_cancel_callback, pattern="^act_cancel$"))
    app.add_handler(CallbackQueryHandler(act_back_callback, pattern="^act_back$"))
    app.add_handler(CallbackQueryHandler(act_info_callback, pattern="^act_info$"))

    # Conversion & Compression triggers
    app.add_handler(CallbackQueryHandler(perform_conversion_callback, pattern="^conv_"))
    app.add_handler(CallbackQueryHandler(perform_compression_callback, pattern="^cmp_"))

    # Media and Document receiver
    file_filters = (
        filters.Document.ALL |
        filters.PHOTO |
        filters.VIDEO |
        filters.AUDIO |
        filters.VOICE
    )
    app.add_handler(MessageHandler(file_filters, file_receiver_handler))

    # Periodic cleanup in job queue if available
    if app.job_queue:
        app.job_queue.run_repeating(scheduled_cleanup_job, interval=CLEANUP_INTERVAL_SECONDS, first=10)

    app.add_error_handler(error_handler)

    print("✅ Bot is online and listening for updates! Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    run()
