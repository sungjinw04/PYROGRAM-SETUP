import time
from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Bot import app

# Assuming you have a MongoDB connection setup to store message counts
from pymongo import MongoClient

client = MongoClient('your_mongo_db_connection_string')
db = client['telegram_bot']
messages_collection = db['message_counts']

# /rank command
@app.on_message(filters.command("rank") & filters.group)
async def rank_command(client, message: Message):
    chat_id = message.chat.id
    overall_ranking = get_overall_ranking(chat_id)
    
    buttons = [
        [InlineKeyboardButton("Overall Ranking", callback_data=f"overall_{chat_id}")],
        [InlineKeyboardButton("Weekly Ranking", callback_data=f"weekly_{chat_id}")],
        [InlineKeyboardButton("Daily Ranking", callback_data=f"daily_{chat_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_text(
        f"Overall message count in this group: {overall_ranking['total']}\n\nTop 10 Chatters:\n{format_ranking(overall_ranking['top_10'])}",
        reply_markup=reply_markup
    )

# Function to get overall ranking
def get_overall_ranking(chat_id):
    pipeline = [
        {"$match": {"chat_id": chat_id}},
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_10 = list(messages_collection.aggregate(pipeline))
    total_messages = sum([user['count'] for user in top_10])
    return {"total": total_messages, "top_10": top_10}

# Function to format the ranking data
def format_ranking(top_10):
    ranking_text = ""
    for i, user in enumerate(top_10, start=1):
        ranking_text += f"{i}. User {user['_id']}: {user['count']} messages\n"
    return ranking_text

# Callback for buttons
@app.on_callback_query(filters.regex(r"^(overall|weekly|daily)_(\d+)$"))
async def rank_callback(client, callback_query):
    chat_id = int(callback_query.data.split("_")[1])
    rank_type = callback_query.data.split("_")[0]

    if rank_type == "overall":
        ranking = get_overall_ranking(chat_id)
    elif rank_type == "weekly":
        ranking = get_period_ranking(chat_id, period="week")
    else:
        ranking = get_period_ranking(chat_id, period="day")

    await callback_query.message.edit_text(
        f"{rank_type.capitalize()} message count in this group: {ranking['total']}\n\nTop 10 Chatters:\n{format_ranking(ranking['top_10'])}"
    )

# Function to get ranking for a specific period (week or day)
def get_period_ranking(chat_id, period):
    now = datetime.now()
    if period == "week":
        start_time = now - timedelta(days=now.weekday())  # Start of the week
    elif period == "day":
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)  # Start of the day
    
    pipeline = [
        {"$match": {"chat_id": chat_id, "timestamp": {"$gte": start_time}}},
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_10 = list(messages_collection.aggregate(pipeline))
    total_messages = sum([user['count'] for user in top_10])
    return {"total": total_messages, "top_10": top_10}

