import discord
from discord.ext import commands
import config

cogs = ["bot.roles.roles", "bot.announcements.announcements", "bot.pomodoro.pomodoro", "bot.questions.questions"]

intents = discord.Intents.all()
client = commands.Bot(command_prefix=config.CMD_PREFIX, help_command=None, intents=intents)

@client.event
async def on_ready():
    print(f"Logged as {client.user}")

for extension in cogs:
    client.load_extension(extension)

client.run(config.BOT_TOKEN)