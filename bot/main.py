import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents) 


@bot.event
async def on_ready():
    print('Bot is ready!')
    await bot.tree.sync()

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.tree.command(name="echo", description="Echoes a message.")
@app_commands.describe(message="The message to echo.")
async def echo(interaction: discord.Interaction, message: str) -> None:
    await interaction.response.send_message(message)


bot.run(os.getenv('BOT_TOKEN'))
