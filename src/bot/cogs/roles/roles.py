import discord
import os
import config
import json
from discord.ext import commands
from .roles_messages import role_message, role_message_uni, role_message_disciplines, greet_message

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
        self.guild = self.client.get_guild(config.ID_GUILD)

        self.default_role = self.guild.get_role(config.ID_DEFAULT_ROLE)
        self.decimo_role = self.guild.get_role(config.ID_DECIMO_ROLE)
        self.decimoprimeiro_role = self.guild.get_role(config.ID_DECIMOPRIMEIRO_ROLE)
        self.decimosegundo_role = self.guild.get_role(config.ID_DECIMOSEGUNDO_ROLE)
        self.universidade_role = self.guild.get_role(config.ID_UNIVERSIDADE_ROLE)

        self.mat_role = self.guild.get_role(config.ID_MAT_ROLE)
        self.fis_role = self.guild.get_role(config.ID_FIS_ROLE)
        self.chem_role = self.guild.get_role(config.ID_CHEM_ROLE)
        self.bio_role = self.guild.get_role(config.ID_BIO_ROLE)
        self.geo_role = self.guild.get_role(config.ID_GEO_ROLE)
        self.pt_role = self.guild.get_role(config.ID_PT_ROLE)

        self.decimosegundo_emoji = "🔵"
        self.decimoprimeiro_emoji = "🟣"
        self.decimo_emoji = "🟠"
        self.universidade_emoji = "📗"

        self.rules_channel = self.client.get_channel(config.ID_RULES_CHANNEL)
        self.roles_channel = self.client.get_channel(config.ID_ROLES_CHANNEL)
        self.greet_channel = self.client.get_channel(config.ID_GREET_CHANNEL)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.greet_channel.send(greet_message(
            member,
            self.rules_channel,
            self.roles_channel)
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        member = payload.member
        if member == self.client.user:
            return

        if "role_message" in storage:
            if int(storage["role_message"]) == payload.message_id:
                if str(payload.emoji) == str(self.decimo_emoji):
                    await member.add_roles(self.decimo_role, self.default_role)
                elif str(payload.emoji) == str(self.decimoprimeiro_emoji):
                    await member.add_roles(self.decimoprimeiro_role, self.default_role)
                elif str(payload.emoji) == str(self.decimosegundo_emoji):
                    await member.add_roles(self.decimosegundo_role, self.default_role)

        if "role_message_uni" in storage:
            if str(payload.emoji) == str(self.universidade_emoji):
                await member.add_roles(self.universidade_role, self.default_role)

        if "role_message_disciplines" in storage:
            if str(payload.emoji) == "📐":
                await member.add_roles(self.mat_role)
            elif str(payload.emoji) == "🪂":
                await member.add_roles(self.fis_role)
            elif str(payload.emoji) == "💧":
                await member.add_roles(self.chem_role)
            elif str(payload.emoji) == "🌱":
                await member.add_roles(self.bio_role)
            elif str(payload.emoji) == "⛏":
                await member.add_roles(self.geo_role)
            elif str(payload.emoji) == "🇵🇹":
                await member.add_roles(self.pt_role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        member = self.guild.get_member(payload.user_id)

        if "role_message" in storage:
            if int(storage["role_message"]) == payload.message_id:
                if str(payload.emoji) == str(self.decimo_emoji):
                    await member.remove_roles(self.decimo_role)
                elif str(payload.emoji) == str(self.decimoprimeiro_emoji):
                    await member.remove_roles(self.decimoprimeiro_role)
                elif str(payload.emoji) == str(self.decimosegundo_emoji):
                    await member.remove_roles(self.decimosegundo_role)

        if "role_message_uni" in storage:
            if str(payload.emoji) == str(self.universidade_emoji):
                await member.remove_roles(self.universidade_role)

        if "role_message_disciplines" in storage:
            if str(payload.emoji) == "📐":
                await member.remove_roles(self.mat_role)
            elif str(payload.emoji) == "🪂":
                await member.remove_roles(self.fis_role)
            elif str(payload.emoji) == "💧":
                await member.remove_roles(self.chem_role)
            elif str(payload.emoji) == "🌱":
                await member.remove_roles(self.bio_role)
            elif str(payload.emoji) == "⛏":
                await member.remove_roles(self.geo_role)
            elif str(payload.emoji) == "🇵🇹":
                await member.remove_roles(self.pt_role)

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

    @commands.command(name="send_role_message_uni")
    @commands.guild_only()
    async def send_role_message_uni(self, ctx):
        if not may_use_command(ctx.author):
            raise PermissionError
        else:
            if "role_message_uni" in storage:
                await ctx.channel.send("Já existe uma mensagem com a role de universitário")

            else:
                print(self.roles_channel)
                sent_message = await self.roles_channel.send(
                    embed=role_message_uni(self.universidade_emoji))

                # Add reactions to the message
                await sent_message.add_reaction(self.universidade_emoji)

                # Store message in storage dict
                storage["role_message_uni"] = sent_message.id

                # Store message in json file
                with open(filename, "w") as file:
                    json.dump(storage, file)

    @commands.command(name="send_role_message_disciplines")
    @commands.guild_only()
    async def send_role_message_disciplines(self, ctx):
        if not may_use_command(ctx.author):
            raise PermissionError
        else:
            if "role_message_disciplines" in storage:
                await ctx.channel.send("Já existe uma mensagem com a seleção das roles")

            else:
                sent_message = await self.roles_channel.send(
                    embed=role_message_disciplines())

                # Add reactions to the message
                await sent_message.add_reaction("📐")
                await sent_message.add_reaction("🪂")
                await sent_message.add_reaction("💧")
                await sent_message.add_reaction("🌱")
                await sent_message.add_reaction("⛏")
                await sent_message.add_reaction("🇵🇹")

                # Store message in storage dict
                storage["role_message_disciplines"] = sent_message.id

                # Store message in json file
                with open(filename, "w") as file:
                    json.dump(storage, file)


def setup(client):
    client.add_cog(roles(client))
