from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Bot.config import MONGO_URL
from Bot import app
from pymongo import MongoClient
from datetime import datetime, timedelta

# Set up MongoDB connection
client = MongoClient(MONGO_URL)
db = client['telegram_bot']
messages_collection = db['message_counts']

def get_top_users(chat_id, time_frame=None):
    query = {"chat_id": chat_id}
    if time_frame:
        query["last_message"] = {"$gte": time_frame}

    users = list(messages_collection.find(query).sort("message_count", -1).limit(10))
    return users

def generate_rank_text(chat_id, time_frame=None):
def generate_rank_text(chat_id, time_frame=None):
    top_users = get_top_users(chat_id, time_frame)
    if not top_users:
        return "No data available."

    rank_text = "Top 10 Chatters:\n\n"
    for i, user in enumerate(top_users):
        message_count = user.get('message_count', 0)  # Safely get message_count
        rank_text += f"{i + 1}. User ID: {user['user_id']} - Messages: {message_count}\n"

    return rank_text


@app.on_message(filters.command("rank") & filters.group)
async def rank_command(client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Overall Ranking", callback_data="overall_ranking")],
        [InlineKeyboardButton("Weekly Ranking", callback_data="weekly_ranking")],
        [InlineKeyboardButton("Daily Ranking", callback_data="daily_ranking")]
    ])

    await message.reply_text("Select ranking type:", reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"overall_ranking"))
async def overall_ranking(client, callback_query):
    chat_id = callback_query.message.chat.id
    rank_text = generate_rank_text(chat_id)
    await callback_query.message.edit_text(rank_text)

@app.on_callback_query(filters.regex(r"weekly_ranking"))
async def weekly_ranking(client, callback_query):
    chat_id = callback_query.message.chat.id
    one_week_ago = datetime.utcnow() - timedelta(weeks=1)
    rank_text = generate_rank_text(chat_id, one_week_ago)
    await callback_query.message.edit_text(rank_text)

@app.on_callback_query(filters.regex(r"daily_ranking"))
async def daily_ranking(client, callback_query):
    chat_id = callback_query.message.chat.id
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    rank_text = generate_rank_text(chat_id, today_start)
    await callback_query.message.edit_text(rank_text)

