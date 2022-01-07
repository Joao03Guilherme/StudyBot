from datetime import datetime, timedelta, time

import config
import nextcord
import pytz

timezone = pytz.timezone(config.TIMEZONE)
EMBED_COLOR = 0x04caff


def format_timedelta(date):
    segundos = int(date.total_seconds())
    horas, remainder = divmod(segundos, 3600)
    minutos, segundos = divmod(remainder, 60)

    restante = datetime.combine(datetime.today(), time(hour=horas, minute=minutos, second=segundos))
    if horas > 0:
        return restante.strftime("%H:%M:%S")
    return restante.strftime("%M:%S")


def timer_embed_template(end_time):
    end_time_str = end_time.astimezone(timezone).strftime("%H:%M")
    time_remaining: timedelta = end_time - datetime.today()
    time_remaining_str = format_timedelta(time_remaining)

    title = "Temporizador ⏰"
    embed = nextcord.Embed(title=title, color=EMBED_COLOR)
    embed.add_field(name="Até às: ", value=end_time_str, inline=False)
    embed.add_field(name="Tempo restante: ", value=time_remaining_str, inline=False)
    return embed


def timer_ended_embed_template(end_time):
    end_time_str = end_time.astimezone(timezone).strftime("%H:%M")
    title = "Temporizador terminado ⏰"
    embed = nextcord.Embed(title=title, description="Terminado", color=EMBED_COLOR)
    embed.add_field(name="Até às: ", value=end_time_str, inline=False)
    return embed


def pomodoro_initial_message_template(member):
    msg = f"Olá {member.mention}!\n" \
          "Apenas tu consegues ver este canal 🔐.\n" \
          "Alguns canais foram ocultados para te focares no estudo 📘.\n" \
          "Se quiseres terminar a sessão de estudo, basta carregar no 🔴 do temporizador atual 🕐.\n" \
          "Bom estudo! 💯"
    return msg


def pomodoro_timer_begins_template(member):
    return f"Começa agora um período de estudo, {member.mention}"


def break_timer_begins_template(member):
    return f"Começa agora um período de pausa, {member.mention}"
