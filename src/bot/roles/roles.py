import discord
import os
import config
import json
from discord.ext import commands
from .roles_messages import role_message, greet_message

here = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(here, 'stored_values.json')

with open(filename) as file:
    try:
        storage = json.load(file)
    except FileNotFoundError:
        storage = {}

def may_use_command(member):
    allowed_roles = ["admin"]
    roles = [discord.utils.get(member.guild.roles, name=role_name) for role_name in allowed_roles]
    return any(role in roles for role in member.roles)

class roles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready!")
        self.guild = self.client.get_guild(config.ID_GUILD)

        self.default_role = self.guild.get_role(config.ID_DEFAULT_ROLE)
        self.decimo_role = self.guild.get_role(config.ID_DECIMO_ROLE)
        self.decimoprimeiro_role = self.guild.get_role(config.ID_DECIMOPRIMEIRO_ROLE)
        self.decimosegundo_role = self.guild.get_role(config.ID_DECIMOSEGUNDO_ROLE)

        self.decimosegundo_emoji = "🔵"
        self.decimoprimeiro_emoji = "🟣"
        self.decimo_emoji = "🟠"

        self.rules_channel = self.client.get_channel(config.ID_RULES_CHANNEL)
        self.roles_channel = self.client.get_channel(config.ID_ROLES_CHANNEL)
        self.greet_channel = self.client.get_channel(config.ID_GREET_CHANNEL)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        rules_channel = self.rules_channel
        roles_channel = self.roles_channel
        greet_channel = self.greet_channel

        await greet_channel.send(greet_message(member, rules_channel, roles_channel))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if "role_message" in storage:
            if int(storage["role_message"]) == payload.message_id:
                member = payload.member
                if str(payload.emoji) == str(self.decimo_emoji):
                    await member.add_roles(self.decimo_role, self.default_role)
                elif str(payload.emoji) == str(self.decimoprimeiro_emoji):
                    await member.add_roles(self.decimoprimeiro_role, self.default_role)
                elif str(payload.emoji) == str(self.decimosegundo_emoji):
                    await member.add_roles(self.decimosegundo_role, self.default_role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if "role_message" in storage:
            if int(storage["role_message"]) == payload.message_id:
                member = self.guild.get_member(payload.user_id)
                if str(payload.emoji) == str(self.decimo_emoji):
                    await member.remove_roles(self.decimo_role)
                elif str(payload.emoji) == str(self.decimoprimeiro_emoji):
                    await member.remove_roles(self.decimoprimeiro_role)
                elif str(payload.emoji) == str(self.decimosegundo_emoji):
                    await member.remove_roles(self.decimosegundo_role)

    @commands.command(name="send_role_message")
    @commands.guild_only()
    async def send_role_message(self, ctx):
        if not may_use_command(ctx.author):
            raise PermissionError
        else:
            if "role_message" in storage:
                await ctx.channel.send("Já existe uma mensagem com as roles")
            else:
                sent_message = await self.roles_channel.send(
                    embed=role_message(self.decimo_emoji, self.decimoprimeiro_emoji, self.decimosegundo_emoji))

                # Add reactions to the message
                await sent_message.add_reaction(self.decimo_emoji)
                await sent_message.add_reaction(self.decimoprimeiro_emoji)
                await sent_message.add_reaction(self.decimosegundo_emoji)

                # Store message in storage dict
                storage["role_message"] = sent_message.id

                # Store message in json file
                with open(filename, "w") as file:
                    json.dump(storage, file)


def setup(client):
    client.add_cog(roles(client))