from datetime import datetime
import discord
from .utils import format_datetime_or_timedelta
import pytz

EMBED_COLOR = 0x04caff

# TODO: ADICIONAR UMA IMAGEM AO EMBED PARA FICAR MAIS BONITO
def break_running_embed_template(end_time, pomodoro):
    end_time_str = format_datetime_or_timedelta(end_time)
    time_remaining = end_time - pytz.utc.localize(datetime.utcnow())
    time_remaining_str = format_datetime_or_timedelta(time_remaining)

    title = "Período de estudo ⏰" if pomodoro else "Pausa ⏰"
    embed = discord.Embed(title=title, color=EMBED_COLOR)
    embed.add_field(name="Até às: ", value=end_time_str, inline=False)
    embed.add_field(name="Tempo restante: ", value=time_remaining_str, inline=False)
    return embed


def break_ended_embed_template(end_time, pomodoro):
    end_time_str = format_datetime_or_timedelta(end_time)
    title = "Período de estudo ⏰" if pomodoro else "Pausa ⏰"
    embed = discord.Embed(title=title, description="Terminado", color=EMBED_COLOR)
    embed.add_field(name="Até às: ", value=end_time_str, inline=False)
    embed.add_field(name="Tempo restante: ", value="Terminou", inline=False)
    return embed

def break_ended_message_template(member, pomodoro):
    msg = "⏰ O período de estudo terminou, faz agora uma pausa" if pomodoro else "⏰ A pausa terminou, começa agora outro período de estudo"
    return f"{member.mention} {msg}"

def pomodoro_initial_message_template(member):
    msg = f"Olá {member.mention}!\n" \
            "Apenas tu consegues ver este canal 🔐.\n" \
            "Alguns canais foram ocultados para te focares no estudo 📘.\n" \
            "Se quiseres terminar a sessão de estudo, basta carregar no 🔴 do temporizador atual 🕐.\n" \
            "Bom estudo! 💯"
    return msg
