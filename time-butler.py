from enum import Enum

from discord import Message, Emoji
from discord.channel import DMChannel
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from interpret import interpret, Format


class SendFormat(Enum):
    auto = "auto"
    relative = "r"
    date = "d"
    time = "t"
    datetime = "f"


STRING = 3

bot = Bot("/")
slash = SlashCommand(bot, sync_commands=True)


GUILDS = [885908649342537810]


@slash.slash(
    name="datetime",
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
            description='''The name of the event. Defaults to just "Event".''',
            option_type=STRING,
            required=False
        ),
    ]
)
async def _datetime(
    ctx: SlashContext,
    datetime: str,
    name: str = "Event",
    display: SendFormat = SendFormat.auto,
):
    '''Display a date and time in an easy-to-read way.'''
    worked, msg = interpret(datetime, Format.datetime, name=name)
    if worked:
        await ctx.send(msg)
    else:
        await ctx.author.send(msg)


@slash.slash(
    guild_ids=GUILDS,
    options=[
        create_option(
            name="date",
            description='''The date. Can be relative ("Next Tuesday") and accepts most languages.''',
            option_type=STRING,
            required=True
        ),
        create_option(
            name="name",
            description='''The name of the event. Defaults to just "Event".''',
            option_type=STRING,
            required=False
        )
    ]
)
async def date(ctx: SlashContext, date: str, name: str = "Event"):
    '''Display a date in an easy-to-read way.'''
    worked, msg = interpret(date, Format.date, name=name)
    if worked:
        await ctx.send(msg)
    else:
        await ctx.author.send(msg)


@slash.slash(
    guild_ids=GUILDS,
    options=[
        create_option(
            name="datetime",
            description='''The date and/or time. Can be relative ("Tomorrow at 2pm") and accepts most languages.''',
            option_type=3,
            required=True
        )
    ]
)
async def formats(ctx: SlashContext, datetime: str):
    '''Display all timestamp formats that can be used for a given date and/or time.'''
    worked, msg = interpret(datetime, Format.all)
    if worked:
        await ctx.send(msg)
    else:
        await ctx.author.send(msg)


SMALL_CAPS = str.maketrans(
    "abcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")
TINY_TEXT = str.maketrans(
    "ABCDEFGHIKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-=()ɑðəɩᶅʃƫʍʔ",
    "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴷᴸᴹᴺᴼᴾᵠᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ¹²³⁴⁵⁶⁷⁸⁹⁰⁻⁼⁽⁾ᵅᶞᵊᶥᶪᶴᶵꭩˀ"
)


@slash.slash(
    guild_ids=GUILDS,
    options=[
        create_option(
            name="text",
            description='''The text to make into small caps.''',
            option_type=STRING,
            required=True
        ),
    ]
)
async def smallcaps(ctx: SlashContext, text: str):
    '''Makes text have small caps (Lɪᴋᴇ ᴛʜɪs)'''
    await ctx.channel.send(text.translate(SMALL_CAPS))


@slash.slash(
    guild_ids=GUILDS,
    options=[
        create_option(
            name="text",
            description='''The text to make superscript.''',
            option_type=STRING,
            required=True
        ),
    ]
)
async def superscript(ctx: SlashContext, text: str):
    '''Makes text tiny and superscript ⁽ᴸᶦᵏᵉ ᵗʰᶦˢ⁾'''
    await ctx.channel.send(text.translate(TINY_TEXT))


def contains(string, fragments):
    return any(f in string for f in fragments.split())


@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
        return
    if not isinstance(message.channel, DMChannel):
        return
    worked, response = interpret(message.content, Format.all)
    if worked:
        await message.channel.send(response)
    else:
        msg = message.content.lower().strip()
        if contains(msg, "🍕 pizza spider-man spiderman spider"):
            await message.channel.send("https://tenor.com/view/spider-man-pizza-time-pizza-day-pizza-dinner-gif-16271126")
            return
        emoji = "❓"
        if contains(msg, "hey hi howdy hello hola"):
            emoji = "👋"
        elif "cake" in msg:
            emoji = "🍰"
        elif "how are you" in msg or "how's it going" in msg or "how are things" in msg:
            emoji = "☺️"
        elif contains(msg, "uprising overlord singularity beep boop bot"):
            emoji = "🤖"
        await message.add_reaction(emoji)


@bot.event
async def on_ready():
    print(f'Signed in as {bot.user}')

with open('oauth-token.txt') as f:
    TOKEN = f.read().strip()
bot.run(TOKEN)
