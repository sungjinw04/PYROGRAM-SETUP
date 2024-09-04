import asyncio
import importlib
import os

from Bot.handlers import MODULES_PATH
from rich.console import Console
from pyrogram import idle

loop = asyncio.get_event_loop()
IMPORTED = {}


LOG = Console()

async def main():
    # from .modules.waifu_dropper import character_cache
    LOG.print(f"[bold yellow]Loading {len(MODULES_PATH)} Modules")
    for module in MODULES_PATH:
        mod = module.replace(os.getcwd(),"")[1:].replace('/','.').replace(".py",'')
        LOG.print(f"[bold cyan]{mod.split('.')[-1]}")
        
        importlib.import_module(mod)

    # if os.path.exists("./waifu_cache.json"):
    #     with open("./waifu_cache.json", "r") as f:
    #         data = json.load(f)
    #         print(data)
    #         character_cache.update(data)
    #         os.remove("./waifu_cache.json")
          
    print("✨ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ")

    await idle()
    # with open("./waifu_cache.json", "w") as file:
    #     json.dump(character_cache, file)
    print("ᴄᴀɴᴄᴇʟɪɴɢ ᴀʟʟ ᴛᴀsᴋs.")


if __name__ == "__main__":
    loop.run_until_complete(main())
    
