import asyncio
from datetime import datetime, timedelta

import pickle
import os
import sys
import config
import nextcord
from nextcord.ext import commands, tasks

from .embed_templates import timer_ended_embed_template, timer_embed_template, pomodoro_initial_message_template, pomodoro_timer_begins_template, \
    break_timer_begins_template

# Permanent storage of timers
abs_path = os.path.join(os.path.dirname(__file__), "stored_timers.pkl")
session_dict = {}

class timer:
    def __init__(self, end_time: datetime, member, channel,
                 message = None):
        self.end_time = end_time
        self.member = member
        self.channel = channel
        self.message = message

    async def create_message(self):
        emb = timer_embed_template(self.end_time)
        self.message = await self.channel.send(embed=emb)

    async def edit_message(self):
        emb = timer_embed_template(self.end_time)
        await self.message.edit(embed=emb)

    async def end_timer(self):
        emb = timer_ended_embed_template(self.end_time)
        await self.message.edit(embed=emb)

    """
    Returns a dict representation of the object
    It will be used in to_dict function from class pomodoro_session
    """
    def to_dict(self):
        return {
            "end_time"  : self.end_time,
            "member_id" : self.member.id,
            "channel_id": self.channel.id,
            "message_id": self.message.id
        }

class pomodoro_session:
    def __init__(self, member, roles_and_category, pomodoro_duration: timedelta, break_duration: timedelta,
                 channel=None, current_timer=None):
        self.member = member
        self.roles_and_category = roles_and_category
        self.channel = channel
        self.is_current_timer_pomodoro = True
        self.current_timer = current_timer
        self.pomodoro_duration = pomodoro_duration
        self.break_duration = break_duration

    async def start_session(self):
        # Create pomodoro channel
        # Set channel visibility settings
        overwrites = {
            self.roles_and_category.default_role: nextcord.PermissionOverwrite(view_channel=False),
            self.member: nextcord.PermissionOverwrite(view_channel=True, send_messages=True),
            self.roles_and_category.everyone_role: nextcord.PermissionOverwrite(view_channel=False),
        }

        await self.member.add_roles(self.roles_and_category.pomodoro_role)
        await self.member.remove_roles(self.roles_and_category.default_role)

        self.channel = await self.roles_and_category.guild.create_text_channel(f"Pomodoro-{self.member.name}",
                                                                               category=self.roles_and_category.pomodoro_category,
                                                                               overwrites=overwrites)

        msg = pomodoro_initial_message_template(self.member)
        await self.channel.send(msg)
        await self.timer_started_message()
        await self.send_timer()

    async def timer_started_message(self):
        if self.is_current_timer_pomodoro:
            msg = pomodoro_timer_begins_template(self.member)
        else:
            msg = break_timer_begins_template(self.member)
        await self.channel.send(msg)

    async def send_timer(self):
        if self.is_current_timer_pomodoro:
            end_time = datetime.today() + self.pomodoro_duration
        else:
            end_time = datetime.today() + self.break_duration

        self.current_timer = timer(end_time, self.member, self.channel)
        await self.current_timer.create_message()

    async def end_session(self):
        await self.member.add_roles(self.roles_and_category.default_role)
        await self.member.remove_roles(self.roles_and_category.pomodoro_role)
        await self.channel.delete()

    """
    Returns a dict representation of a pomodoro section
    """
    def to_dict(self):
        return {
            "member_id" : self.member.id,
            "channel_id": self.channel.id,
            "is_current_timer_pomodoro" : self.is_current_timer_pomodoro,
            "current_timer_dict" : self.current_timer.to_dict(),
            "pomodoro_duration" : self.pomodoro_duration,
            "break_duration" : self.break_duration
        }

# Data class
class roles_and_category_class:
    def __init__(self, client):
        self.guild = client.get_guild(config.ID_GUILD)
        self.pomodoro_category = self.guild.get_channel(
            config.ID_POMODORO_CATEGORY)  # get_channel method also gets category
        self.pomodoro_role = self.guild.get_role(config.ID_POMODORO_ROLE)
        self.default_role = self.guild.get_role(config.ID_DEFAULT_ROLE)
        self.everyone_role = self.guild.get_role(config.ID_EVERYONE_ROLE)

"""
Converts dict to pomodoro_session object
"""
async def from_dict_to_obj(dict, roles : roles_and_category_class):
   return pomodoro_session(
            roles.guild.get_member(dict["member_id"]),
            roles,
            dict["pomodoro_duration"],
            dict["break_duration"],
            roles.guild.get_channel(dict["channel_id"]),
            timer(dict["current_timer_dict"]["end_time"],
                  roles.guild.get_member(dict["current_timer_dict"]["member_id"]),
                  roles.guild.get_channel(dict["current_timer_dict"]["channel_id"]),
                  await roles.guild.get_channel(dict["current_timer_dict"]["channel_id"]).fetch_message(
                      dict["current_timer_dict"]["message_id"])
                  )
        )


# time is in minutes
def is_valid_time_argument(time: int):
    return 0 < time <= 180


def is_time_in_past(time: datetime):
    return time <= datetime.today()


def may_use_command(member):
    return any("admin" == role.name for role in member.roles)


class pomodoro(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.update_timers.start()

    @commands.Cog.listener()
    async def on_ready(self):
        global session_dict
        self.roles = roles_and_category_class(self.client)

        # Load dictionary
        try:
            with open(abs_path, "rb") as file:
                tmp_dict = pickle.load(file)
                for key in tmp_dict.keys():
                    val = tmp_dict[key]
                    session_dict[key] = await from_dict_to_obj(val, self.roles)
        except FileNotFoundError:
            print("Ficheiro ainda não criado", file=sys.stderr)

    @nextcord.slash_command(name="pomodoro", description="Cria uma sessão de estudo Pomodoro")
    async def pomodoro(self, interaction: nextcord.Interaction,
                       arg1: int = nextcord.SlashOption(name="estudo", description="Tempo de estudo (min)"),
                       arg2: int = nextcord.SlashOption(name="pausa", description="Tempo de pausa (min)"),
                       ):
        if not (is_valid_time_argument(arg1) and is_valid_time_argument(arg2)):
            await interaction.send("Os argumentos inseridos são inválidos", ephemeral=True)
            return

        await interaction.send("A criar sessão pomodoro...", ephemeral=True)
        await asyncio.sleep(1)

        pomodoro_duration, break_duration = timedelta(minutes=arg1), timedelta(minutes=arg2)
        new_session = pomodoro_session(interaction.user, self.roles, pomodoro_duration, break_duration)

        global session_dict
        session_dict[interaction.user.id] = new_session
        await new_session.start_session()

    @nextcord.slash_command(name="end_pomodoro", description="Termina uma sessão de estudo Pomodoro")
    async def end_pomodoro(self, interaction: nextcord.Interaction):
        global session_dict
        if interaction.user.id not in session_dict.keys():
            await interaction.send("Não estás numa sessão de estudo Pomodoro", ephemeral=True)
        else:
            session = session_dict[interaction.user.id]
            await interaction.send("A terminar sessão pomodoro...", ephemeral=True)
            await asyncio.sleep(1)
            await session.end_session()

            del session_dict[interaction.user.id]

    @commands.check(may_use_command)
    @nextcord.slash_command(name="force_end_pomodoro", description="Força o fim de uma sessão pomodoro")
    async def force_end_pomodoro(self, interaction: nextcord.Interaction,
                                 arg1=nextcord.SlashOption(name="member_id",
                                                           description="Id do membro preso no pomodoro"),
                                 arg2=nextcord.SlashOption(name="channel_id", description="Id do canal do pomodoro")
                                 ):
        try:
            member = self.roles.guild.get_member(int(arg1))
            channel = self.roles.guild.get_channel(int(arg2))
            await member.add_roles(self.roles.default_role)
            await member.remove_roles(self.roles.pomodoro_role)
            await channel.delete()
            await interaction.send("A sessão foi eliminada com sucesso", ephemeral=True)
        except:
            await interaction.send("Ocorreu um erro a eliminar o pomodoro", ephemeral=True)

    @tasks.loop(seconds=1)
    async def update_timers(self):
        global session_dict

        try:
            # Store dictionary representation in the file
            with open(abs_path, "wb") as file:
                converted_dict = {}
                for key in session_dict.keys():
                    val = session_dict[key]
                    try:
                        converted_dict[key] = val.to_dict()
                    except AttributeError:
                        # Message or channel might be None (not created yet)
                        # Thus, .id attribute isn't valid
                        pass
                pickle.dump(converted_dict, file)

            for session in list(session_dict.values()):
                if session.current_timer is None: continue
                if is_time_in_past(session.current_timer.end_time):
                    await session.current_timer.end_timer()

                    session.is_current_timer_pomodoro = not session.is_current_timer_pomodoro
                    await session.timer_started_message()
                    await session.send_timer()
                else:
                    try:
                        await session.current_timer.edit_message()
                    except nextcord.errors.NotFound:
                        # Timer message might be already deleted (None)
                        del session_dict[session.member.id]
        except:
            print("Ocorreu um erro a dar update dos timers", file=sys.stderr)

    @update_timers.before_loop
    async def before_update_timers(self):
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(pomodoro(client))
