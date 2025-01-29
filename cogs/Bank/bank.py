import discord
import json
import requests
import datetime
import random
from discord.ext import commands
from discord import app_commands
from api.routers.db import get_balance

class Embed:
    def __init__(self):
        pass
    def balance(self, balance: int, name: str, image_url: str):
        embed = discord.Embed(title=f"{name} 的戶頭資訊",colour=0xf5ec00)
        embed.set_author(name="銀行戶頭資訊")
        embed.add_field(name=f"目前餘額",value=f"{balance} 元",inline=False)
        embed.set_thumbnail(url="https://i.imghippo.com/files/KvCA9823vhI.png")
        embed.set_image(url=f"{image_url}")
        return embed

class Bank(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(name="bank_balance", description="查詢自己的銀行戶頭餘額")
    async def balance(self, interaction: discord.Interaction):
        balance = get_balance(interaction.user.id)
        embed = Embed()
        avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
        await interaction.response.send_message(embed=embed.balance(balance, interaction.user.display_name, avatar_url))

async def setup(bot):
    await bot.add_cog(Bank(bot=bot))