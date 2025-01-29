import discord
import random
import requests
from discord.ext import commands
from discord import app_commands

class Lottery(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="scratch", description="花 350 元玩新年呱呱樂！")
    async def scratch(self, interaction: discord.Interaction):
        def generate_numbers(pattern, count):
            numbers = [random.choice(pattern) for _ in range(count)]
            return numbers, "||" + "||||".join(str(num) for num in numbers) + "||"

        game_1_numbers, game_1 = generate_numbers(range(0, 10), 20)
        game_2_numbers, game_2 = generate_numbers(range(0, 10), 20)
        game_3_numbers, game_3 = generate_numbers(range(0, 10), 20)
        game_4_numbers, game_4 = generate_numbers(range(0, 10), 4)

        api_url = f"http://127.0.0.1:8000/db/update/add/{interaction.user.id}/{-350}"
        requests.post(api_url)

        class LotteryView(discord.ui.View):
            def __init__(self, user: discord.User):
                super().__init__()
                self.user = user

            @discord.ui.button(label="對獎", style=discord.ButtonStyle.green)
            async def check_prize(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user != self.user:
                    await interaction.response.send_message("❌ 你不是這張刮刮卡的擁有者，不能對獎！", ephemeral=True)
                    return

                total_prize = sum(game_1_numbers)
                seven_count = game_2_numbers.count(7)
                total_prize += sum(game_1_numbers) * seven_count
                total_prize += sum(10 for num in game_3_numbers if num in {0, 2, 5})
                if "".join(map(str, game_4_numbers)) == "2025":
                    total_prize += 10_000_000

                embed.add_field(name="💰 你的總獎金", value=f"**{total_prize} 元**", inline=False)
                api_url = f"http://127.0.0.1:8000/db/update/add/{interaction.user.id}/{total_prize}"
                requests.post(api_url)
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(embed=embed, view=self)

        embed = discord.Embed(title="新年快樂，一起來玩呱呱樂", colour=0x96d35f)
        embed.set_author(name="呱呱樂 (歡慶開幕版)")
        embed.add_field(name="遊戲 1: 每一格呱到的數字即獲得對應金額", value=game_1, inline=False)
        embed.add_field(name="遊戲 2: 呱到 1 個 7 可以獲得遊戲 1 對應數字的金額", value=game_2, inline=False)
        embed.add_field(name="遊戲 3: 刮出 0、2、5 一個可獲得 10 元", value=game_3, inline=False)
        embed.add_field(name="遊戲 4: 呱到 2025 這個數字即可獲得 1000 萬元", value=game_4, inline=False)
        embed.set_thumbnail(url="https://i.imghippo.com/files/gblo9797Gl.png")

        await interaction.response.send_message(embed=embed, view=LotteryView(interaction.user))

async def setup(bot):
    await bot.add_cog(Lottery(bot=bot))
