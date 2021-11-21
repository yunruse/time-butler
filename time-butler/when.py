from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

from dateparser import DateDataParser

from context import slash, STRING, GUILDS
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from joke import joke_gif

FORMATS = "RtTdDfF"
now = datetime.now

PARSER = DateDataParser(settings={
    'RETURN_TIME_AS_PERIOD': True,
    'PREFER_DATES_FROM': 'future',
})


def parse(string):
    now = datetime.now()
    parsed = PARSER.get_date_data(string)
    dt = parsed.date_obj
    # For some reason, relative dates will always return "day", even if they're clearly providing a time.
    # We work around this by simply changing it iff the H:M:S is different.
    # If it's the same, we can safely assume "In two days" etc was used, so it can remain a date.
    if dt is not None:
        if parsed.period == "day" and (dt.hour, dt.minute, dt.second) != (now.hour, now.minute, now.second):
            parsed.period = "time"
    return parsed


@dataclass
class InterpretResult:
    worked: bool
    msg: str
    datetime: Optional[datetime] = None


def interpret(string, fmt: str, name: str = None) -> InterpretResult:
    parsed = parse(string)
    if parsed.date_obj is None:
        return InterpretResult(False, f"Sorry, I didn't understand what you mean by `{string}`! :(")

    if parsed.period not in ("time", "day"):
        return InterpretResult(
            False,
            f"Sorry - Discord doesn't have any magic display formats built in for a {parsed.period} :(")

    now = datetime.now()
    unix = int(parsed.date_obj.timestamp())
    utc = datetime.fromtimestamp(unix)

    in_future = utc >= now
    delta = abs(utc - now)
    time_show_seconds = parsed.date_obj.second != 0

    # TODO: Other languages based on parsed.locale
    WILL_BE = "will be" if in_future else "was"
    ON = "on" if fmt in "dDfF" else "at"

    if fmt == "all":
        msg = "You can present this in a variety of ways:\n"
        for code in FORMATS:
            msg += f"Type `<t:{unix}:{code}>` to get <t:{unix}:{code}>\n"
        msg += "These messages all adapt to the time zone of the reader! \n"
        msg += f"Don't forget to add the UTC timestamp ({utc.strftime('%Y-%m-%d %H:%M:%S')} UTC)"
        msg += ", just in case someone is using an older version of Discord!"
        return InterpretResult(True, msg, utc)

    msg = [] if name is None else [f"**{name}** {WILL_BE}"]

    if fmt == "auto":
        fmt = "F"
        utc_fmt = '%Y-%m-%d %H:%M'
        if parsed.period == "day":
            fmt = "D"
            utc_fmt = '%Y-%m-%d'
        elif delta < timedelta(days=1):
            fmt = "T" if time_show_seconds else "t"
            utc_fmt = '%H:%M'

        if time_show_seconds:
            utc_fmt = utc_fmt.replace('%M', '%M:%S')

        if name is None:
            msg.append(f"`{string}` {WILL_BE}")
        msg.append(f"<t:{unix}:R> {ON} <t:{unix}:{fmt}>")
        msg.append(f"({utc.strftime(utc_fmt)} UTC)")
    else:
        if name is not None:
            msg.append(ON)
        msg.append(f" <t:{unix}:{fmt}>")
    return InterpretResult(True, " ".join(msg), utc)


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
    options=DATE_OPTIONS + [
        create_option(
            name="name",
            description="Give the event a name",
            option_type=STRING,
            required=False,
        )
    ]
)
async def when(
    ctx: SlashContext,
    datetime: str,
    display: str = "auto",
    name: str = None,
):
    '''Display a date and time in an easy-to-read way.'''
    response = interpret(datetime, display, name)
    await ctx.send(response.msg, hidden=not response.worked)
