import discord
import json
import random
import requests
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from api.routers.ncku_course import ParsingNCKU
from config import ADMIN_ID
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
    @app_commands.command(name="course_update", description="更新選課系統資料(此為限制指令)")
    async def course_update(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.id != ADMIN_ID:
            await interaction.followup.send("你沒有權限使用這個指令！不然你會把我電腦炸了...", ephemeral=True)
        else:
            await interaction.followup.send("⏳ 正在更新：各大學院資料...")
            api_url = "http://127.0.0.1:8000/ncku_course/list/all_college"
            response = requests.get(api_url)
            if response.status_code == 200: await interaction.followup.send("✅ 更新完成！所有學院資料已更新！")
            else: await interaction.followup.send("出現錯誤，請回報")
            
            await interaction.followup.send("⏳ 正在更新：所有科系資料...")
            file_path = "./api/routers/college.json"
            with open(file_path, "r", encoding="utf-8") as json_file:
                college_list = json.load(json_file)

            cnt: int = 0
            all_data = {}
            msg_str: str = ""
            for college, college_url in college_list.items():
                parsing = ParsingNCKU(college_url)
                data = parsing.list_department(college)
                all_data[college] = data
                if( cnt == 0 ): 
                    message = await interaction.followup.send(f"✅ {college} 資料更新完成！")
                    msg_str += f"✅ {college} 資料更新完成！\n"
                else:
                    msg_str += f"✅ {college} 資料更新完成！\n"
                    await message.edit(content=msg_str)
                cnt += 1
            await interaction.followup.send("系所課程資料更新完成！")
            await interaction.followup.send("⏳ 正在更新：大學國文...")

            api_url = f"http://127.0.0.1:8000/ncku_course/get/url/general/大學國文"
            response = requests.get(api_url)
            if response.status_code == 200:
                all_data["通識類課程"] = {"大學國文": response.text.replace('"', '')}
            await interaction.followup.send(f"✅ 大學國文更新完成！")        

            with open("./api/routers/department.json", "w", encoding="utf-8") as json_file: # Write
                json.dump(all_data, json_file, ensure_ascii=False, indent=4)


    @app_commands.command(name="course_query", description="查詢課程資訊")
    @app_commands.choices(
        college = [
            app_commands.Choice(name="通識類課程", value="通識類課程"),
            app_commands.Choice(name="規劃與設計學院", value="規劃與設計學院"),
            app_commands.Choice(name="工學院", value="工學院"),
            app_commands.Choice(name="社會科學院", value="社會科學院"),
            app_commands.Choice(name="醫學院", value="醫學院"),
            app_commands.Choice(name="管理學院", value="管理學院"),
            app_commands.Choice(name="文學院", value="文學院"),
            app_commands.Choice(name="理學院", value="理學院"),
            app_commands.Choice(name="電機資訊學院", value="電機資訊學院"),
            app_commands.Choice(name="生物科學與科技學院", value="生物科學與科技學院"),
            app_commands.Choice(name="智慧半導體及永續製造學院", value="智慧半導體及永續製造學院"),
            app_commands.Choice(name="敏求智慧運算學院", value="敏求智慧運算學院"),
        ]
    )
    async def course_query(self, interaction: discord.Interaction, college: str, department: str, course_name: str):
        await interaction.response.defer()
        url = f"http://127.0.0.1:8000/ncku_course/query/{college}/{department}/{course_name}"
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
    @course_query.autocomplete("department")
    async def department_autocomplete(self, interaction: discord.Interaction, current: str):
        selected_college = interaction.namespace.college
        if not selected_college:
            return []
        file_path = "./api/routers/department.json"
        with open(file_path, "r", encoding="utf-8") as json_file:
            department_data  = json.load(json_file)
        departments = department_data.get(selected_college, {})
        filtered_departments = [
            app_commands.Choice(name=department, value=department)
            for department in departments.keys() if current.lower() in department.lower()
        ]
        return filtered_departments
        
    

async def setup(bot: commands.Bot):
    await bot.add_cog(NCKU_Course(bot))
        