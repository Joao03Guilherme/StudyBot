import nextcord
import config
from nextcord.ext import commands
from .roles_greet import greet_message
from .roles_selection import YearDropdownViewer, SubjectDropdownViewer, GamingDropdownViewer, StudySessionButtonViewer


def may_use_command(ctx):
    return any(role.name == "admin" for role in ctx.message.author.roles)


class roles(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.client.get_guild(config.ID_GUILD)

        self.year_roles = {
            "DEFAULT": self.guild.get_role(config.ID_DEFAULT_ROLE),
            "10ANO": self.guild.get_role(config.ID_DECIMO_ROLE),
            "11ANO": self.guild.get_role(config.ID_DECIMOPRIMEIRO_ROLE),
            "12ANO": self.guild.get_role(config.ID_DECIMOSEGUNDO_ROLE),
            "UNIVERSIDADE": self.guild.get_role(config.ID_UNIVERSIDADE_ROLE),
        }

        self.subject_roles = {
            "MAT": self.guild.get_role(config.ID_MAT_ROLE),
            "PT": self.guild.get_role(config.ID_PT_ROLE),
            "FIS": self.guild.get_role(config.ID_FIS_ROLE),
            "QUI": self.guild.get_role(config.ID_CHEM_ROLE),
            "BIO": self.guild.get_role(config.ID_BIO_ROLE),
            "GEO": self.guild.get_role(config.ID_GEO_ROLE),
        }

        self.gaming_roles = {
            "JOGOS": self.guild.get_role(config.ID_JOGOS_ROLE),
            "FJOGOS": self.guild.get_role(config.ID_FJOGOS_ROLE),
        }

        self.study_session_role = self.guild.get_role(config.ID_STUDYSESSION_ROLE)

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

    @commands.command(name="enviar")
    @commands.check(may_use_command)
    async def enviar(self, ctx):
        v1 = YearDropdownViewer(self.year_roles)
        v2 = SubjectDropdownViewer(self.subject_roles)
        v3 = GamingDropdownViewer(self.gaming_roles)
        b1 = StudySessionButtonViewer(self.study_session_role)
        await ctx.send("➜ Seleciona o teu ano para teres acesso ao resto do servidor", view=v1)
        await ctx.send("➜ _Opcional:_ Seleciona as tuas disciplinas", view=v2)
        await ctx.send("➜ _Optional:_ Seleciona as tuas roles de gaming", view=v3)
        await ctx.send("➜ _Opcional:_ Se quiseres ser notificado sobre sessões de estudo, carrega no botão.\n_Para "
                       "deixar de receber notificações, carrega outra vez no botão._", view=b1)

def setup(client):
    client.add_cog(roles(client))
