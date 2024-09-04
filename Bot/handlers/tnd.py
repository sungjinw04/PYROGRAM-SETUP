import random
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import the app instance from the bot's __init__.py
from .. import app

# List of truth questions and dare tasks
TRUTH_QUESTIONS = [
    "What’s the most inappropriate time you’ve ever had a lustful thought?",
    "Have you ever had a naughty dream about someone here?",
    "What's the wildest fantasy you've ever had?",
    "Who here do you find the most attractive?",
    "Have you ever lied to get someone into bed?",
    # Add more questions to reach 200...
]

DARE_TASKS = [
    "Send a flirty message to your last chat.",
    "Do a seductive dance for 1 minute and share a video.",
    "Imitate your sexiest voice and send a voice note.",
    "Confess a lustful secret to someone in this chat.",
    "Post a suggestive picture (within limits).",
    # Add more dares to reach 200...
]

@app.on_message(filters.command("tnd"))
async def truth_or_dare(client, message):
    emojis = ["💀", "☠️"]
    
    # Send the initial animated emoji cycle
    emoji_msg = await message.reply(emojis[0])
    for i in range(1):  # Cycle 3 times
        for emoji in emojis:
            # Change the message content slightly to avoid MESSAGE_NOT_MODIFIED error
            await asyncio.sleep(1.25)  # Increased delay to 1.5 seconds
            await emoji_msg.edit_text(f"{emoji} {i+1}")

    # Edit the message to ask the user to choose Truth or Dare
    await emoji_msg.edit_text("choose.....☠️🥷")
    
    # Create the inline keyboard with Truth and Dare buttons
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Truth ☠️", callback_data="truth")],
            [InlineKeyboardButton("Dare 💀", callback_data="dare")]
        ]
    )
    
    # Send the message with the keyboard
    choose_msg = await message.reply("What will it be?", reply_markup=keyboard)

@app.on_callback_query(filters.regex("truth|dare"))
async def handle_choice(client, callback_query):
    choice = callback_query.data
    if choice == "truth":
        question = random.choice(TRUTH_QUESTIONS)
        await callback_query.message.reply(f"Truth ☠️: {question}")
    elif choice == "dare":
        dare = random.choice(DARE_TASKS)
        await callback_query.message.reply(f"Dare 💀: {dare}")
    
    # Delete the interactive messages (emoji, text, buttons)
    await callback_query.message.delete()
    await callback_query.answer()  # Close the button after it's clicked

