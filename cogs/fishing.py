import discord
import json
from discord.ext import commands
from discord import app_commands 


class Fishing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open("./cogs/responses.json", "r", encoding="utf-8") as file:
            self.responses = json.load(file)
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        response = self.responses.get(message.content)
        if response:
            await message.channel.send(response)
    @app_commands.command(name="ping", description="跟機器人一起吵鬧")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 我好吵。")
       

async def setup(bot):
    await bot.add_cog(Fishing(bot=bot))