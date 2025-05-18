from datetime import datetime, timezone

def get_token_age_minutes(timestamp_ms):
    """
    Convert a millisecond timestamp to the age in minutes from current UTC time.
    """
    try:
        created_at = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        age_minutes = (datetime.now(timezone.utc) - created_at).total_seconds() / 60
        return round(age_minutes, 2)
    except Exception:
        return float('inf')  # Return very high age if invalid timestamp

def shorten_address(address):
    """
    Shorten a blockchain address for display: first 4 + ... + last 4 chars.
    """
    if not address or len(address) < 10:
        return address or "N/A"
    return f"{address[:4]}...{address[-4:]}"

def format_usd(amount):
    """
    Format a number as USD currency with commas, no decimals.
    """
    try:
        return f"${amount:,.0f}"
    except Exception:
        return "$0"
