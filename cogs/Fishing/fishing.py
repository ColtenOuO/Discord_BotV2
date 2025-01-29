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
        self.fish_times = {}  
        self.jailed_users = {}  
        self.education_count = {}  

    def fish_embed_generator(self, fish_name: str, fish_level: str, fish_description: str, price: int):
        embed = discord.Embed(
            title=fish_name,
            description=fish_description,
            colour=0x00b0f4,
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name="你釣起了一隻魚！！")
        embed.add_field(name="等級", value=fish_level, inline=False)
        embed.add_field(name="價格", value=f"{price} 元", inline=False)
        embed.set_thumbnail(url="https://i.imghippo.com/files/ntuW9239iso.webp")
        return embed

    def report_embed_generator(self, reporter_name: str, reported_name: str, money: int, result: str):
        embed = discord.Embed(
            title=f"剛剛... {reporter_name} 檢舉了 {reported_name}",
            colour=0xb51a00
        )
        if result == "檢舉失敗":
            reporter_name, reported_name = reported_name, reporter_name
        embed.set_author(name="重大新聞事件！！！")
        embed.add_field(name="檢舉結果", value=f"**{result}！**", inline=False)
        embed.add_field(
            name="判決",
            value=f"🔴 **{reported_name} 罰款 {money} 元，監禁 15 分鐘！**\n\n"
                  f"📝 **出獄後，{reported_name} 需強制實施「海洋生態保育」講習，出獄後的前 30 次釣魚，顯示的資訊皆為海洋生態保育科普！**\n\n"
                  f"💰 **另外，{reporter_name} 將獲得 {money // 2} 元獎勵(補償)！**",
            inline=False
        )
        embed.set_thumbnail(url="https://i.imghippo.com/files/LS1592Y.png")
        return embed

    def education_message(self, user_name: str, remaining: int):
        """生成海洋生態保育教育訊息"""
        embed = discord.Embed(
            title="🌊 海洋生態保育教育 🌊",
            description=(
                f"親愛的 {user_name}，你知道嗎？\n"
                "我們的海洋佔據地球表面超過 **70%**，但面臨著過度捕撈、海洋污染與氣候變遷等危機。\n\n"
                "**🐟 過度捕撈的危害**\n"
                "過度捕魚不僅減少了漁業資源，還會影響整個海洋生態鏈，導致掠食者缺乏食物，甚至造成物種滅絕。\n\n"
                "**🛢 海洋污染的影響**\n"
                "每年超過 **800 萬噸塑膠垃圾** 進入海洋，導致無數海龜、魚類和鳥類誤食而死亡。\n\n"
                "**🔥 氣候變遷與珊瑚白化**\n"
                "全球暖化導致海水溫度上升，使珊瑚礁白化並最終死亡，影響整個海洋生態系。\n\n"
                "**🌱 我們能做什麼？**\n"
                "- 選擇永續漁業產品 🐠\n"
                "- 減少塑膠使用 🌎\n"
                "- 參與海洋保育活動 💙\n\n"
                f"🌊 **你還需完成 {remaining} 次海洋生態保育教育！**"
            ),
            colour=0x1E90FF
        )
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
        user_id = interaction.user.id
        now = datetime.datetime.now()

        if user_id in self.jailed_users and now < self.jailed_users[user_id]:
            remaining_time = int((self.jailed_users[user_id] - now).total_seconds() / 60)
            await interaction.response.send_message(f"🚨 你還在監獄中！還有 {remaining_time} 分鐘才出獄！請好好思考為什麼要這樣殘害海洋！")
            return
        else:
            self.jailed_users.pop(user_id, None)

        if user_id in self.education_count and self.education_count[user_id] > 0:
            education_embed = self.education_message(interaction.user.display_name, self.education_count[user_id]-1)
            self.education_count[user_id] -= 1
            if self.education_count[user_id] == 0:
                del self.education_count[user_id]
        else:
            education_embed = None
            self.fish_times[user_id] = now
            response = requests.get("http://127.0.0.1:8000/fishing/random_fish")

        if response.status_code == 200:
            fish = response.json()
            price = random.randint(0, 100)
            embed = self.fish_embed_generator(fish['name'], fish['level'], fish['description'], price)

            if education_embed:
                await interaction.response.send_message(embed=education_embed, ephemeral=(self.education_count != 29) )
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
                requests.post(f"http://127.0.0.1:8000/db/update/add/{user_id}/{price}")
        else:
            await interaction.response.send_message("api 掛ㄌ，需要修復...")

    @app_commands.command(name="report", description="檢舉一位使用者，如果他在 5 分鐘內釣過魚則檢舉成功")
    async def report(self, interaction: discord.Interaction, user: discord.Member):
        reporter_id = interaction.user.id
        reported_id = user.id
        now = datetime.datetime.now()

        if reported_id in self.fish_times and (now - self.fish_times[reported_id]).total_seconds() <= 300:
            jail_time = now + datetime.timedelta(minutes=15)
            self.jailed_users[reported_id] = jail_time
            self.education_count[reported_id] = 30
            fine_amount = random.randint(5000, 20000)
            reward_amount = fine_amount // 2

            requests.post(f"http://127.0.0.1:8000/db/update/add/{reported_id}/{-fine_amount}")
            requests.post(f"http://127.0.0.1:8000/db/update/add/{reporter_id}/{reward_amount}")

            embed = self.report_embed_generator(interaction.user.display_name, user.display_name, fine_amount, "檢舉成功")
            await interaction.response.send_message(embed=embed)
        else:
            jail_time = now + datetime.timedelta(minutes=15)
            self.jailed_users[reporter_id] = jail_time
            self.education_count[reporter_id] = 30
            fine_amount = random.randint(5000, 20000)
            reward_amount = fine_amount // 2

            requests.post(f"http://127.0.0.1:8000/db/update/add/{reporter_id}/{-fine_amount}")
            requests.post(f"http://127.0.0.1:8000/db/update/add/{reported_id}/{reward_amount}")

            embed = self.report_embed_generator(interaction.user.display_name, user.display_name, fine_amount, "檢舉失敗")
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fishing(bot=bot))
