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
    try:
        guild = discord.Object(id=int(GUILD_ID))
        synced = await bot.tree.sync(guild=guild)
        print(f"Commands synced for guild: {GUILD_ID}, {len(synced)} commands registered.")
    except Exception as e:
        print(f"Failed to sync commands: {str(e)}")


@bot.command()
async def sync(ctx):
    # Sync commands interactively
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"Synced {len(synced)} command(s)")

@bot.tree.command(name="hello", description="Use this command to tell the bot hello", guild=discord.Object(id=int(GUILD_ID)))
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user}!")

'''
SOME EXAMPLE COMMANDS FROM CHAT GPT
'''
# This command takes a user as input. When executing the command in Discord, 
# users can select a member of the server to inspect.
@bot.tree.command(name="userinfo", description="Get information about a user")
@app_commands.describe(user="The user to get information about")
async def userinfo(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"User {user.display_name} has ID {user.id}")

# This takes a channel and a message string as inputs. 
# It allows users to send a specified message to a selected channel directly from the command.
@bot.tree.command(name="announce", description="Send an announcement to a specific channel")
@app_commands.describe(channel="The channel to send the announcement to", message="The message to announce")
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    await channel.send(message)
    await interaction.response.send_message(f"Announcement sent to {channel.name}")

# It accepts a role input and provides information about that role, such as the number of members and its color.
@bot.tree.command(name="roleinfo", description="Get information about a role")
@app_commands.describe(role="The role to get information about")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.send_message(f"Role {role.name} has {len(role.members)} members and color {role.color}")

# Lets users select their status from a predefined set of choices.
@bot.tree.command(name="status", description="Set your current status")
@app_commands.describe(status="Your current status")
@app_commands.choices(status=[
    app_commands.Choice(name="Online", value="online"),
    app_commands.Choice(name="Away", value="away"),
    app_commands.Choice(name="Do not disturb", value="dnd"),
    app_commands.Choice(name="Invisible", value="invisible")
])
async def status(interaction: discord.Interaction, status: str):
    # Set the user's status here
    await interaction.response.send_message(f"Status set to {status}")

bot.run(BOT_TOKEN)