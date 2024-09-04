from Bot import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient
from Bot.config import MONGO_URL

# Initialize MongoDB client
client = MongoClient(MONGO_URL)
db = client["message_count_db"]
collection = db["message_count"]

def generate_rank_text(chat_id, time_filter=None):
    query = {"chat_id": chat_id}
    if time_filter:
        query["timestamp"] = {"$gte": time_filter}

    top_users = collection.find(query).sort("message_count", -1).limit(10)
    rank_text = f"Top 10 chatters:\n\n"
    for i, user in enumerate(top_users):
        rank_text += f"{i + 1}. User ID: {user['user_id']} - Messages: {user.get('message_count', 0)}\n"
    return rank_text

@app.on_message(filters.command("rank") & filters.group)
async def rank_command(client, message):
    chat_id = message.chat.id

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Overall Ranking", callback_data="overall_rank")],
        [InlineKeyboardButton("Weekly Ranking", callback_data="weekly_rank")],
        [InlineKeyboardButton("Daily Ranking", callback_data="daily_rank")]
    ])

    await message.reply("Choose a ranking option:", reply_markup=keyboard)

@app.on_callback_query(filters.regex("overall_rank"))
async def overall_ranking(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    rank_text = generate_rank_text(chat_id)
    await query.message.edit_text(rank_text)

@app.on_callback_query(filters.regex("weekly_rank"))
async def weekly_ranking(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    # Filter messages from the past week
    time_filter = int(time.time()) - 7 * 24 * 60 * 60
    rank_text = generate_rank_text(chat_id, time_filter)
    await query.message.edit_text(rank_text)

@app.on_callback_query(filters.regex("daily_rank"))
async def daily_ranking(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    # Filter messages from the past day
    time_filter = int(time.time()) - 24 * 60 * 60
    rank_text = generate_rank_text(chat_id, time_filter)
    await query.message.edit_text(rank_text)

