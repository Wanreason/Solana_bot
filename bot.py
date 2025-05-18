import asyncio
from aiohttp import web

# Your existing imports
from fetchers.dexscreener import fetch_dexscreener_data
from filters import is_token_valid
from alert import send_alert

# --- Web server ping handler (for Railway/UptimeRobot) ---
async def handle_ping(request):
    return web.Response(text="OK")

# --- Your main bot loop ---
async def process_tokens():
    while True:
        print("🔍 Fetching tokens...")
        tokens = await fetch_dexscreener_data()
        for token in tokens:
            if await is_token_valid(token):
                await send_alert(token)
        await asyncio.sleep(60)

# --- Entry point: run both web server and bot loop concurrently ---
async def main():
    # Start aiohttp web server
    app = web.Application()
    app.add_routes([web.get('/', handle_ping)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    # Run token processor
    await process_tokens()

if __name__ == "__main__":
    asyncio.run(main())
