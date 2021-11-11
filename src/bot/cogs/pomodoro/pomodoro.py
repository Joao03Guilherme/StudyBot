import discord
import config
import os
import json
from .pomodoro_messages import timer_running_embed_template, timer_ended_embed_template, timer_ended_message_template, \
    pomodoro_initial_message_template
from .utils import get_date_from_duration, is_time_in_past
from discord.ext import commands, tasks

here = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(here, 'stored_timers.json')
try:
    with open(filename) as file:
        timer_dict = json.load(file)
except FileNotFoundError:
    timer_dict = {}


def dump_json():
    # Store values in json file
    with open(filename, "w") as file:
        json.dump(timer_dict, file)


# TODO: UTILIZAR INHERITANCE DA CLASSE TIMER PARA AS CHILD CLASSES POMODORO E BREAK?
class timer:
    def __init__(self, guild, is_pomodoro, channel_id, pomodoro_duration, break_duration, long_break_duration,
                 member_id, iteration, end_time=None, message_id=None):
        self.guild = guild
        self.is_pomodoro = is_pomodoro
        self.channel = guild.get_channel(channel_id)
        self.message = None if message_id is None else self.channel.get_partial_message(message_id)
        self.end_time = get_date_from_duration(
            pomodoro_duration if self.is_pomodoro else
            long_break_duration if iteration % (config.POMODORO_ITERATIONS * 2) == 0 else
            break_duration
        ) if end_time is None else end_time
        self.pomodoro_duration = pomodoro_duration
        self.break_duration = break_duration
        self.long_break_duration = long_break_duration
        self.member = guild.get_member(member_id)
        self.pomodoro_role = guild.get_role(config.ID_POMODORO_ROLE)
        self.default_role = guild.get_role(config.ID_DEFAULT_ROLE)
        self.iteration = iteration

    async def create_initial_message(self):
        global timer_dict

        self.message = await self.channel.send(embed=timer_running_embed_template(self.end_time, self.is_pomodoro))
        await self.message.add_reaction("🔴")
        timer_dict[self.member.id] = self.to_dict()
        dump_json()

    async def update_timer(self):
        if is_time_in_past(self.end_time):
            await self.end_timer()

        elif self.message is not None:
            await self.message.edit(embed=timer_running_embed_template(self.end_time, self.is_pomodoro))

    async def end_timer(self):
        await self.message.edit(embed=timer_ended_embed_template(self.end_time, self.is_pomodoro))
        await self.channel.send(timer_ended_message_template(self.member, self.is_pomodoro))
        await self.continue_pomodoro()

    async def continue_pomodoro(self):
        """
        Creates the next timer object based on current timer object information
        """
        global timer_dict

        next_timer = timer(
            self.guild,
            not self.is_pomodoro,
            self.channel.id,
            self.pomodoro_duration,
            self.break_duration,
            self.long_break_duration,
            self.member.id,
            self.iteration + 1
        )

        await next_timer.create_initial_message()

    async def end_pomodoro_session(self):
        global timer_dict
        del timer_dict[self.member.id]

        await self.member.remove_roles(self.pomodoro_role)
        await self.member.add_roles(self.default_role)
        await self.channel.delete()

        dump_json()

    def to_dict(self):
        return {
            "is_pomodoro": self.is_pomodoro,
            "channel_id": self.channel.id,
            "pomodoro_duration": self.pomodoro_duration,
            "break_duration": self.break_duration,
            "long_break_duration": self.long_break_duration,
            "member_id": self.member.id,
            "iteration": self.iteration,
            "end_time": self.end_time.strftime("%H:%M"),
            "message_id": self.message.id
        }


class pomodoro(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.update_time.start()
        self.guild = None
        self.pomodoro_role = None
        self.pomodoro_category = None
        self.default_role = None
        self.everyone_role = None

    def cog_unload(self):
        self.update_time.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.client.get_guild(config.ID_GUILD)
        self.pomodoro_category = self.guild.get_channel(config.ID_POMODORO_CATEGORY)
        self.pomodoro_role = self.guild.get_role(config.ID_POMODORO_ROLE)
        self.default_role = self.guild.get_role(config.ID_DEFAULT_ROLE)
        self.everyone_role = self.guild.get_role(config.ID_EVERYONE_ROLE)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member == self.client.user:
            return

        if str(payload.emoji) != str("🔴"):
            return

        if payload.member.id in timer_dict:
            t = timer_dict[payload.member.id]
            if t["channel_id"] == payload.channel_id:
                timer_obj = timer(
                    self.guild,
                    t["is_pomodoro"],
                    t["channel_id"],
                    t["pomodoro_duration"],
                    t["break_duration"],
                    t["long_break_duration"],
                    t["member_id"],
                    t["iteration"]
                )

                await timer_obj.end_pomodoro_session()

    async def add_initial_timer(self, channel_id, member_id, pomodoro_duration, break_duration, long_break_duration):
        timer_obj = timer(
            self.guild,
            True,
            channel_id,
            pomodoro_duration,
            break_duration,
            long_break_duration,
            member_id,
            1
        )
        await timer_obj.create_initial_message()

    @commands.command(name="pomodoro")
    async def pomodoro(self, ctx, *args):
        member = ctx.message.author
        await ctx.message.delete()  # Always remove message

        if self.pomodoro_role in member.roles:
            await member.send(
                "⚠️Já estás numa sessão de estudo pomodoro.\nTens de sair primeiro desta, reagindo com :red_circle: a "
                "um temporizador")
            return

        if len(args) != 3:
            await member.send(
                "⚠️Utilização: `!pomodoro [duração do tempo de estudo] [duração do tempo de pausa curta] [duração do "
                "tempo de pausa longa]`\n "
                "Exemplos: `!pomodoro 45 10 15` ou `!pomodoro 25 5 10`")
            return

        if not (0 < int(args[0]) < 600 and 0 < int(args[1]) < 600 and 0 < int(args[2]) < 600):
            await member.send("⚠️ As durações especificadas não são válidas")
            return

        if not (args[0].isnumeric() and args[1].isnumeric() and args[2].isnumeric()):
            await member.send("⚠️ As durações especificadas não são válidas")

        pomodoro_duration = args[0] + " min"
        break_duration = args[1] + " min"
        long_break_duration = args[2] + " min"

        channel = await self.create_pomodoro_channel(member)
        await self.add_initial_timer(channel.id, member.id, pomodoro_duration, break_duration, long_break_duration)

    async def create_pomodoro_channel(self, member):
        # Setup channel visibility settings
        overwrites = {
            self.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            self.everyone_role: discord.PermissionOverwrite(view_channel=False),
        }

        await member.add_roles(self.pomodoro_role)
        await member.remove_roles(self.default_role)

        channel = await self.guild.create_text_channel(name=f"Pomodoro {member.name}", category=self.pomodoro_category,
                                                       overwrites=overwrites)
        await channel.send(pomodoro_initial_message_template(member))

        return channel

    @tasks.loop(seconds=1)
    async def update_time(self):
        for t in list(timer_dict.values()):
            timer_obj = timer(
                self.guild,
                t["is_pomodoro"],
                t["channel_id"],
                t["pomodoro_duration"],
                t["break_duration"],
                t["long_break_duration"],
                t["member_id"],
                t["iteration"],
                get_date_from_duration(t["end_time"]),
                t["message_id"]
            )
            await timer_obj.update_timer()

    @update_time.before_loop
    async def before_update_time(self):
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(pomodoro(client))
