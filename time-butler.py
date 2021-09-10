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
    worked, msg = interpret(datetime, display, name=name)
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
    await ctx.send(text.translate(SMALL_CAPS))


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
    await ctx.send(text.translate(TINY_TEXT))


def contains(string, fragments):
    return any(f in string for f in fragments.split())


@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
        return
    if not isinstance(message.channel, DMChannel):
        return
    worked, response = interpret(message.content, "all")
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
