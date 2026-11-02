# 🤖 Universal File Converter & Compressor Bot

A feature-rich, high-performance Telegram Bot built in Python that converts files across virtually any format (images, documents, audio, video, structured data, and archives) and performs smart file compression with customizable quality levels.

---

## ✨ Features

- **🔄 Universal Format Conversion**:
  - **Images**: PNG, JPG, JPEG, WEBP, BMP, TIFF, ICO, PDF.
  - **Documents**: PDF ↔ DOCX, PDF ↔ TXT, CSV ↔ XLSX, TXT → PDF, PDF → Images (.ZIP).
  - **Audio**: MP3, WAV, OGG, AAC, FLAC, M4A.
  - **Video**: MP4, MKV, AVI, MOV, WEBM, GIF, Video ➔ MP3 (Audio Extractor).
  - **Data**: JSON ↔ YAML ↔ XML ↔ CSV.
  - **Archives**: Pack or convert to ZIP, TAR.GZ, TAR.BZ2.
- **🗜️ Multi-Level Smart Compression**:
  - **Images**: Light (80%), Medium (60%), High (30%), 50% Downscale.
  - **Videos**: Fast H.264 compression with CRF presets & 720p scaling.
  - **Audio**: 64 kbps (podcast/voice), 128 kbps (standard), 192 kbps (high fidelity).
  - **PDF**: Stream deflation & aggressive image downsampling.
  - **Archives**: Deflate level 9 ZIP / GZIP.
- **⚡ Interactive UI**: Uses Telegram Inline Keyboards for one-tap format selection.
- **🧹 Automatic Resource Cleanup**: Isolated temporary folders per user task with automatic cleanup after upload.
- **📦 Zero External System Dependency on Windows**: Automatically bundles and discovers high-speed FFmpeg binary.

---

## 📁 Project Structure

```
telegram-file-converter-bot/
├── .env.example              # Sample environment configuration
├── .gitignore
├── README.md                 # Complete documentation
├── requirements.txt          # Python dependencies
├── run_bot.py                # Main bot launcher
├── test_converter.py         # Offline test runner for all conversion engines
└── bot/
    ├── __init__.py
    ├── config.py             # Configuration & environment loader
    ├── main.py               # Telegram bot application setup & handlers
    ├── converters/
    │   ├── __init__.py
    │   ├── dispatcher.py     # Central routing for conversions & compressions
    │   ├── image_converter.py
    │   ├── document_converter.py
    │   ├── audio_converter.py
    │   ├── video_converter.py
    │   ├── data_converter.py
    │   └── archive_converter.py
    ├── handlers/
    │   ├── __init__.py
    │   ├── start.py          # /start, /help, /formats commands
    │   ├── file_receiver.py  # Media & document upload handler
    │   ├── conversion_callback.py
    │   ├── compression_callback.py
    │   └── cancel.py         # Cancel, back, and file info handlers
    └── utils/
        ├── __init__.py
        ├── file_manager.py   # Temporary workspace management & cleanup
        ├── format_detector.py# Format detection & conversion mapping
        └── keyboard.py       # Inline keyboard builders
```

---

## 🌐 24/7 Deployment on Render

This repository includes a `Dockerfile` and built-in HTTP health check server specifically designed to run 24/7 on **Render.com**.

### Step 1: Push Code to GitHub
```bash
git init
git add .
git commit -m "Deploy AeroFormat Bot"
gh repo create AeroFormat-Bot --public --source=. --remote=origin --push
```

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** ➔ **Web Service**.
3. Connect your GitHub repository (`AeroFormat-Bot`).
4. Set the configuration:
   - **Environment**: `Docker` (Render automatically uses the included `Dockerfile`)
   - **Plan**: `Free`
5. Under **Environment Variables**, add:
   - `TELEGRAM_BOT_TOKEN` = `your_bot_token`
   - `MAX_FILE_SIZE_MB` = `50`
6. Click **Create Web Service**!

### Step 3: Keep 24/7 Online (No Sleep on Free Tier)
Render's free tier spins down after 15 minutes of no web requests. Since this bot has an embedded HTTP health server listening on `$PORT`:
1. Copy your Render web service URL (e.g. `https://aeroformat-bot.onrender.com`).
2. Go to a free monitor like [cron-job.org](https://cron-job.org) or [UptimeRobot](https://uptimerobot.com).
3. Set up a ping every **10 minutes** to your Render URL.
4. Your bot will now stay **permanently awake and operational 24/7** at zero cost!

---

### 1. Configure Bot Token
1. Open Telegram and message [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the prompts to choose a name and username.
3. Copy the HTTP API token provided by BotFather.
4. Create a `.env` file from the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```
5. Open `.env` and paste your bot token:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
   ```

### 2. Verify Conversion Engines (Offline Test)
You can test all conversion and compression engines immediately without starting Telegram polling:
```powershell
python test_converter.py
```

### 3. Launch the Bot
```powershell
python run_bot.py
```

---

## 💬 Bot Commands

| Command | Description |
| :--- | :--- |
| `/start` | Starts the bot and displays the welcome message and quick guide |
| `/help` | Shows detailed usage instructions and supported modes |
| `/formats` | Lists all supported input formats and target extensions |
| `/cancel` | Cancels the active file operation and clears session cache |

---

## 📊 Supported Conversions Matrix

| Input Category | Formats | Available Output Conversions |
| :--- | :--- | :--- |
| **Images** | `JPG`, `PNG`, `WEBP`, `BMP`, `TIFF`, `ICO`, `GIF` | `PNG`, `JPG`, `WEBP`, `BMP`, `TIFF`, `ICO`, `PDF` |
| **Documents** | `PDF` | `DOCX`, `TXT`, `Images (.ZIP)` |
| | `DOCX` | `PDF`, `TXT` |
| | `TXT` / `MD` | `PDF`, `DOCX` |
| | `CSV` | `XLSX`, `JSON`, `PDF` |
| | `XLSX` | `CSV`, `JSON` |
| **Audio** | `MP3`, `WAV`, `OGG`, `AAC`, `FLAC`, `M4A` | `MP3`, `WAV`, `OGG`, `AAC`, `FLAC`, `M4A` |
| **Video** | `MP4`, `MKV`, `AVI`, `MOV`, `WEBM`, `GIF` | `MP4`, `AVI`, `MKV`, `MOV`, `WEBM`, `GIF`, `MP3 (Audio Extract)` |
| **Data** | `JSON`, `YAML`, `XML`, `CSV` | `JSON`, `YAML`, `XML`, `CSV` |
| **Archives** | Any file or folder | `ZIP`, `TAR.GZ`, `TAR.BZ2` |
