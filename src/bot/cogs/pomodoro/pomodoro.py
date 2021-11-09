import discord
import config
from discord.errors import NotFound
from .pomodoro_messages import break_running_embed_template, break_ended_embed_template, break_ended_message_template, \
    pomodoro_initial_message_template
from .utils import get_date_from_arguments, is_time_in_past
from discord.ext import commands, tasks

timer_list = []


class timer:
    def __init__(self, is_pomodoro, channel, pomodoro_time: str, break_time: str, long_break_time: str, end_time, member, pomodoro_role,
                 default_role, iteration):
        self.is_pomodoro = is_pomodoro
        self.channel = channel
        self.message = None
        self.end_time = end_time
        self.pomodoro_time = pomodoro_time
        self.break_time = break_time
        self.long_break_time = long_break_time
        self.member = member
        self.has_ended = False
        self.pomodoro_role = pomodoro_role
        self.default_role = default_role
        self.iteration = iteration

    async def initial_message(self):
        self.message = await self.channel.send(embed=break_running_embed_template(self.end_time, self.is_pomodoro))
        await self.message.add_reaction("🔴")
        timer_list.append(self)

    async def update_timer(self):
        if self.message is None or self.has_ended:
            return

        if is_time_in_past(self.end_time):
            self.has_ended = True
            await self.end_timer()
        else:
            try:
                await self.message.edit(embed=break_running_embed_template(self.end_time, self.is_pomodoro))
            except NotFound:
                raise NotFound

    async def end_timer(self):
        await self.message.edit(embed=break_ended_embed_template(self.end_time, self.is_pomodoro))
        await self.channel.send(break_ended_message_template(self.member, self.is_pomodoro))
        await self.continue_pomodoro()

    async def continue_pomodoro(self):
        end_time = get_date_from_arguments(self.pomodoro_time if not self.is_pomodoro else self.break_time if ((self.iteration+1)//2)%config.POMODORO_ITERATIONS != 0 else self.long_break_time)
        timer_list.append(
            timer(not self.is_pomodoro, self.channel, self.pomodoro_time, self.break_time, self.long_break_time, end_time, self.member,
                  self.pomodoro_role, self.default_role, self.iteration+1)
        )
        await timer_list[-1].initial_message()

    async def end_pomodoro_session(self):
        await self.member.remove_roles(self.pomodoro_role)
        await self.member.add_roles(self.default_role)
        await self.channel.delete()


class pomodoro(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.channels = {}
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

        for timer_object in timer_list:
            if timer_object.message.id == payload.message_id:
                if str(payload.emoji) == str("🔴"):
                    timer_list.remove(timer_object)
                    await timer_object.end_pomodoro_session()

    async def add_timer(self, channel, member, pomodoro_time, break_time, long_break_time):
        end_time = get_date_from_arguments(pomodoro_time)
        timer_list.append(
            timer(True, channel, pomodoro_time, break_time, long_break_time, end_time, member, self.pomodoro_role, self.default_role, 1)
        )
        await timer_list[-1].initial_message()

    @commands.command(name="pomodoro")
    async def pomodoro(self, ctx, *args):
        if self.pomodoro_role in ctx.message.author.roles:
            await ctx.message.author.send(
                "⚠️Já estás numa sessão de estudo pomodoro.\n" \
                "Tens de sair primeiro desta, reagindo com :red_circle: ao temporizador atual para criar outra sessão de estudo")
            await ctx.message.delete()
            return

        elif len(args) != 3:
            await ctx.message.user.send(
                "⚠️Utilização: `!pomodoro [duração do tempo de estudo] [duração do tempo de pausa curta] [duração do tempo de pausa longa]`\n"
                "Exemplos: `!pomodoro 45 10 15` ou `!pomodoro 25 5 10`")
            await ctx.message.delete()
            return

        try:
            if not (0 < int(args[0]) < 600 and 0 < int(args[1]) < 600 and 0 < int(args[2]) < 600):
                await ctx.message.author.send("⚠️ As durações especificadas não são válidas")
                await ctx.message.delete()
                return
        except ValueError or TypeError:
            await ctx.message.author.send("⚠️ As durações especificadas não são um número inteiro")
            await ctx.message.delete()
            return

        channel = await self.create_pomodoro_channel(ctx.message.author)
        pomodoro_time = args[0] + " min"
        break_time = args[1] + " min"
        long_break_time = args[2] + " min"
        await self.add_timer(channel, ctx.message.author, pomodoro_time, break_time, long_break_time)
        await ctx.message.delete()

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
        self.channels[member] = channel
        return channel

    async def delete_pomodoro_channel(self, member):
        await member.remove_roles(self.pomodoro_role)
        channel = self.channels[member]
        await channel.delete()
        del self.channels[member]

    @tasks.loop(seconds=1)
    async def update_time(self):
        for timer_object in timer_list:
            try:
                await timer_object.update_timer()
            except:
                pass
            if timer_object.has_ended:
                timer_list.remove(timer_object)

    @update_time.before_loop
    async def before_update_time(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(pomodoro(client))