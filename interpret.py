
from datetime import datetime
from enum import Enum

from dateparser import parse


class Format(Enum):
    all = 1
    date = 2
    datetime = 3


FORMATS = "RtTdDfF"


def interpret(string, fmt: Format, name: str = "Event"):
    dt = None
    try:
        dt = parse(string, settings={
            # 'TIMEZONE': tz,
            # TODO: user settings for this?
            'PREFER_DATES_FROM': 'future'
        })
    except ValueError:
        pass

    if dt is None:
        return (False, f"Sorry, I didn't understand what you mean by `{string}`! :(")

    now = datetime.now()
    unix = int(dt.timestamp())
    utc = datetime.fromtimestamp(unix)

    in_future = utc >= now
    days = abs(now - utc).days

    if fmt == Format.all:
        msg = "You can present this in a variety of ways:\n"
        for code in FORMATS:
            msg += f"Type `<t:{unix}:{code}>` to get <t:{unix}:{code}>\n"
        msg += "These messages all adapt to the time zone of the reader! \n"
        msg += f"Don't forget to add the UTC timestamp ({utc.strftime('%Y-%m-%d %H:%M:%S')} UTC)"
        msg += ", just in case someone is using an older version of Discord!"

    else:
        code = "D"
        utc_fmt = '%Y-%m-%d'
        if fmt == Format.datetime:
            code = "F"
            utc_fmt = '%Y-%m-%d %H:%M:%S'

        msg = f"{name} " + ('will be' if in_future else 'was')
        msg += f" <t:{unix}:R> "
        msg += "on" if in_future else "at"
        msg += f" <t:{unix}:{code}> ({utc.strftime(utc_fmt)} UTC)"
    return (True, msg)
