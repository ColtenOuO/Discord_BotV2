import discord
import os
from discord.ext import commands
import asyncio
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

# load all python files in cogs
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
# load all app commands
async def load_appcommands():
    try:
        synced = await bot.tree.sync()  # all app_commands sync to Discord
        print(f"[OK]: Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"[FAIL]: Failed to sync commands: {e}")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)
        

if __name__ == "__main__":
    asyncio.run(main())