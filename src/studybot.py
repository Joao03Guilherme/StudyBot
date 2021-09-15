import discord
from discord.ext import commands

import config

cogs = ["bot.roles", "bot.announcements", "bot.pomodoro.pomodoro"]

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', help_command=None, intents=intents)

for extension in cogs:
    client.load_extension(extension)

client.run(config.BOT_TOKEN)