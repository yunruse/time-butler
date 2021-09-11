from datetime import timedelta

from discord.role import Role

from context import bot, slash, STRING, GUILDS, STORAGE
from discord.utils import get
from discord_slash import SlashContext, ComponentContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_actionrow, create_select, create_select_option

from when import interpret, now, DATE_OPTIONS

ROLE = 8

# key :: (guild, channel, message)

# {user: {key: timestamp}}
STORAGE.setdefault("event_reminders", {})
# {guild: role_id}
STORAGE.setdefault("event_role", {})

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

    delta: timedelta = abs(now() - response.datetime)
    components = [create_actionrow(create_select(
        placeholder="Select an option to be reminded for this time!",
        options=[
            create_select_option(
                text, value=f"{seconds} {int(response.datetime.timestamp()) - seconds}")
            for seconds, text in REMINDERS.items()
            if seconds <= delta.seconds
        ],
    ))]
    await ctx.send(response.msg, components=components)


@bot.event
async def on_component(ctx: ComponentContext):
    if len(ctx.selected_options) != 1:
        return
    offset, timestamp = ctx.selected_options[0].split(" ")
    timestamp = int(timestamp)
    offset = int(offset)
    reminder_type = REMINDERS[offset].lower()

    STORAGE["event_reminders"].setdefault(ctx.author.id, {})
    key = (ctx.guild_id, ctx.channel.id, ctx.origin_message_id)
    STORAGE["event_reminders"][ctx.author.id][key] = timestamp

    if timestamp <= int(now().timestamp()):
        del STORAGE["event_reminders"][ctx.author.id][key]
        await ctx.send(f"I can't set a reminder – the event happened <t:{timestamp}:R>!", hidden=True)
    elif offset == -1:
        await ctx.send("Reminder cancelled!", hidden=True)
    else:
        await ctx.send(f"Reminder set for {reminder_type}!", hidden=True)

    print(STORAGE)


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
    for timestamp, key in sorted((t, u) for u, t in reminders.items()):
        if timestamp < NOW:
            # somehow in the past?
            del reminders[key]
        guild, channel, message = key

        if ch := bot.get_channel(channel):
            msg += (await ch.fetch_message(message)).content
        else:
            msg += f"<t:{timestamp}:R> at <t:{timestamp}:f>"
        msg += f" https://discord.com/channels/{guild}/{channel}/{message}/ \n"

    return await ctx.send(msg.strip(), hidden=True)
