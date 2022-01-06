from datetime import time, datetime, timedelta
import pytz
from nextcord.errors import InvalidArgument
import config

timezone = pytz.timezone(config.TIMEZONE)


def get_date_from_duration(time_str):
    """
        Recebe uma string das formas: "x min", "x horas", "x horas y min" ou "xx:yy" e converte
        num objeto datetime timezone-aware em UTC
    :param args: command arguments
    :return: a datetime object, the date obtained from offset or directly from time arguments
    """
    args = time_str.split(" ")
    try:
        if len(args) == 1:
            horas = int(args[0].split(":")[0])
            minutos = int(args[0].split(":")[1])
            local = timezone.localize(
                datetime.combine(datetime.now(tz=timezone).date(), time(hour=horas, minute=minutos, second=0)))
            return local.astimezone(pytz.utc)

        elif len(args) == 2:
            if args[1].lower() in ["hora", "hr", "h", "horas"]:
                intervalo_horas = int(args[0])
                return pytz.utc.localize(datetime.utcnow() + timedelta(hours=intervalo_horas))
            else:
                intervalo_minutos = int(args[0])
                return pytz.utc.localize(datetime.utcnow() + timedelta(minutes=intervalo_minutos))

        elif len(args) == 4:
            intervalo_horas = int(args[0])
            intervalo_minutos = int(args[2])
            return pytz.utc.localize(datetime.utcnow() + timedelta(hours=intervalo_horas, minutes=intervalo_minutos))
    except Exception:
        pass
    raise InvalidArgument


def is_time_in_past(hora_de_fim):
    return hora_de_fim <= pytz.utc.localize(datetime.utcnow())


def format_datetime_or_timedelta(data):
    """
        Converte objetos datetime e timedelta para strings.
        No objeto datetime, é feita a conversão para tempo local
    :param data:
    :return:
    """
    if isinstance(data, datetime):
        return data.astimezone(timezone).strftime("%H:%M")

    # Calcular o tempo restante (chamado das funções editar mensagem e criar mensagem)
    elif isinstance(data, timedelta):
        segundos = int(data.total_seconds())
        horas, remainder = divmod(segundos, 3600)
        minutos, segundos = divmod(remainder, 60)

        restante = datetime.combine(datetime.today(), time(hour=horas, minute=minutos, second=segundos))
        if horas > 0:
            return restante.strftime("%H:%M:%S")
        return restante.strftime("%M:%S")
