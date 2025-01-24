import discord
import json
import requests
import datetime
import random
from discord.ext import commands
from discord import app_commands 


class Fishing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open("./cogs/Fishing/responses.json", "r", encoding="utf-8") as file:
            self.responses = json.load(file)
    def fish_embed_generator(self, discord_mention:str, fish_name: str, fish_level: str, fish_description: str):
        
        embed = discord.Embed(title=f"{fish_name}",
                      description=f"{fish_description}",
                      colour=0x00b0f4,
                      timestamp=datetime.datetime.now()
                      )
        embed.set_author(name=f"你釣起了一隻魚！！")
        embed.add_field(name="等級",value=f"{fish_level}",inline=False)
        embed.add_field(name="價格",value=f"{random.randint(0,100)} 元",inline=False)
        embed.set_thumbnail(url="https://i.imghippo.com/files/ntuW9239iso.webp")
        return embed
    
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
    @app_commands.command(name="fishing", description="釣一隻魚")
    async def fishing(self, interaction: discord.Interaction):
        url = "http://127.0.0.1:8000/fishing/random_fish"
        response = requests.get(url)
        if response.status_code == 200:
            random_fish = response.json()
            fish_name = random_fish['name']
            fish_level = random_fish['level']
            fish_description = random_fish['description']
            user_mention = interaction.user.mention
            print([fish_name, fish_level, fish_description])
            await interaction.response.send_message(embed=self.fish_embed_generator(user_mention, fish_name, fish_level, fish_description))
        else:
            await interaction.response.send_message("api 掛ㄌ，需要修復...")



async def setup(bot):
    await bot.add_cog(Fishing(bot=bot))