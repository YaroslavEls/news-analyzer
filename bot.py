import os
import traceback
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

from db_handler import DatabaseHandler
from commands_descriptions import BotCommandsDescriptions
import bot_functions as funcs


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

db = DatabaseHandler()
bcd = BotCommandsDescriptions()


@bot.event
async def on_ready():
    print('Bot is ready!')
    await bot.tree.sync()

@bot.tree.command(name='resources', description=bcd.resources)
async def resources(interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    result = funcs.get_resources(db)
    await interaction.followup.send(result)

@bot.tree.command(name='is_true', description=bcd.is_true)
@app_commands.describe(link=bcd.link_arg)
async def is_true(interaction: discord.Interaction, link: str) -> None:
    await interaction.response.defer()
    result = funcs.check_if_true(db, link)
    await interaction.followup.send(result)

@bot.tree.command(name='analyze', description=bcd.analyze)
@app_commands.describe(start_date=bcd.start_arg)
@app_commands.describe(end_date=bcd.end_arg)
async def analyze(interaction: discord.Interaction, start_date: str, end_date: str) -> None:
    await interaction.response.defer()
    result, plots = funcs.analyze_period(db, start_date, end_date)
    with open(plots[0], 'rb') as file1, open(plots[1], 'rb') as file2:
        image1 = discord.File(file1)
        image2 = discord.File(file2)
        await interaction.followup.send(content=result, files=[image1, image2])

@bot.tree.command(name='find', description=bcd.find)
@app_commands.describe(topic=bcd.topic_arg)
@app_commands.describe(start_date=bcd.start_arg)
@app_commands.describe(end_date=bcd.end_arg)
async def find(interaction: discord.Interaction, topic: str, start_date: str, end_date: str) -> None:
    await interaction.response.defer()
    result = funcs.find_n_analyze(db, topic, start_date, end_date)
    await interaction.followup.send(result)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, app_commands.errors.AppCommandError):
        descr = error
    else:
        error_data = ''.join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        descr = f'Unknown error\n{error_data[:1000]}'
    
    log = ''.join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    print(f'\033[91mError log of handled error:\033[0m\n{log}')
    await interaction.followup.send(f'```\nERROR LOG:\n\n{descr}\n```')


try:
    bot.run(os.getenv('BOT_TOKEN'))
except Exception as e:
    print("An error occurred: ", e)
finally:
    db.disconnect()
    print('Bot has been stopped!')
