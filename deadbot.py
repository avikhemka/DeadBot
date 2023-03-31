import os
import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands, tasks
from disnake.app_commands import Option, OptionType
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from pytz import timezone
from disnake import TextChannel
import json
import os
import re

TOKEN = "MTA5MDYwNzY3OTUyMjc1MDUxNA.GTmsv8.UWIwxf02IQP5PtB-PFPWS47ay6tCE-Xos69NN8"

intents = disnake.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Deadline dictionary
deadlines = {}


def load_deadlines():
    for guild in bot.guilds:
        file_path = f"server-deadlines/{guild.id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                deadlines[guild.id] = json.load(file)
        else:
            deadlines[guild.id] = {}


def save_deadlines(guild_id):
    file_path = f"server-deadlines/{guild_id}.json"
    with open(file_path, "w") as file:
        json.dump(deadlines[guild_id], file)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    print(f"Connected to {len(bot.guilds)} server(s):")
    for guild in bot.guilds:
        print(f"{guild.name}")


@bot.event
async def on_raw_message_delete(payload: disnake.RawMessageDeleteEvent):
    # Retrieve the channel where the message was deleted
    channel = bot.get_channel(payload.channel_id)

    # Check if the channel is the deadlines channel
    if channel.name == "deadlines":
        # Load the deadlines JSON file
        with open("server-deadlines/{}.json".format(channel.guild.id), "r") as f:
            deadlines = json.load(f)

        # Find the deadline with the matching message ID
        for project_name, deadline_data in deadlines.items():
            if deadline_data["message_id"] == payload.message_id:
                # Remove the deadline from the JSON file
                del deadlines[project_name]

                # Save the updated JSON file
                with open("server-deadlines/{}.json".format(channel.guild.id), "w") as f:
                    json.dump(deadlines, f)

                print(f"Deadline for project {project_name} deleted.")
                break

@bot.slash_command(
    name="deadbot",
    description="Create a new deadline",
    options=[
        Option("project_name", "Name of the project", OptionType.string, required=True),
        Option("description", "Description of the project", OptionType.string, required=True),
        Option("deadline_date", "Deadline date in YYYY-MM-DD format", OptionType.string, required=True),
        Option("deadline_time", "Deadline time in HH:mm format", OptionType.string, required=True),
        Option("timezone", "Timezone abbreviation, e.g., HKT", OptionType.string, required=True),
        Option("roles", "Roles to be notified (separate by comma)", OptionType.string, required=True),

    ]
)
async def deadbot(inter: ApplicationCommandInteraction, project_name: str, deadline_date: str, deadline_time: str,
                  timezone: str, roles: str, description: str):
    try:
        dt = dateparser.parse(f"{deadline_date} {deadline_time} {timezone}")
        parsed_roles = [role.strip() for role in roles.split(",")]

        days_remaining = (dt - datetime.now(dt.tzinfo)).days

        deadline_message = (
            f"Project: {project_name}\n\n"
            f"Deadline: {dt.strftime('%Y-%m-%d %H:%M%Z')}\n\n"
            f"Description: {description}\n\n"
            f"{'-' * 29}Days until deadline: {days_remaining} Days{'-' * 29}\n\n"
            f"Deadline created by: {inter.author.mention}\n\n"
            f"Team: {', '.join(parsed_roles)}"
        )

        deadline = {
            "project_name": project_name,
            "deadline": dt.isoformat(),  # Convert datetime object to a string
            "timezone": timezone,
            "roles": parsed_roles,
            "description": description,
            "created_by": inter.author.id,
            "message_content": deadline_message  # Add this line
        }

        guild_id = inter.guild.id
        if guild_id not in deadlines:
            deadlines[guild_id] = {}

        deadlines[guild_id][project_name] = deadline
        save_deadlines(guild_id)

        days_remaining = (dt - datetime.now(dt.tzinfo)).days
        deadlines[project_name] = deadline

        deadline_message = (
            f"Project: {project_name}\n\n"
            f"Deadline: {dt.strftime('%Y-%m-%d %H:%M%Z')}\n\n"
            f"Description: {description}\n\n"
            f"{'-' * 29}Days until deadline: {days_remaining} Days{'-' * 29}\n\n"
            f"Deadline created by: {inter.author.mention}\n\n"
            f"Team: {', '.join(parsed_roles)}"
        )
        return_message = f"Thanks {inter.author.mention}" f" I've created a deadline for {project_name}!" f" You can view it in the #deadlines channel."
        await inter.response.send_message(return_message, ephemeral=True)
        deadlines_channel_name = "deadlines"  # Replace this with the name of your deadlines channel

        # Find the deadlines channel
        deadlines_channel = disnake.utils.get(inter.guild.text_channels, name=deadlines_channel_name)

        # Create the deadlines channel if it doesn't exist
        if not deadlines_channel:
            overwrites = {
                inter.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            }
            deadlines_channel = await inter.guild.create_text_channel(deadlines_channel_name, overwrites=overwrites)

        # Send the deadline message to the deadlines channel
        message_sent = await deadlines_channel.send(deadline_message)

        # Store the message ID in the deadline dictionary
        deadline["message_id"] = message_sent.id
        deadlines[guild_id][project_name] = deadline
        save_deadlines(guild_id)

    except Exception as e:
        await inter.response.send_message(f"Error: {e}", ephemeral=True)


bot.run(TOKEN)
