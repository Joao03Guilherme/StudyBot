import nextcord

class YearDropdown(nextcord.ui.Select):
    def __init__(self, role_dict):
        options = [
            nextcord.SelectOption(label="10º Ano", value="10ANO", emoji="🟠"),
            nextcord.SelectOption(label="11º Ano", value="11ANO", emoji="🟣"),
            nextcord.SelectOption(label="12º Ano", value="12ANO", emoji="🔵"),
            nextcord.SelectOption(label="Universidade", value="UNIVERSIDADE", emoji="📗"),
        ]
        super().__init__(placeholder="Escolhe o teu ano", max_values=1, min_values=1, options=options,
                         custom_id="YearDropdown")
        self.role_dict = role_dict

    async def callback(self, interaction: nextcord.Interaction):
        user = interaction.user
        try:
            await user.add_roles(self.role_dict["DEFAULT"])
            for role in user.roles:
                if role in self.role_dict.values() and role != self.role_dict["DEFAULT"]:
                    await user.remove_roles(role)

            await user.add_roles(self.role_dict[self.values[0]])
            await interaction.response.send_message(f"✅ A role `{self.role_dict[self.values[0]].name}` foi aplicada "
                                                    f"com sucesso.", ephemeral=True)
        except:
            await interaction.response.send_message(f"❌ Ocorreu um erro a aplicar a role", ephemeral=True)


class SubjectDropdown(nextcord.ui.Select):
    def __init__(self, role_dict):
        options = [
            nextcord.SelectOption(label="Matemática", value="MAT", emoji="📐"),
            nextcord.SelectOption(label="Português", value="PT", emoji="🇵🇹"),
            nextcord.SelectOption(label="Física", value="FIS", emoji="🪂"),
            nextcord.SelectOption(label="Química", value="QUI", emoji="💧"),
            nextcord.SelectOption(label="Biologia", value="BIO", emoji="🌱"),
            nextcord.SelectOption(label="Geologia", value="GEO", emoji="⛏"),
        ]
        super().__init__(placeholder="Escolhe as tuas disciplinas", max_values=6, min_values=0, options=options,
                         custom_id="SubjectDropdown")
        self.role_dict = role_dict

    async def callback(self, interaction: nextcord.Interaction):
        user = interaction.user
        try:
            for role in user.roles:  # Remove all subject roles
                if role in self.role_dict.values():
                    await user.remove_roles(role)

            for role in self.values:
                await user.add_roles(self.role_dict[role])

            await interaction.response.send_message(f"✅ As alterações foram efetuadas com sucesso.",
                                                    ephemeral=True)
        except:
            await interaction.response.send_message(f"❌ Ocorreu um erro.", ephemeral=True)


class GamingDropdown(nextcord.ui.Select):
    def __init__(self, role_dict):
        options = [
            nextcord.SelectOption(label="Fanático dos jogos", value="FJOGOS", emoji="🎮"),
            nextcord.SelectOption(label="Gamer casual", value="JOGOS", emoji="🎲"),
            nextcord.SelectOption(label="Jogador de Xadrez", value="XADREZ", emoji="♟")
        ]
        super().__init__(placeholder="Se gostares de jogar alguma coisa, escolhe uma opção", max_values=2, min_values=0,
                         options=options, custom_id="GamingDropdown")
        self.role_dict = role_dict

    async def callback(self, interaction: nextcord.Interaction):
        user = interaction.user
        try:
            for role in user.roles:
                if role in self.role_dict.values():
                    await user.remove_roles(role)

            for role in self.values:
                await user.add_roles(self.role_dict[role])

            await interaction.response.send_message(f"✅ As Roles foram aplicadas.", ephemeral=True)
        except:
            await interaction.response.send_message(f"❌ Ocorreu um erro a aplicar a role.", ephemeral=True)


class StudySessionButton(nextcord.ui.Button):
    def __init__(self, study_session_role):
        super().__init__(style=nextcord.ButtonStyle.blurple, label="Sessões de estudo", custom_id="StudySessionButton")
        self.study_session_role = study_session_role

    async def callback(self, interaction: nextcord.Interaction):
        user = interaction.user
        try:
            if self.study_session_role in user.roles:
                await user.remove_roles(self.study_session_role)
                await interaction.response.send_message(f"✅ Deixarás de receber notificações de sessões de estudo.",
                                                        ephemeral=True)
            else:
                await user.add_roles(self.study_session_role)
                await interaction.response.send_message(f"✅ Irás receber notificações de sessões de estudo.",
                                                        ephemeral=True)
        except:
            await interaction.response.send_message(f"❌ Ocorreu um erro a aplicar a role.", ephemeral=True)


class YearDropdownViewer(nextcord.ui.View):
    def __init__(self, role_dict):
        super().__init__(timeout=None)
        self.add_item(YearDropdown(role_dict))


class SubjectDropdownViewer(nextcord.ui.View):
    def __init__(self, role_dict):
        super().__init__(timeout=None)
        self.add_item(SubjectDropdown(role_dict))


class GamingDropdownViewer(nextcord.ui.View):
    def __init__(self, role_dict):
        super().__init__(timeout=None)
        self.add_item(GamingDropdown(role_dict))


class StudySessionButtonViewer(nextcord.ui.View):
    def __init__(self, study_session_role):
        super().__init__(timeout=None)
        self.add_item(StudySessionButton(study_session_role))
