from pyrogram import filters
from pyrogram.types import Message, InputMediaPhoto
from Bot import app

# Function to send an animated butterfly
async def send_butterfly_animation(chat_id):
    butterfly_animation = [
        "🦋", "🌸", "🦋", "🌸", "🦋", "🌸", "🦋", "🌸", "🦋", "🌸"
    ]
    for frame in butterfly_animation:
        await app.send_message(chat_id, frame)
        await asyncio.sleep(0.5)

# Command handler for /start
@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    chat_id = message.chat.id

    # Send butterfly animation
    await send_butterfly_animation(chat_id)

    # Send the image as an interface
    await app.send_photo(chat_id, "https://telegra.ph/file/d83a2cf2bd0dd868f37ae.jpg")

    # Send a welcome message
    await app.send_message(chat_id, "wlcm to Sung Network")

# Ensure that this file's functions are imported when the bot starts
if __name__ == "__main__":
    app.run()

