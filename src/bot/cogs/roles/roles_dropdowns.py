import nextcord


class YearDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="10º Ano", emoji="🟠"),
            nextcord.SelectOption(label="11º Ano", emoji="🟣"),
            nextcord.SelectOption(label="12º Ano", emoji="🔵"),
            nextcord.SelectOption(label="Universidade", emoji="📗"),
        ]
        super().__init__(placeholder="Escolhe o teu ano", max_values=1, min_values=1, options=options, custom_id="YearDropdown")

    async def callback(self, interaction : nextcord.Interaction):
        await interaction.response.send_message(f"A role `{self.values[0]}` foi aplicada.", ephemeral=True)


class SubjectDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label = "Matemática", emoji="📐"),
            nextcord.SelectOption(label="Português", emoji="🇵🇹"),
            nextcord.SelectOption(label="Física", emoji="🪂"),
            nextcord.SelectOption(label="Química", emoji="💧"),
            nextcord.SelectOption(label="Biologia", emoji="🌱"),
            nextcord.SelectOption(label="Geologia", emoji="⛏"),
        ]
        super().__init__(placeholder="Escolhe as tuas disciplinas", max_values=6, min_values=0, options=options, custom_id="SubjectDropdown")

    async def callback(self, interaction : nextcord.Interaction):
        if len(self.values) == 1:
            await interaction.response.send_message(f"A disciplina selecionada foi aplicada", ephemeral=True)
        else:
            await interaction.response.send_message(f"As disciplinas selecionadas foram aplicadas", ephemeral=True)

class GamingDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="Fanático dos jogos"),
            nextcord.SelectOption(label="Gamer casual"),
        ]
        super().__init__(placeholder="Se gostares de jogos, escolhe uma opção", max_values=2, min_values=0, options=options, custom_id="GamingDropdown")

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(f"As Roles foram aplicadas.", ephemeral=True)

class YearDropdownViewer(nextcord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.add_item(YearDropdown())
        self.ctx = ctx

    async def interaction_check(self, interaction : nextcord.Interaction):
        if self.ctx.author == interaction.user:
            pass



class SubjectDropdownViewer(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SubjectDropdown())

class GamingDropdownViewer(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(GamingDropdown())

