from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
import asyncio

# Replace with your app instance and owner ID
app = Client("my_bot")
BOT_OWNER = 1886390680  # Replace with the actual Bot Owner ID

# In-memory set to store group chat IDs (use a database in production)
group_chat_ids = set()

# Handler to add groups to the list when the bot is added
@app.on_chat_member_updated()
async def track_group_chats(client: Client, message: Message):
    if message.chat.type in ("group", "supergroup"):
        if message.new_chat_member and message.new_chat_member.is_self:
            group_chat_ids.add(message.chat.id)
        elif message.left_chat_member and message.left_chat_member.is_self:
            group_chat_ids.discard(message.chat.id)

# Handler for the /bcast command
@app.on_message(filters.command("bcast") & filters.user(BOT_OWNER))
async def broadcast_message(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text("Please reply to a message or provide a text to broadcast.")
        return

    # Get the message to broadcast
    broadcast_text = message.reply_to_message.text if message.reply_to_message else message.text.split(maxsplit=1)[1]

    # Iterate over stored group chat IDs
    for chat_id in group_chat_ids:
        try:
            await app.send_message(chat_id=chat_id, text=broadcast_text)
            await asyncio.sleep(0.5)  # Sleep to avoid hitting Telegram's flood limits
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"Failed to send message in chat {chat_id}: {e}")

    await message.reply_text("Broadcast completed.")

# Only the bot owner can use the /bcast command
@app.on_message(filters.command("bcast") & ~filters.user(BOT_OWNER))
async def unauthorized_bcast(client: Client, message: Message):
    await message.reply_text("You are not authorized to use this command.")

