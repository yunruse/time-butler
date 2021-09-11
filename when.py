from datetime import datetime, time, timedelta
from dataclasses import dataclass
from typing import Optional

from dateparser import parse
from discord import channel
from discord.message import Message

from context import bot, slash, STRING, GUILDS, STORAGE
from discord_slash import SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select, create_select_option
from discord_slash.model import ButtonStyle

FORMATS = "RtTdDfF"
now = datetime.now

# {user: {(guild, channel, message): timestamp}}
STORAGE.setdefault("event_reminders", {})


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
        msg = f"{name} " + ('will be' if in_future else 'was') + " "

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


REMINDERS = {
    -1: "Cancel that reminder!",
    0: "At the event",
    60: "A minute before",
    60 * 5: "5 minutes before",
    60 * 60: "An hour before",
    60 * 60 * 24: "A day before",
    60 * 60 * 24 * 7: "A week before"
}


@slash.slash(
    guild_ids=GUILDS,
    options=[
        create_option(
            name="datetime",
            description='''The time (and date, if not today). Can be relative ("Tomorrow at 2pm") and accepts most languages.''',
            option_type=STRING,
            required=True
        ),
        create_option(
            name="name",
            description='''Provide a name to the event.''',
            option_type=STRING,
            required=False
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
)
async def when(
    ctx: SlashContext,
    datetime: str,
    name: str = None,
    display: str = "auto",
):
    '''Display a date and time in an easy-to-read way.'''
    response = interpret(datetime, display, name=name)
    if not response.worked:
        return await ctx.author.send(response.msg)

    delta: timedelta = abs(now() - response.datetime)
    in_future: bool = now() <= response.datetime

    components = []

    if in_future:
        options = []
        for seconds, text in REMINDERS.items():
            if seconds > delta.seconds:
                continue
            options.append(create_select_option(
                text, value=f"{seconds} {int(response.datetime.timestamp()) - seconds}"))

        components = [create_actionrow(create_select(
            options=options,
            placeholder="Select an option to be reminded for this time!"
        ))]
    await ctx.send(response.msg, components=components)


@bot.event
async def on_component(ctx: ComponentContext):
    await ctx.defer(hidden=True)

    if len(ctx.selected_options) != 1:
        return
    offset, timestamp = ctx.selected_options[0].split(" ")
    timestamp = int(timestamp)
    offset = int(offset)
    reminder_type = REMINDERS[offset].lower()

    STORAGE["event_reminders"].setdefault(ctx.author.id, {})
    key = (ctx.guild_id, ctx.channel.id, ctx.origin_message_id)
    STORAGE["event_reminders"][ctx.author.id][key] = timestamp

    if offset == -1:
        await ctx.send(content=f"Reminder cancelled!")
    else:
        await ctx.send(content=f"Reminder set for {reminder_type}!")

    print(STORAGE)


@slash.slash(
    guild_ids=GUILDS,
)
async def upcoming(ctx: SlashContext):
    '''Show all upcoming events you set a reminder for.'''
    await ctx.defer(hidden=True)

    reminders = STORAGE["event_reminders"].get(ctx.author.id, {})

    if not reminders:
        return await ctx.send("You have no reminders set! Use `/when` in a server to set an event that others can be reminded of.")

    msg = "Your reminders are:\n"
    for timestamp, (guild, channel, message) in sorted((t, u) for u, t in reminders.items()):
        if ch := bot.get_channel(channel):
            msg += (await ch.fetch_message(message)).content
        else:
            msg += f"<t:{timestamp}:R> at <t:{timestamp}:f>"
        msg += f" https://discord.com/channels/{guild}/{channel}/{message}/ \n"

    return await ctx.send(msg.strip())
