from dataclasses import dataclass
from datetime import timedelta

from discord import User
from discord.message import Message

from discord.role import Role
from discord.ext import tasks, commands
from discord.utils import get

from context import bot, slash, STRING, GUILDS, STORAGE
from discord_slash import SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_actionrow, create_select, create_select_option

from when import interpret, now, DATE_OPTIONS

ROLE = 8

# {message: Event}
STORAGE.setdefault("events", {})
# {user: {message: timestamp}}
STORAGE.setdefault("event_reminders", {})
# {guild: role_id}
STORAGE.setdefault("event_role", {})


@dataclass
class Event:
    name: str
    timestamp: int
    guild_id: int
    channel_id: int
    msg_id: int

    @classmethod
    def get(cls, msg_id) -> "Event":
        return STORAGE["events"][msg_id]

    @property
    def message_URL(self) -> str:
        return f"https://discord.com/channels/{self.guild_id}/{self.channel_id}/{self.msg_id}/"

    async def message_fetch(self):
        if ch := bot.get_channel(self.channel_id):
            return await ch.fetch_message(self.msg_id)
        return None


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
            name="role",
            description="The role which may create events",
            option_type=ROLE,
            required=True,
        )
    ]
)
async def event_creator_role(
    ctx: SlashContext,
    role: Role,
):
    """Admins only! Restrict event creation to a given role."""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("Only administrators can set the role for event creation.", hidden=True)
    STORAGE["event_role"][ctx.guild_id] = role.id
    STORAGE.save()
    is_everyone = role == ctx.guild.default_role
    await ctx.send(f"Okay, {'everyone' if is_everyone else f'only <@&{role.id}>'} may create events.", hidden=True)


@slash.slash(
    guild_ids=GUILDS,
    options=[
        create_option(
            name="name",
            description='''The event's name.''',
            option_type=STRING,
            required=True,
        )
    ] + DATE_OPTIONS
)
async def create_event(
    ctx: SlashContext,
    name: str,
    datetime: str,
    display: str = "auto",
):
    '''Display a named event in the future, which people can set reminders for.'''

    role_id = STORAGE["event_role"].get(
        ctx.guild_id, ctx.guild.default_role.id)
    if not get(ctx.author.roles, id=role_id):
        return await ctx.send(f"You don't have the role <@&{role_id}> required to create events", hidden=True)

    response = interpret(datetime, display, name=name)
    if not response.worked:
        return await ctx.send(response.msg, hidden=True)

    if response.datetime < now():
        return await ctx.send("This event has to be in the future!", hidden=True)

    timestamp = int(response.datetime.timestamp())

    delta: timedelta = abs(now() - response.datetime)
    components = [create_actionrow(create_select(
        placeholder="Select an option to be reminded for this time!",
        options=[
            create_select_option(
                text, value=f"{seconds} {timestamp - seconds}")
            for seconds, text in REMINDERS.items()
            if seconds <= delta / timedelta(seconds=1)
        ],
    ))]
    msg: Message = await ctx.send(response.msg, components=components)

    STORAGE["events"][msg.id] = Event(
        name=name,
        timestamp=int(response.datetime.timestamp()),
        guild_id=ctx.guild_id,
        channel_id=ctx.channel_id,
        msg_id=msg.id
    )


@bot.event
async def on_component(ctx: ComponentContext):
    if len(ctx.selected_options) != 1:
        return
    offset, timestamp = ctx.selected_options[0].split(" ")
    timestamp = int(timestamp)
    offset = int(offset)
    reminder_type = REMINDERS[offset].lower()

    msg_id = ctx.origin_message_id
    STORAGE["event_reminders"].setdefault(ctx.author.id, {})

    # TODO: figure out a way to delete these when not in use anymore D:
    STORAGE["event_messages"][msg_id] = (ctx.guild_id, ctx.channel.id)

    STORAGE["event_reminders"][ctx.author.id][msg_id] = timestamp
    STORAGE.save()

    if timestamp <= int(now().timestamp()):
        del STORAGE["event_reminders"][ctx.author.id][msg_id]
        await ctx.send(f"I can't set a reminder – the event happened <t:{timestamp}:R>!", hidden=True)
    elif offset == -1:
        await ctx.send("Reminder cancelled!", hidden=True)
    else:
        await ctx.send(f"Reminder set for {reminder_type}!", hidden=True)

    print(STORAGE)


@tasks.loop(seconds=10.0)
async def reminder():
    '''Remind users of notifications'''
    NOW = int(now().timestamp())
    for user_id, reminders in STORAGE["event_reminders"]:
        for msg_id, timestamp in reminders.items():
            if NOW > timestamp:
                user: User = await bot.fetch_user(user_id)
                user.send(
                    "🔔 You requested I give you a notification, so here you are!")


@tasks.loop(seconds=300)
async def purger():
    '''Purge events that have passed'''
    STORAGE["event_reminders"].sort(key=lambda event: event.timestamp)

    NOW = int(now().timestamp())
    for i, event in enumerate(STORAGE["event_reminders"]):
        if NOW > event.timestamp:
            pass
            # somehow remove all in the past?? idfk


@reminder.before_loop
@purger.before_loop
async def wait_for_bot():
    await bot.wait_until_ready()


@slash.slash(
    guild_ids=GUILDS,
)
async def upcoming(ctx: SlashContext):
    '''Show all upcoming events you set a reminder for.'''
    reminders = STORAGE["event_reminders"].get(ctx.author.id, {})

    NOW = int(now().timestamp())

    if not reminders:
        return await ctx.send("You have no reminders set! Try setting an `/event`.", hidden=True)

    msg = "Your reminders are:\n"
    for timestamp, msg_id in sorted((t, u) for u, t in reminders.items()):
        if timestamp < NOW:
            # somehow in the past?
            del reminders[msg_id]

        reminder = f"<t:{timestamp}:R> at <t:{timestamp}:f>"
        event = Event.get(msg_id)
        if msg_id in STORAGE["event_messages"]:
            reminder = (await event.message(msg_id)).content
            reminder += f" {message_URL(msg_id)} \n"
            msg += reminder

    return await ctx.send(msg.strip(), hidden=True)
