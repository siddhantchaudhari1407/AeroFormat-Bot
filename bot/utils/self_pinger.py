import os
import time
import threading
import urllib.request
import logging

logger = logging.getLogger(__name__)

def start_auto_self_ping(interval_seconds: int = 600):
    """
    Periodically sends an external HTTP request to the bot's own public Render URL
    to prevent Render's free tier from entering sleep mode.
    """
    def _ping_worker():
        # Wait 30 seconds after bot boot before starting self-ping cycle
        time.sleep(30)
        
        while True:
            # Render automatically populates RENDER_EXTERNAL_URL or RENDER_EXTERNAL_HOSTNAME
            target_url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("PING_URL")
            if not target_url and os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
                target_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}"
                
            if target_url:
                try:
                    req = urllib.request.Request(
                        target_url,
                        headers={"User-Agent": "AeroFormat-KeepAlive-Agent/1.0"}
                    )
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        logger.info(f"⚡ [Keep-Alive Ping] Sent ping to {target_url} -> Status {resp.status}")
                except Exception as err:
                    logger.warning(f"⚠️ [Keep-Alive Ping] Self-ping attempt to {target_url} returned: {err}")
            else:
                logger.debug("[Keep-Alive Ping] Neither RENDER_EXTERNAL_URL nor PING_URL is set.")
                
            time.sleep(interval_seconds)

    thread = threading.Thread(target=_ping_worker, daemon=True, name="SelfPingerThread")
    thread.start()
    logger.info("✅ [Keep-Alive Self-Pinger] Background thread initialized (10-minute cycle).")
