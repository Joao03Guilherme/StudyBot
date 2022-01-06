import nextcord

def greet_message(member, rules_channel, roles_channel):
    message = f'Olá {member.mention}, bem vindo/a ao servidor :grinning:!\n' \
              f'Antes de mais, certifica-te que passas pelo canal :scroll:{rules_channel.mention} para perceberes ' \
              f'melhor como o servidor funciona.\n' \
              f"Depois disso, passa pelo canal {roles_channel.mention} para escolheres **o teu ano** e teres acesso ao resto do servidor!\n" \
              "Bom estudo! :blue_book:"

    return message