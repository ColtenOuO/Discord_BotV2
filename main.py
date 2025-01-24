import discord
import os
from threading import Thread
from discord.ext import commands
import asyncio
from api.api import start_api 
from config import TOKEN
from config import APPLICATION_ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = "%", intents = intents, application_id=APPLICATION_ID)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await load_appcommands()

@bot.command()
async def reload(ctx, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"ReLoaded {extension} done.")
@bot.command()
async def shutdown(ctx):
    await ctx.send("Shutting down the bot...")
    await bot.close()

# load all python files in cogs
async def load_extensions():
    for root, _, files in os.walk("./cogs"):
        for file in files:
            if file.endswith(".py"):
                relative_path = os.path.relpath(os.path.join(root, file), "./cogs")
                module_path = "cogs." + relative_path.replace(os.sep, ".")[:-3]
                try:
                    await bot.load_extension(module_path)
                    print(f"[OK]: Loaded {module_path}")
                except Exception as e:
                    print(f"[FAIL]: Failed to load {module_path}: {e}")

# load all app commands
async def load_appcommands():
    try:
        synced = await bot.tree.sync()  # all app_commands sync to Discord
        print(f"[OK]: Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"[FAIL]: Failed to sync commands: {e}")


async def main():
    async with bot:
        api_thread = Thread(target=start_api, daemon=True)
        api_thread.start()
        await load_extensions()
        await bot.start(TOKEN)
        

if __name__ == "__main__":
    asyncio.run(main())