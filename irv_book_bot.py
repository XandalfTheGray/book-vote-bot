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
from ranked_irv import instant_runoff_vote
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
        events.create_index([("active", ASCENDING)], unique=True, partialFilterExpression={"active": True})
        print("Partial unique index on active events has been created.")
    except Exception as e:
        print("An error occurred while creating partial unique index on active:", e)

    # Access collection, create 'preference_lists' if it doesn't already exist
    preference_lists = db.preference_lists

    # Create a compound unique index on both 'username' and 'event' fields in 'preference_lists'
    try:
        preference_lists.create_index([("username", 1), ("event", 1)], unique=True)
        print("Compound unique index on username and event in preference_lists has been created.")
    except Exception as e:
        print("An error occurred while creating index on usernames:", e)

    print("Database setup is now complete.")

def drop_old_indexes(db):
    # Access the 'preference_lists' collection
    preference_lists = db.preference_lists

    # Drop the old index on the 'username' field
    try:
        preference_lists.drop_index([("username", 1)])  # Adjust if the index name is different
        print("Old index on 'username' has been dropped.")
    except Exception as e:
        print(f"An error occurred while dropping the old index: {e}")

    # Optionally, you can list current indexes to verify
    print(list(preference_lists.index_information()))

def start_vote_event(event_name):
    
    # Access events collection
    events = db.events

    # Check for an existing active event
    active_event = events.find_one({"active": True})

    if active_event:
        # Handle the case where an active event already exists
        print(f"Cannot start a new event, the following event is already active event: {active_event['name']}\nUse the '/tally_votes' discord command to end your current event.")
    else:
        #If an active event doesn't exist, add a new event with the name input and the start_datetime set to now
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

def upload_user_prefs(username, user_pref_list):
    # Access events and user_prefs collections
    events = db.events
    preference_lists = db.preference_lists

    # Check for an existing active event
    active_event = events.find_one({"active": True})

    if not active_event:
        print("No active event found. Cannot upload preferences.")
        return

    # Add a new preference list document with the username and preference list input
    user_pref_data = {
        "username": username,
        "event": active_event["name"],
        "preference_list": user_pref_list
    }

    try:
        # Attempt to insert the new preference list document into the collection
        result = preference_lists.insert_one(user_pref_data)
        ("Inserted user preference list with ID:", result.inserted_id)
    except DuplicateKeyError:
        print(f"A preference list for username '{username}' already exists for the event '{active_event['name']}'.")

def tally_event_votes():
    
    # Access events collection
    events = db.events

    # Search for the event with the name input
    current_event = events.find_one({"active": True})
    current_event_name = current_event['name']

    # Make the sure the event doesn't have an end_datetime
    if current_event and "end_datetime" not in current_event:
        # Access the existing event and add an end_datetime
        update_result = events.update_one(
            {"active": True},  # Ensure we only end events that are currently active
            {
                "$set": 
                {
                    "end_datetime": datetime.datetime.now(),
                    "active": False  # Set the active flag to False
                }
            }
        )
        if update_result.modified_count > 0:
            print(f"Event '{current_event_name}' ended successfully.")
        else:
            print(f"No active events updated. Make sure the event name '{current_event_name}' exists and is active.")
    
    # Tell the user the event already ended if there is an end_datetime
    elif current_event and "end_datetime" in current_event:
        print(f"The event '{current_event_name}' has already ended.")
    else:
        print(f"No events found with the name '{current_event_name}'.")

    # Access preference list collection
    preference_lists = db.preference_lists

    # Search for all preference lists for the ended event
    event_pref_lists = preference_lists.find({"event": current_event_name})

    # Initialize dictionary to hold the user preferences for this event
    user_prefs = {}

    # Organize the prefs as a dict
    for pref in event_pref_lists:
        user_prefs[pref['username']] = pref['preference_list']

    # Runs the instant runoff voting method to tally the votes
    instant_runoff_vote(user_prefs)

        
# loads important environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
MONGO_URI = os.getenv('MONGO_URI')

# Create a new client and connect to the server
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Discord_bot database will be created if it doesn't exist
db = client['discord_bot']

# Call this function before updating your indexes
# drop_old_indexes(db)

# Setup our database. Commented out bcs it's generally done once:
# setup_database(db)
# print(db.preference_lists.index_information())
# print(db.events.index_information())

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

# Say hello
@bot.tree.command(name="hello", description="Use this command to tell the bot hello", guild=discord.Object(id=int(GUILD_ID)))
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user}!")

# Name and start a new event
@bot.tree.command(name="start_event", description="Start a new voting event.", guild=discord.Object(id=int(GUILD_ID)))
@app_commands.describe(event_name="The designated name for this voting event.")
async def announce(interaction: discord.Interaction, event_name: str):
    await start_vote_event(event_name)
    await interaction.response.send_message(f"{interaction.user} started a new event: {event_name}")

# Take the users three votes as inputs, upload the votes, and print them
@bot.tree.command(name="vote", description="Submit your vote for the most recent voting event.", guild=discord.Object(id=int(GUILD_ID)))
@app_commands.describe(first_vote="Your first choice for this voting event.", second_vote="Your second choice for this voting event.", third_vote="Your third choice for this voting event.")
async def announce(interaction: discord.Interaction, first_vote: str, second_vote: str, third_vote: str):
    await upload_user_prefs(interaction.user, [first_vote, second_vote, third_vote])
    await interaction.response.send_message(f"{interaction.user} cast their votes:\n1. {first_vote}\n2. {second_vote}\n3. {third_vote}")

# End the currently active event and tally the votes
@bot.tree.command(name="tally_votes", description="End the active event and tally the votes.", guild=discord.Object(id=int(GUILD_ID)))
async def announce(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user} has ended this vote event. We'll now tally the votes.")
    await tally_event_votes()

bot.run(BOT_TOKEN)

'''
Some example commands
'''
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
'''