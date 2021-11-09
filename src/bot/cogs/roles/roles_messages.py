import discord


EMBED_COLOR = 0x04caff
EMBED_COLOR_UNI = 0x16c644
EMBED_COLOR_DISCIPLINES = 0x9c0f06

def role_message(decimo_emoji, decimoprimeiro_emoji, decimosegundo_emoji):
    embed = discord.Embed(title="Escolhe o teu ano!", color=EMBED_COLOR)
    embed.add_field(name="**10º Ano**", value=f"Se estás no **10º** ano reage com {decimo_emoji}")
    embed.add_field(name="**11º Ano**", value=f"Se estás no **11º** ano reage com {decimoprimeiro_emoji}")
    embed.add_field(name="**12º Ano**", value=f"Se estás no **12º** ano reage com {decimosegundo_emoji}")

    return embed

def role_message_uni(universidade_emoji):
    embed = discord.Embed(title="Universidade", color=EMBED_COLOR_UNI)
    embed.add_field(name="**Universitário**", value=f"Se estás na **universidade** reage com {universidade_emoji}")

    return embed

def role_message_disciplines():
    embed = discord.Embed(title="Disciplinas", color=EMBED_COLOR_DISCIPLINES)
    embed.add_field(name="**Matemática**", value=f"Para receber notificações desta disciplina reage com 📐")
    embed.add_field(name="**Física**", value=f"Para receber notificações desta disciplina reage com 🪂")
    embed.add_field(name="**Química**", value=f"Para receber notificações desta disciplina reage com 💧")
    embed.add_field(name="**Biologia**", value=f"Para receber notificações desta disciplina reage com 🌱")
    embed.add_field(name="**Geologia**", value=f"Para receber notificações desta disciplina reage com ⛏")
    embed.add_field(name="**Português**", value=f"Para receber notificações desta disciplina reage com 🇵🇹")

    return embed

def greet_message(member, rules_channel, roles_channel):
    message = f'Olá {member.mention}, bem vindo/a ao servidor :grinning:!\n' \
              f'Antes de mais, certifica-te que passas pelo canal :scroll:{rules_channel.mention} para perceberes ' \
              f'melhor como o servidor funciona.\n' \
              f"Depois disso, passa pelo canal {roles_channel.mention} para escolheres o teu ano e teres acesso ao resto do servidor!\n" \
              "Bom estudo! :blue_book:"

    return message