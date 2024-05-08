import os
from dotenv import load_dotenv
import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
import functions as funcs


load_dotenv()

conn = sqlite3.connect('./data/news.db')
cursor = conn.cursor()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents) 


@bot.event
async def on_ready():
    print('Bot is ready!')
    await bot.tree.sync()

# @bot.command()
# async def ping(ctx):
#     await ctx.send('pong')

@bot.tree.command(name="resources", description="List of supported resources")
async def resources(interaction: discord.Interaction) -> None:
    result = funcs.get_resources(cursor)
    await interaction.response.send_message(result)

@bot.tree.command(name="is_true", description="Check if the article is true")
@app_commands.describe(link="Url address of the article (must be from supported resources)")
async def is_true(interaction: discord.Interaction, link: str) -> None:
    result = funcs.check_if_true(cursor, link)
    await interaction.response.send_message(result)

@bot.tree.command(name="analyze", description="Analyze articles over a specific period of time")
@app_commands.describe(start_date="Start date for selecting articles in format dd.mm.yyyy")
@app_commands.describe(end_date="End date for selecting articles in format dd.mm.yyyy")
async def analyze(interaction: discord.Interaction, start_date: str, end_date: str) -> None:
    await interaction.response.defer()
    result = funcs.analyze_period(cursor, start_date, end_date)
    with open("./data/plot1.png", "rb") as file1, open("./data/plot2.png", "rb") as file2:
        image1 = discord.File(file1)
        image2 = discord.File(file2)
        await interaction.followup.send(content=result, files=[image1, image2])


try:
    bot.run(os.getenv('BOT_TOKEN'))
except Exception as e:
    print("An error occurred: ", e)
finally:
    conn.close()
    print('Bot has been stopped!')
