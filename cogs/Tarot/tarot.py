import discord
import json
import requests
from io import BytesIO
import datetime
from PIL import Image
import random
from discord.ext import commands
from discord import app_commands 

class Tarot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="tarot_card", description="抽一張塔羅牌")
    async def tarot_card(self, interaction: discord.Interaction):
        url = "http://127.0.0.1:8000/tarot/random_tarot"
        response = requests.get(url)
        await interaction.response.defer()
        
        if response.status_code == 200:
            card = response.json()
            card_url = card['url'] 
            card_name = card['name']
            is_reversed = False
            
            try:
                img_response = requests.get(card_url)
                if img_response.status_code != 200:
                    await interaction.response.send_message("Error to get image！")
                    return

                image_bytes = BytesIO(img_response.content)

                if random.randint(1, 100) <= 30:
                    is_reversed = True
                    with Image.open(image_bytes) as img:
                        rotated_img = img.rotate(180)
                        rotated_image_bytes = BytesIO()
                        rotated_img.save(rotated_image_bytes, format=img.format) 
                        rotated_image_bytes.seek(0)
                        image_bytes = rotated_image_bytes

                description_url = f"http://127.0.0.1:8000/tarot/get_tarot/description/{card_name}{'%20(逆位)' if is_reversed else ''}"
                card_description = requests.get(description_url).json()['description']
                
                embed = discord.Embed(
                    title=f"{card_name} {'(逆位)' if is_reversed else ''}",
                    description = card_description,
                    colour=0x2c1376,
                    timestamp=datetime.datetime.now(),
                )
                embed.set_author(name="你抽了一張塔羅牌！")
                embed.set_thumbnail(url=card_url) 

                await interaction.followup.send(embed=embed, file=discord.File(image_bytes, filename="tarot_card.png"))
            except Exception as e:
                await interaction.followup.send(f"[ERROR]: {str(e)}")
        else:
            await interaction.followup.send("API 掛了，請稍後再試！")

async def setup(bot):
    await bot.add_cog(Tarot(bot=bot))
