import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bot.main import run

if __name__ == "__main__":
    run()
