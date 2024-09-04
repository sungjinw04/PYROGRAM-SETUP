from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
import asyncio
from .. import app, BOT_OWNER  # Import the app instance and BOT_OWNER from __init__.py

# Handler for the /bcast command
@app.on_message(filters.command("bcast") & filters.user(BOT_OWNER))
async def broadcast_message(client: Client, message: Message):
    print("Broadcast command received")  # Debugging
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text("Please reply to a message or provide text to broadcast.")
        return

    # Get the message to broadcast
    broadcast_text = message.reply_to_message.text if message.reply_to_message else message.text.split(maxsplit=1)[1]

    # Iterate over stored group chat IDs
    for chat_id in app.group_chat_ids:
        print(f"Sending to {chat_id}")  # Debugging
        try:
            await app.send_message(chat_id=chat_id, text=broadcast_text)
            await asyncio.sleep(0.5)  # Sleep to avoid hitting Telegram's flood limits
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"Failed to send message in chat {chat_id}: {e}")

    await message.reply_text("Broadcast completed.")
    print("Broadcast completed.")  # Debugging

