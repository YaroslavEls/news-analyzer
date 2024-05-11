import os
import traceback
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
import interface.commands_handlers as handlers
from interface.commands_descriptions import BotCommandsDescriptions
from interface.commands_error import UserInputError
from database.db_handler import DatabaseHandler
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
    result = handlers.resources(db)
    await interaction.followup.send(result)

@bot.tree.command(name='resource_info', description=bcd.resource_info)
@app_commands.describe(resource_id=bcd.resource_id_arg)
async def resource_info(interaction: discord.Interaction, 
                        resource_id: str) -> None:
    await interaction.response.defer()
    result, plot = handlers.resource_info(db, id=resource_id)
    with open(plot, 'rb') as file:
        image = discord.File(file)
    await interaction.followup.send(content=result, file=image)

@bot.tree.command(name='is_true', description=bcd.is_true)
@app_commands.describe(link=bcd.link_arg)
async def is_true(interaction: discord.Interaction, link: str) -> None:
    await interaction.response.defer()
    result = handlers.is_true(db, link=link)
    await interaction.followup.send(result)

@bot.tree.command(name='analyze', description=bcd.analyze)
@app_commands.describe(start_date=bcd.start_arg)
@app_commands.describe(end_date=bcd.end_arg)
async def analyze(interaction: discord.Interaction, 
                  start_date: str, end_date: str) -> None:
    await interaction.response.defer()
    result, plots = handlers.analyze(db, start=start_date, end=end_date)
    with open(plots[0], 'rb') as file1, \
         open(plots[1], 'rb') as file2, \
         open(plots[2], 'rb') as file3:
        image1 = discord.File(file1)
        image2 = discord.File(file2)
        image3 = discord.File(file3)
    await interaction.followup.send(content=result, 
                                    files=[image1, image2, image3])

@bot.tree.command(name='find', description=bcd.find)
@app_commands.describe(topic=bcd.topic_arg)
@app_commands.describe(start_date=bcd.start_arg)
@app_commands.describe(end_date=bcd.end_arg)
async def find(interaction: discord.Interaction, 
               topic: str, start_date: str, end_date: str) -> None:
    await interaction.response.defer()
    result = handlers.find(db, topic=topic, start=start_date, end=end_date)
    await interaction.followup.send(result)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, 
                               error: app_commands.AppCommandError) -> None:
    if isinstance(error, UserInputError):
        descr = f'INPUT ERROR:\n\n{error.message}'
    elif isinstance(error, app_commands.errors.AppCommandError):
        descr = f'SYSTEM ERROR:\n\n{error}'
    else:
        descr = 'UNKNOWN ERROR'
    
    log = ''.join(
        traceback.format_exception(type(error), error, error.__traceback__)
    )
    print(f'\033[91mError log of handled error:\033[0m\n{log}')
    await interaction.followup.send(f'```\n{descr}\n```')


try:
    bot.run(os.getenv('BOT_TOKEN'))
except Exception as e:
    print("An error occurred: ", e)
finally:
    db.disconnect()
    print('Bot has been stopped!')
