import asyncio
from datetime import datetime, timedelta

import config
import nextcord
from nextcord.ext import commands, tasks

from .embed_templates import timer_embed_template, pomodoro_initial_message_template, pomodoro_timer_begins_template, \
    break_timer_begins_template

session_dict = {}


class timer:
    def __init__(self, end_time: datetime, member, channel):
        self.end_time = end_time
        self.member = member
        self.channel = channel
        self.message = None

    async def create_message(self):
        emb = timer_embed_template(self.end_time)
        self.message = await self.channel.send(embed=emb)

    async def edit_message(self):
        emb = timer_embed_template(self.end_time)
        await self.message.edit(embed=emb)

    async def end_timer(self):
        emb = timer_embed_template(self.end_time)
        await self.message.edit(embed=emb)

class pomodoro_session:
    def __init__(self, member, roles_and_category, pomodoro_duration: timedelta, break_duration: timedelta):
        self.member = member
        self.roles_and_category = roles_and_category
        self.channel = None
        self.is_current_timer_pomodoro = True
        self.current_timer = None
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


# Data class
class roles_and_category_class:
    def __init__(self, client):
        self.guild = client.get_guild(config.ID_GUILD)
        self.pomodoro_category = self.guild.get_channel(
            config.ID_POMODORO_CATEGORY)  # get_channel method also gets category
        self.pomodoro_role = self.guild.get_role(config.ID_POMODORO_ROLE)
        self.default_role = self.guild.get_role(config.ID_DEFAULT_ROLE)
        self.everyone_role = self.guild.get_role(config.ID_EVERYONE_ROLE)


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
        self.roles = roles_and_category_class(self.client)

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
        session_dict[interaction.user] = new_session
        await new_session.start_session()

    @nextcord.slash_command(name="end_pomodoro", description="Termina uma sessão de estudo Pomodoro")
    async def end_pomodoro(self, interaction: nextcord.Interaction):
        global session_dict
        if interaction.user not in session_dict.keys():
            await interaction.send("Não estás numa sessão de estudo Pomodoro", ephemeral=True)
        else:
            session = session_dict[interaction.user]
            await interaction.send("A terminar sessão pomodoro...", ephemeral=True)
            await asyncio.sleep(1)
            await session.end_session()

            del session_dict[interaction.user]

    @commands.check(may_use_command)
    @nextcord.slash_command(name="force_end_pomodoro", description="Força o fim de uma sessão pomodoro")
    async def force_end_pomodoro(self, interaction : nextcord.Interaction,
                                 arg1 = nextcord.SlashOption(name="member_id", description="Id do membro preso no pomodoro"),
                                 arg2 = nextcord.SlashOption(name="channel_id", description="Id do canal do pomodoro")
    ):
        try:
            member = self.roles.guild.get_member(int(arg1))
            channel = self.roles.guild.get_channel(int(arg2))
            await member.add_roles(self.roles.default_role)
            await member.remove_roles(self.roles.pomodoro_role)
            await channel.delete()
            await interaction.send("A sessão foi eliminado com sucesso", ephemeral=True)
        except:
            await interaction.send("Ocorreu um erro a eliminar o pomodoro", ephemeral=True)

    @tasks.loop(seconds=1)
    async def update_timers(self):
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
                except:
                    pass  # Message has been deleted, session ended before timer expired

    @update_timers.before_loop
    async def before_update_timers(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(pomodoro(client))
