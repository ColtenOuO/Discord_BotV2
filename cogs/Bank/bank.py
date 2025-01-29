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
    @app_commands.command(name="transfer", description="轉帳給某個人")
    async def transfer(self, interaction: discord.Interaction, user: discord.Member, count: int, remark: str= "無任何備註訊息"):
        await interaction.response.defer()
        user1_balance = get_balance(interaction.user.id)
        result = "交易成功"
        fee = count // 20
        if user1_balance < count + fee: result = "交易失敗: 餘額不足！！！"
        if( count == 0 ): result = "交易失敗: 請不要轉 0 元給別人好嗎？？？"
        if( count < 0 ): 
            result = "交易失敗: 你以為這樣可以偷到錢嗎？？？"
            fee = 0
        embed = discord.Embed(title=f"{interaction.user.display_name} 轉帳給 {user.display_name} 共 {count} 元",colour=0xffd877)
        embed.set_author(name="轉帳資訊")
        embed.add_field(name="轉帳結果",value=f"**{result}**",inline=False)
        embed.add_field(name="手續費(5%)",value=f"**{fee} 元**",inline=False)
        embed.add_field(name="備註：",value=f"{remark}",inline=False)
        embed.set_thumbnail(url="https://i.imghippo.com/files/Oui4416ZY.png")

        if result == "交易成功":
            requests.post(f"http://127.0.0.1:8000/db/update/add/{interaction.user.id}/{-(count+fee)}")
            requests.post(f"http://127.0.0.1:8000/db/update/add/{user.id}/{count}")
        await interaction.followup.send(embed=embed) 


    @app_commands.command(name="leaderboard", description="查看此伺服器富有排行榜")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()

        members = [member for member in interaction.guild.members if not member.bot] 
        balances = []

        for member in members:
            balance = get_balance(member.id)
            balances.append((member, balance))
        sorted_balances = sorted(balances, key=lambda x: x[1], reverse=True)
        top_10 = sorted_balances[:10]

        embed = discord.Embed(title="🏆 伺服器富有排行榜", colour=0xFFD700)
        embed.set_thumbnail(url="https://i.imghippo.com/files/LiN2231aiQ.png")

        for index, (member, balance) in enumerate(top_10, start=1):
            embed.add_field(name=f"#{index} {member.display_name}", value=f"💰 {balance} 元", inline=False)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Bank(bot=bot))