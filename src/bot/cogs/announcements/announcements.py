from discord.ext import commands
import config


class announcements(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="anunciar")
    async def announcement(self, ctx):
        guild = ctx.message.guild
        announcement_channel = guild.get_channel(config.ID_ANNOUNCEMENT_CHANNEL)
        default_role = guild.get_role(config.ID_DEFAULT_ROLE)

        await announcement_channel.send(f"{default_role.mention}\n" + ctx.message.content[10:])

    @commands.command(name="anunciar_canal")
    async def announcement_by_channel(self, ctx, *args):
        guild = ctx.message.guild
        channel_id = int(args[0])
        announcement_channel = guild.get_channel(channel_id)

        await announcement_channel.send(ctx.message.content[34:])


def setup(client):
    client.add_cog(announcements(client))