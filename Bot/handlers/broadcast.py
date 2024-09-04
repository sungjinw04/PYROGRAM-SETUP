from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
import asyncio
from .. import app, BOT_OWNER

# Handler for the /bcast command
@app.on_message(filters.command("bcast") & filters.user(BOT_OWNER))
async def broadcast_message(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text("Please reply to a message or provide a text to broadcast.")
        return

    # Get the message to broadcast
    if message.reply_to_message:
        broadcast_text = message.reply_to_message.text
    else:
        broadcast_text = message.text.split(maxsplit=1)[1]

    # Use async for to iterate over all group chats the bot is in
    async for dialog in app.get_dialogs():
        if dialog.chat.type in ("group", "supergroup"):
            try:
                await app.send_message(chat_id=dialog.chat.id, text=broadcast_text)
                await asyncio.sleep(0.5)  # Sleep to avoid hitting Telegram's flood limits
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Failed to send message in {dialog.chat.title}: {e}")

    await message.reply_text("Broadcast completed.")

# Only the bot owner can use the /bcast command
@app.on_message(filters.command("bcast") & ~filters.user(BOT_OWNER))
async def unauthorized_bcast(client: Client, message: Message):
    await message.reply_text("You are not authorized to use this command.")
    
