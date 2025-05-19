import os
from dotenv import load_dotenv

load_dotenv()

# Telegram bot credentials
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Filter thresholds
MIN_VOLUME = 5000  # Minimum 24h trading volume in USD
MIN_LIQUIDITY = 3000  # Minimum liquidity in USD
MAX_BUY_TAX = 10  # Max acceptable buy tax (%)
MAX_SELL_TAX = 10  # Max acceptable sell tax (%)
REQUIRED_TOKEN_AGE_MINUTES = 10  # Minimum token age in minutes

# Blacklisted words (token names or descriptions)
BLACKLISTED_WORDS = [
    "rug", "scam", "honeypot", "slow", "steal", "hack", "drain", "exit", "rekt",
    "sniper", "bot", "kill", "trap"
]

# Emojis for alert formatting (optional aesthetic improvement)
EMOJIS = {
    "check": "✅",
    "cross": "❌",
    "chart": "📈",
    "warning": "⚠️",
    "fire": "🔥",
    "money": "💰",
    "clock": "⏰",
}
