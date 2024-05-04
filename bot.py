import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import goodscrape
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

@bot.command()
async def sync(ctx):
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"Synced {len(synced)} command(s)")

# @bot.tree.command(name="clear_commands", guild=discord.Object(id=GUILD_ID))
# async def clear_commands(interaction: discord.Interaction):
#     await interaction.response.send_message('Clearing all commands')
#     bot.tree.clear_commands(guild=None)
#     await bot.tree.sync(guild=None)
#     bot.tree.clear_commands(guild=discord.Object(id=GUILD_ID))
#     await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
#     await interaction.response.send_message('All commands wiped')


@bot.tree.command(name="hello", description="Use this command to tell the bot hello", guild=discord.Object(id=GUILD_ID))
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user}!")


@bot.tree.command(name="book", description="Find information on a book in GoodReads", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(book="Book info (e.g. title, author)")
async def book(interaction: discord.Interaction, book: str):
    await interaction.response.send_message(f"Searching GoodReads for {book}...")
    
    dict = await goodscrape.scrape(book)

    await interaction.followup.send(dict)


bot.run(BOT_TOKEN)