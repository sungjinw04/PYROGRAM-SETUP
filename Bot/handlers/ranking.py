from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pymongo import MongoClient
from Bot.config import MONGO_URL

# Initialize MongoDB client and connect to the database
client = MongoClient(MONGO_URL)
db = client['telegram_bot']
messages_collection = db['message_counts']

@app.on_message(filters.command("rank") & filters.group)
async def show_rank_interface(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Overall Ranking", callback_data="overall_ranking")],
        [InlineKeyboardButton("Weekly Ranking", callback_data="weekly_ranking")],
        [InlineKeyboardButton("Daily Ranking", callback_data="daily_ranking")],
    ])
    await message.reply("Select a ranking type:", reply_markup=keyboard)

def generate_rank_text(chat_id, time_frame=None):
    top_users = get_top_users(chat_id, time_frame)
    if not top_users:
        return "No data available."

    rank_text = "Top 10 Chatters:\n\n"
    for i, user in enumerate(top_users):
        message_count = user.get('message_count', 0)
        rank_text += f"{i + 1}. User ID: {user['user_id']} - Messages: {message_count}\n"

    return rank_text

@app.on_callback_query(filters.regex(r"overall_ranking"))
async def overall_ranking(client, query):
    chat_id = query.message.chat.id
    rank_text = generate_rank_text(chat_id)
    await query.message.edit_text(rank_text)

@app.on_callback_query(filters.regex(r"weekly_ranking"))
async def weekly_ranking(client, query):
    chat_id = query.message.chat.id
    rank_text = generate_rank_text(chat_id, time_frame='weekly')
    await query.message.edit_text(rank_text)

@app.on_callback_query(filters.regex(r"daily_ranking"))
async def daily_ranking(client, query):
    chat_id = query.message.chat.id
    rank_text = generate_rank_text(chat_id, time_frame='daily')
    await query.message.edit_text(rank_text)

def get_top_users(chat_id, time_frame=None):
    # Modify query based on time_frame (e.g., for weekly or daily ranking)
    query = {"chat_id": chat_id}

    # Sort by message_count and limit to top 10
    top_users = messages_collection.find(query).sort("message_count", -1).limit(10)
    return list(top_users)

