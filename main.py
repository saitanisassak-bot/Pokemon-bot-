import asyncio
from aiohttp import web
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
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
    bot = await client.get_me()
    
    # The "Add me to Group" button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add to a Group ➕", url=f"t.me/{bot.username}?startgroup=true")]
    ])

    if message.chat.type == enums.ChatType.PRIVATE:
        # User started bot in DM
        user = await db.get_user(message.from_user.id)
        if not user:
            await db.create_new_user(message.from_user.id)
            await message.reply_text("Welcome to the Pokemon World! 🌍 Here are your starter Pokeballs!", reply_markup=keyboard)
            
            # Send Log to Channel
            log_text = f"🆕 **New Trainer Registered!**\n**ID:** `{message.from_user.id}`\n**Name:** {message.from_user.first_name}\n**Username:** @{message.from_user.username}"
            try:
                await client.send_message(config.LOG_CHANNEL, log_text)
            except Exception:
                pass
        else:
            await message.reply_text("Welcome back, Trainer! Ready to catch some Pokemon?", reply_markup=keyboard)
            
    elif message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        # Bot added to a group or someone typed /start in a group
        await db.add_group(message.chat.id, message.chat.title)
        await message.reply_text("Thanks for adding me! A wild Pokemon might appear soon... 👀", reply_markup=keyboard)
        
        # Send Log to Channel
        log_text = f"🏘️ **Added to New Group!**\n**ID:** `{message.chat.id}`\n**Title:** {message.chat.title}"
        try:
            await client.send_message(config.LOG_CHANNEL, log_text)
        except Exception:
            pass 


# --- GOD MODE / ADMIN COMMANDS ---

@app.on_message(filters.command("give_item") & filters.user(config.ADMINS))
async def god_give_item(client: Client, message: Message):
    try:
        args = message.text.split()
        target_id = int(args[1])
        item_name = args[2] # e.g., master_ball
        amount = int(args[3])
        
        await db.give_item(target_id, item_name, amount)
        await message.reply_text(f"✨ God Mode: Gave {amount}x {item_name} to {target_id}!")
    except Exception:
        await message.reply_text("🤧 Format: `/give_item [user_id] [item_name] [amount]`")


@app.on_message(filters.command("make_gym_leader") & filters.user(config.ADMINS))
async def god_make_gym(client: Client, message: Message):
    try:
        target_id = int(message.command[1])
        await db.set_gym_leader(target_id, True)
        await message.reply_text("🏆 Boom. They are now an official Gym Leader!")
    except Exception:
        await message.reply_text("🤧 Format: `/make_gym_leader [user_id]`")


@app.on_message(filters.command("stats") & filters.user(config.ADMINS))
async def stats_cmd(client: Client, message: Message):
    msg = await message.reply_text("🔄 Fetching stats...")
    users = await db.count_users()
    groups = await db.count_groups()
    
    text = (
        f"📊 **Pokemon Bot Stats**\n\n"
        f"👥 **Total Trainers:** `{users}`\n"
        f"🏘️ **Total Groups:** `{groups}`"
    )
    await msg.edit_text(text)


@app.on_message(filters.command("broadcast") & filters.user(config.ADMINS))
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("🤧 Please reply to a message you want to broadcast!")

    msg = await message.reply_text("🚀 Broadcasting started... This might take a while.")
    user_ids = await db.get_all_user_ids()
    
    success = 0
    failed = 0

    for user_id in user_ids:
        try:
            # .copy() sends the exact message (with buttons/images)
            await message.reply_to_message.copy(user_id)
            success += 1
            await asyncio.sleep(0.05) # Crucial: Prevents FloodWait bans
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(user_id)
            success += 1
        except Exception:
            # Usually means the user blocked the bot or deleted their account
            failed += 1

    await msg.edit_text(f"✅ **Broadcast Complete!**\n\n📩 Sent: `{success}`\n🚫 Failed (Blocked/Deleted): `{failed}`")


# --- MAIN LOOP ---

async def main():
    # Start web server first
    await start_web_server()
    # Start bot
    print("Bot is starting...")
    await app.start()
    # Keep the script running
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
