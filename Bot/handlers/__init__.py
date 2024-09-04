import os
from typing import Tuple, List
        

def get_all_modules(dirname: str) -> Tuple[List[str]]:
    """
    Recursively searches for Python module files within the specified directory and its subdirectories.
    This function scans the specified directory and its subdirectories for files with a `.py` extension,
    excluding the `__init__.py` files. It returns a tuple containing two lists: one containing the full paths
    of the discovered Python module files, and another containing the module names (without the `.py` extension).
    Parameters:
        dirname (str): The directory path to search for Python module files.
    Returns:
        Tuple[List[str]]: A tuple containing two lists. The first list contains the full paths of the discovered
        Python module files, and the second list contains the module names (without the `.py` extension).
    """
    modules_path = []
    module_names = []
    for root, _, files in os.walk(dirname):
        for file in files:
            if os.path.splitext(file)[1] == ".py" and file != "__init__.py":
                modules_path.append(os.path.join(root, file))
                module_names.append(file[:-3])

    return module_names , modules_path

from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.types import Message
from Bot import app
from .config import MONGO_URL

# Set up MongoDB connection
client = MongoClient(MONGO_URL)
db = client['telegram_bot']
messages_collection = db['message_counts']

@app.on_message(filters.group)
async def count_messages(client, message: Message):
    if message.from_user and message.chat:
        result = messages_collection.update_one(
            {
                "chat_id": message.chat.id,
                "user_id": message.from_user.id,
            },
            {
                "$inc": {"message_count": 1},
                "$set": {"last_message": message.date}
            },
            upsert=True
        )



ALL_MODULES, MODULES_PATH = get_all_modules(os.path.dirname(__file__))

# Add ranking module manually if it's not being picked up automatically
if 'ranking' not in ALL_MODULES:
    ALL_MODULES.append('ranking')
    MODULES_PATH.append(os.path.join(os.path.dirname(__file__), 'ranking.py'))

