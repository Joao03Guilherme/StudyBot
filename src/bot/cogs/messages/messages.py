import asyncio

import config
import nextcord.errors
from nextcord.ext import commands

l = ["nitro", "http", "@everyone"]
allowed_roles = ["admin"]
ban_msg = """
Olá {USER_MENTION} 👋
Foste removido do servidor, se quiseres voltar a entrar segue o link: 
https://discord.gg/RBST2BgDy3"""


class messages(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.client.get_guild(config.ID_GUILD)
        self.staff_channel = self.client.get_channel(config.ID_STAFF_CHANNEL)

    @commands.Cog.listener()
    async def on_message(self, message):
        content = message.content.lower()
        for part in l:
            if part not in content:
                return

        member = message.author
        if any(role.name in allowed_roles for role in member.roles):
            return

        await member.ban(reason="Discord nitro spam")
        try:
            ban_msg.replace("{USER_MENTION}", member.mention)
            await member.send(ban_msg)
        except nextcord.errors.Forbidden:
            pass  # Can't send message to user

        await asyncio.sleep(10)
        await member.unban()

        # Alert staff
        await self.staff_channel.send(f"O utilizador _{member.name}_ deu fake nitro spam. \
        \nAs ações necessárias já foram tomadas.")


def setup(client):
    client.add_cog(messages(client))
