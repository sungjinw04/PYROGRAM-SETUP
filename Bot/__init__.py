import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from .config import api_id, api_hash, bot_token, OWNER_ID as BOT_OWNER
import sys



loop = asyncio.get_event_loop()

# Pyrogram Client instance
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# In-memory set to store group chat IDs (use a database in production)
app.group_chat_ids = set()

StartTime = time.time()
BOT_ID: int = 0
BOT_USERNAME: str = ""
MENTION_BOT: str = ""

async def get_readable_time(seconds: int) -> str:
    time_string = ""
    if seconds < 0:
        raise ValueError("Input value must be non-negative")

    if seconds < 60:
        time_string = f"{round(seconds)}s"
    else:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        if days > 0:
            time_string += f"{round(days)}days, "
        if hours > 0:
            time_string += f"{round(hours)}h:"
        time_string += f"{round(minutes)}m:{round(seconds):02d}s"

    return time_string
  
# Track group chat IDs when the bot is added or removed
@app.on_chat_member_updated()
async def track_group_chats(client: Client, message: Message):
    if message.chat.type in ("group", "supergroup"):
        if message.new_chat_member and message.new_chat_member.is_self:
            app.group_chat_ids.add(message.chat.id)
        elif message.left_chat_member and message.left_chat_member.is_self:
            app.group_chat_ids.discard(message.chat.id)

async def init_bot():
    global BOT_NAME, BOT_USERNAME, BOT_ID, MENTION_BOT, JOINED_USERS
    print("Connecting to the Telegram API...")
    try:
        await app.start()
        print("Connected")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    details = await app.get_me()
    BOT_ID = details.id
    BOT_USERNAME = details.username
    BOT_NAME = details.first_name
    MENTION_BOT = details.mention

    print(
        f"Your Bot Info:\n‣ Bot ID: {BOT_ID}\n‣ Bot Name: {BOT_NAME}\n‣ Bot Username: {BOT_USERNAME}"
    )

async def main():
    await init_bot()

loop.run_until_complete(main())

