# Simulated: Normally you'd use APIs like Syrax/SolanaFM for this
async def basic_safety_check(token):
    # Check mint authority removed and LP lock simulated
    base_token = token.get("baseToken", {})
    if "scam" in base_token.get("name", "").lower():
        return False  # crude scam filter
    return True
