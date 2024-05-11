from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError
from pymongo import IndexModel, ASCENDING
import datetime
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import ranked_irv
import asyncio

# Define function for setting up our database, generally run once
def setup_database(db):
    # Access collection, create 'events' if it doesn't already exist
    events = db.events

    # Create a unique index on the 'name' field if it doesn't already exist
    try:
        events.create_index([("name", 1)], unique=True)
        print("Unique index on event names has been created.")
    except Exception as e:
        print("An error occurred while creating index on event names:", e)

    # Create a partial unique index on the 'active' field for documents where active is True
    try:
        events.create_index(
            [("active", ASCENDING)],
            unique=True,
            partialFilterExpression={"active": True}
        )
        print("Partial unique index on active events has been created.")
    except Exception as e:
        print("An error occurred while creating partial unique index on active:", e)

    # Access collection, create 'preference_lists' if it doesn't already exist
    preference_lists = db.preference_lists

    # Create a unique index on the 'username' field if it doesn't already exist
    try:
        preference_lists.create_index([("username", 1)], unique=True)
        print("Unique index on preference_list usernames has been created.")
    except Exception as e:
        print("An error occurred while creating index on usernames:", e)

    print("Database setup is now complete.")

def start_vote_event(event_name):
    
    # Access events collection
    events = db.events

    # Add a new event with the name input and the start_datetime set to now
    event_data = {
        "name": event_name,
        "start_datetime": datetime.datetime.now(),
        "active": True
    }
    
    try:
        # Attempt to insert the new event document into the collection
        result = events.insert_one(event_data)
        print("Inserted event with ID:", result.inserted_id)
    except DuplicateKeyError:
        print(f"An event with the name '{event_name}' already exists.")

def end_vote_event(event_name):
    
    # Access events collection
    events = db.events

    # Search for the event with the name input
    current_event = events.find_one({"name": event_name})

    # Make the sure the event doesn't have an end_datetime
    if current_event and "end_datetime" not in current_event:
        # Access the existing event and add an end_datetime
        update_result = events.update_one(
            {"name": event_name, "active": True},  # Ensure we only end events that are currently active
            {
                "$set": 
                {
                    "end_datetime": datetime.datetime.now(),
                    "active": False  # Set the active flag to False
                }
            }
        )
        if update_result.modified_count > 0:
            print(f"Event '{event_name}' ended successfully.")
        else:
            print(f"No active events updated. Make sure the event name '{event_name}' exists and is active.")
    
    # Tell the user the event already ended if there is an end_datetime
    elif current_event and "end_datetime" in current_event:
        print(f"The event '{event_name}' has already ended.")
    else:
        print(f"No events found with the name '{event_name}'.")


uri = "mongodb+srv://xapicella7:aoCDthsQLgUEJ4f2@discordbookbot.nffupxa.mongodb.net/?retryWrites=true&w=majority&appName=DiscordBookBot"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Discord_bot database will be created if it doesn't exist
db = client['discord_bot']

# Setup our database. Commented out bcs it's generally done once:
# setup_database(db)

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

# Says hello
@bot.tree.command(name="hello", description="Use this command to tell the bot hello", guild=discord.Object(id=int(GUILD_ID)))
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user}!")

# This takes the users three votes as inputs and 
# It allows users to send a specified message to a selected channel directly from the command.
@bot.tree.command(name="vote", description="Submit your vote for the most recent voting event.", guild=discord.Object(id=int(GUILD_ID)))
@app_commands.describe(first_vote="Your first choice for this voting event.", second_vote="Your second choice for this voting event.", third_vote="Your third choice for this voting event.")
async def announce(interaction: discord.Interaction, first_vote: str, second_vote: str, third_vote: str):
    #await 
    await interaction.response.send_message(f"{interaction.user} cast their votes:\n1. {first_vote}\n2. {second_vote}\n3. {third_vote}")

'''
Some example commands
'''
# This command takes a user as input. When executing the command in Discord, 
# users can select a member of the server to inspect.
@bot.tree.command(name="userinfo", description="Get information about a user", guild=discord.Object(id=int(GUILD_ID)))
@app_commands.describe(user="The user to get information about")
async def userinfo(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"User {user.display_name} has ID {user.id}")

# This takes a channel and a message string as inputs. 
# It allows users to send a specified message to a selected channel directly from the command.
@bot.tree.command(name="announce", description="Send an announcement to a specific channel", guild=discord.Object(id=int(GUILD_ID)))
@app_commands.describe(channel="The channel to send the announcement to", message="The message to announce")
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    await channel.send(message)
    await interaction.response.send_message(f"Announcement sent to {channel.name}")

# It accepts a role input and provides information about that role, such as the number of members and its color.
@bot.tree.command(name="roleinfo", description="Get information about a role", guild=discord.Object(id=int(GUILD_ID)))
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