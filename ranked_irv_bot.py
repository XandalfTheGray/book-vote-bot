import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import ranked_irv
import asyncio

# loads important environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

# basic bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has started')
    # Ensure GUILD_ID is correctly converted to integer
    guild = discord.Object(id=int(GUILD_ID))
    # Sync commands specifically for the guild
    await bot.tree.sync(guild=guild)
    print("Commands synced for guild:", GUILD_ID)

@bot.command()
async def sync(ctx):
    # Sync commands interactively
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"Synced {len(synced)} command(s)")

@bot.tree.command(name="hello", description="Use this command to tell the bot hello", guild=discord.Object(id=int(GUILD_ID)))
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user}!")

bot.run(BOT_TOKEN)