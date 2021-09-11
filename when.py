from datetime import datetime, time, timedelta
from dataclasses import dataclass
from typing import Optional

from dateparser import parse

from context import slash, STRING, GUILDS
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

FORMATS = "RtTdDfF"
now = datetime.now



@dataclass
class InterpretResult:
    worked: bool
    msg: str
    datetime: Optional[datetime] = None


def interpret(string, fmt: str, name: str = None) -> InterpretResult:
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
        return InterpretResult(False, f"Sorry, I didn't understand what you mean by `{string}`! :(")

    now = datetime.now()
    unix = int(dt.timestamp())
    utc = datetime.fromtimestamp(unix)

    in_future = utc >= now

    if fmt == "all":
        msg = "You can present this in a variety of ways:\n"
        for code in FORMATS:
            msg += f"Type `<t:{unix}:{code}>` to get <t:{unix}:{code}>\n"
        msg += "These messages all adapt to the time zone of the reader! \n"
        msg += f"Don't forget to add the UTC timestamp ({utc.strftime('%Y-%m-%d %H:%M:%S')} UTC)"
        msg += ", just in case someone is using an older version of Discord!"
        return InterpretResult(True, msg, utc)

    msg = ""
    if name is not None:
        msg = f"**{name}** will be "

    if fmt == "auto":
        fmt = "F"
        utc_fmt = '%Y-%m-%d %H:%M:%S'
        # TODO: use other codes based on context (e.g. time not provided)

        msg += f"<t:{unix}:R> "
        msg += "on" if in_future else "at"
        msg += f" <t:{unix}:{fmt}> ({utc.strftime(utc_fmt)} UTC)"
    else:
        if name is not None:
            msg += "on" if in_future else "at"
        msg += f" <t:{unix}:{fmt}>"
    return InterpretResult(True, msg.strip(), utc)


DATE_OPTIONS = [
    create_option(
        name="datetime",
        description='''The time (and date, if not today). Can be relative ("Tomorrow at 2pm") and accepts most languages.''',
        option_type=STRING,
        required=True
    ),
    create_option(
        name="display",
        description="Method of display",
        option_type=STRING,
        required=False,
        choices=[
            create_choice(name="Automatic", value="auto"),
            create_choice(name="Relative (In x hours, etc)", value="R"),
            create_choice(name="Time (HH:MM)", value="t"),
            create_choice(name="Time (HH:MM:SS)", value="T"),
            create_choice(name="Date (numbers)", value="d"),
            create_choice(name="Date (words)", value="D"),
            create_choice(name="Date (words + time)", value="f"),
            create_choice(name="Date (words + time + weekday)", value="F"),
            create_choice(name="Display ALL formats", value="all"),
        ]
    ),
]


@slash.slash(
    guild_ids=GUILDS,
    options=DATE_OPTIONS
)
async def when(
    ctx: SlashContext,
    datetime: str,
    display: str = "auto",
):
    '''Display a date and time in an easy-to-read way.'''
    response = interpret(datetime, display)
    if not response.worked:
        return await ctx.author.send(response.msg)
    await ctx.send(response.msg)
