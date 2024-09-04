from pyrogram import filters
from pyrogram.types import Message
from Bot import app

# Points system based on dice roll
def calculate_points(dice_value: int) -> int:
    points = {
        1: 10,
        2: 20,
        3: 30,
        4: 40,
        5: 50,
        6: 60
    }
    return points.get(dice_value, 0)

# Command handler for /roll
@app.on_message(filters.command("roll") & filters.group)
async def roll_dice(client, message: Message):
    chat_id = message.chat.id

    # Send an animated dice emoji
    await app.send_message(chat_id, "🎲 Rolling the dice...")

    # Send the animated dice
    dice_message = await app.send_dice(chat_id)
    dice_value = dice_message.dice.value

    # Calculate the points based on dice value
    points = calculate_points(dice_value)

    # Send the score message
    await app.send_message(chat_id, f"You rolled a {dice_value} and earned {points} points!")

# Ensure that this file's functions are imported when the bot starts
if __name__ == "__main__":
    app.run()

