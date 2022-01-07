import nextcord
from nextcord.ext import commands
import config

cogs = ["bot.cogs.roles.roles", "bot.cogs.announcements.announcements", "bot.cogs.questions.questions", "bot.cogs.pomodoro.pomodoro"]

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix=config.CMD_PREFIX, help_command=None, intents=intents)

@client.event
async def on_ready():
    print(f"Logged as {client.user}")

for extension in cogs:
    client.load_extension(extension)

client.run(config.BOT_TOKEN)
