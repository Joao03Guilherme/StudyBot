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


def setup(client):
    client.add_cog(announcements(client))