import discord
import json
import random
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

with open("./cogs/Quiz/question.json", "r", encoding="utf-8") as file:
    data = json.load(file)

class QuizButton(Button):
    def __init__(self, label, correct_answer, parent_view):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.correct_answer = correct_answer
        self.parent_view = parent_view
    async def callback(self, interaction: discord.Interaction):
        for button in self.parent_view.children: # disable all button
            button.disabled = True

        if self.label == self.correct_answer:
            content = f"🎉 恭喜 {interaction.user.mention} 答對了！答案是 **{self.label}**！"
            await interaction.response.send_message('恭喜答對')
        else:
            content = f"❌ 抱歉 {interaction.user.mention}，答案錯誤，正確答案是 **{self.correct_answer}**！"
            await interaction.response.send_message('歐歐，答錯了')

        await interaction.message.edit(content=content, view=self.parent_view)


class Quiz(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="daily_quiz", description="抽一題（搶答模式）")
    async def daily_quiz(self, interaction: discord.Interaction):
        random_question = random.choice(data["questions"])
        question = random_question['question']
        options = random_question['options']
        correct_answer = random_question['answer']
        view = View()
        for option in options:
            view.add_item(QuizButton(label=option, correct_answer=correct_answer, parent_view=view))
        embed = discord.Embed(
            title="抽一題：搶答模式",
            description=f"{question}\n\n請搶答：",
            colour=discord.Colour.blue()
        )
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Quiz(bot))
