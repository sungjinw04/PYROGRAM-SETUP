import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from Bot import app  # Ensure this matches your import path for the `app` object
from config import adminlist
from Bot.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from Bot.utils.decorators.language import language  # Update with your decorators path
from Bot.utils.formatters import alpha_to_int  # Update with your formatters path

IS_BROADCASTING = False

# Handler for the /bcast command
@app.on_message(filters.command("bcast") & filters.user(SUDOERS))
@language  # Assuming this decorator handles language translations
async def broadcast_message(client, message, _):
    global IS_BROADCASTING
    if IS_BROADCASTING:
        return await message.reply_text(_["broad_9"])  # Prevent concurrent broadcasts

    # Determine if message is a reply or text input
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        query = message.text.split(None, 1)[1]
        # Remove special commands from query text
        for flag in ["-pin", "-nobot", "-pinloud", "-assistant", "-user"]:
            query = query.replace(flag, "")
        if query.strip() == "":
            return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    # Broadcast to group chats
    if "-nobot" not in message.text:
        await broadcast_to_chats(message, x, y, query, _)

    # Broadcast to served users
    if "-user" in message.text:
        await broadcast_to_users(message, x, y, query, _)

    # Broadcast via assistant accounts
    if "-assistant" in message.text:
        await broadcast_via_assistants(message, x, y, query, _)

    IS_BROADCASTING = False

async def broadcast_to_chats(message, x, y, query, _):
    sent, pin = 0, 0
    schats = await get_served_chats()
    for chat in schats:
        chat_id = int(chat["chat_id"])
        try:
            m = (
                await app.forward_messages(chat_id, y, x)
                if message.reply_to_message
                else await app.send_message(chat_id, text=query)
            )
            if "-pin" in message.text:
                try:
                    await m.pin(disable_notification=True)
                    pin += 1
                except:
                    continue
            elif "-pinloud" in message.text:
                try:
                    await m.pin(disable_notification=False)
                    pin += 1
                except:
                    continue
            sent += 1
            await asyncio.sleep(0.2)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except:
            continue
    await message.reply_text(_["broad_3"].format(sent, pin))

async def broadcast_to_users(message, x, y, query, _):
    susr = 0
    susers = await get_served_users()
    for user in susers:
        user_id = int(user["user_id"])
        try:
            await app.forward_messages(user_id, y, x) if message.reply_to_message else await app.send_message(user_id, text=query)
            susr += 1
            await asyncio.sleep(0.2)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except:
            pass
    await message.reply_text(_["broad_4"].format(susr))

async def broadcast_via_assistants(message, x, y, query, _):
    aw = await message.reply_text(_["broad_5"])
    text = _["broad_6"]
    from Bot.core.userbot import assistants  # Ensure this matches your import path

    for num in assistants:
        sent = 0
        client = await get_client(num)
        async for dialog in client.get_dialogs():
            try:
                if message.reply_to_message:
                    await client.forward_messages(dialog.chat.id, y, x)
                else:
                    await client.send_message(dialog.chat.id, text=query)
                sent += 1
                await asyncio.sleep(3)
            except FloodWait as fw:
                await asyncio.sleep(fw.value)
            except:
                continue
        text += _["broad_7"].format(num, sent)
    await aw.edit_text(text)

# Automatically cleans admin list every 10 seconds
async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue

asyncio.create_task(auto_clean())

