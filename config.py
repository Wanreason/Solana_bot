import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MIN_VOLUME = 5000      # Minimum trading volume to consider (USD)
MIN_LIQUIDITY = 5000   # Minimum liquidity pool value to consider (USD)
