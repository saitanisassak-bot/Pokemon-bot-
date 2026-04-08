import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message
import config
import database as db

# Initialize Pyrogram Client
app = Client(
    "PokemonBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# --- WEB SERVER FOR RENDER (Keeps bot alive) ---
async def handle_ping(request):
    return web.Response(text="Bot is running! 🚀")

async def start_web_server():
    server = web.Application()
    server.router.add_get('/', handle_ping)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', config.PORT)
    await site.start()
    print(f"Web server started on port {config.PORT}")

# --- BOT HANDLERS ---

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await db.create_new_user(message.from_user.id)
        await message.reply_text("Welcome to the Pokemon World! 🌍 Here are your starter Pokeballs!")
    else:
        await message.reply_text("Welcome back, Trainer! Ready to catch some Pokemon?")

# --- GOD MODE COMMANDS (Admins Only) ---

@app.on_message(filters.command("give_item") & filters.user(config.ADMINS))
async def god_give_item(client: Client, message: Message):
    try:
        args = message.text.split()
        target_id = int(args[1])
        item_name = args[2] # e.g., master_ball
        amount = int(args[3])
        
        await db.give_item(target_id, item_name, amount)
        await message.reply_text(f"✨ God Mode: Gave {amount}x {item_name} to {target_id}!")
    except Exception as e:
        await message.reply_text("🤧 Format: `/give_item [user_id] [item_name] [amount]`")

@app.on_message(filters.command("make_gym_leader") & filters.user(config.ADMINS))
async def god_make_gym(client: Client, message: Message):
    try:
        target_id = int(message.command[1])
        await db.set_gym_leader(target_id, True)
        await message.reply_text("🏆 Boom. They are now an official Gym Leader!")
    except Exception:
        await message.reply_text("🤧 Format: `/make_gym_leader [user_id]`")

# --- MAIN LOOP ---

async def main():
    # Start web server first
    await start_web_server()
    # Start bot
    print("Bot is starting...")
    await app.start()
    # Keep the script running
    await pyrogram.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
