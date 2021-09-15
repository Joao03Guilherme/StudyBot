import discord

EMBED_COLOR = 0x04caff


def greet_message(member, rules_channel, roles_channel):
    message = f'Olá {member.mention}, bem vindo/a ao servidor :grinning:!\n' \
              f'Antes de mais, certifica-te que passas pelo canal :scroll:{rules_channel.mention} para perceberes ' \
              f'melhor como o servidor funciona.\n' \
              f"Depois disso, passa pelo canal {roles_channel.mention} para escolheres o teu ano letivo e teres " \
              f"acesso ao resto do servidor!\n" \
              "Bom estudo! :blue_book:"

    return message


def role_message(decimo_emoji, decimoprimeiro_emoji, decimosegundo_emoji):
    embed = discord.Embed(title="Escolhe o teu ano!", color=EMBED_COLOR)
    embed.add_field(name="**10º Ano**", value=f"Se estás no **10º** ano reage com {decimo_emoji}")
    embed.add_field(name="**11º Ano**", value=f"Se estás no **11º** ano reage com {decimoprimeiro_emoji}")
    embed.add_field(name="**12º Ano**", value=f"Se estás no **12º** ano reage com {decimosegundo_emoji}")

    return embed

