import discord
import json
import random
import requests
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
class Embed:
    def __init__(self, id:str, name: str, teacher: str, grade: str, people: str, place: str, remark: str):
        self.id = id
        self.name = name
        self.teacher = teacher
        self.grade = grade
        self.people = people
        self.place = place
        self.remark = remark
    def generator(self):
        embed = discord.Embed(title=self.name, description=self.id, colour=0xffe4a8)
        embed.set_author(name="課程資訊")
        embed.add_field(name="授課老師",value=self.teacher,inline=False)
        embed.add_field(name="年級/分班",value=self.grade,inline=True)
        embed.add_field(name="目前選課人數",value=self.people,inline=True)
        embed.add_field(name="上課時間/地點",value=self.place,inline=True)
        embed.add_field(name="備註",value=self.remark,inline=True)
        embed.set_thumbnail(url="https://i.imghippo.com/files/mZ3729PQA.png")
        embed.set_footer(text="資料來源：國立成功大學課程資訊及選課系統")
        return embed

class NCKU_Course(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(name="course_query", description="查詢課程資訊")
    async def course_query(self, interaction: discord.Interaction, course_name: str):
        await interaction.response.defer()
        url = f"http://127.0.0.1:8000/ncku_course/query/{course_name}"
        response = requests.get(url)   
        if response.status_code == 200:
            response = response.json()
            print(response['course_name'])
            fixed_course_name = response['course_name']
            if '\n' in response['course_name']:
                fixed_course_name, fixed_note = response['course_name'].split('\n', 1)
            else: fixed_note = "無"
            print("ok")
            generated_embed = Embed(response['course_code'], fixed_course_name, response['instructor'], response['class'], response['note'], response['time_slot'], fixed_note)
            print(response['course_code'], fixed_course_name, response['instructor'], response['class'], response['note'], response['time_slot'], fixed_note)
            await interaction.followup.send(embed=generated_embed.generator())
        elif response.status_code == 404:
            await interaction.followup.send("找不到課程捏，有可能是我太笨了... QQ")
        else:
            await interaction.followup.send("api 掛ㄌ，需要修復...")

async def setup(bot: commands.Bot):
    await bot.add_cog(NCKU_Course(bot))
        