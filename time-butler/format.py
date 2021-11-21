import json
from string import ascii_lowercase, ascii_uppercase

from context import slash, STRING, GUILDS

from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from context import slash, STRING, GUILDS

# TODO:
# - Spaced out text  l i k e  t h i s  (with nbsp)
# - Spaced out text with fullwidth characters

TRANSFORMATIONS = {}
TRANSFORMATION_OPTIONS = []


def transform(text: str, format: str = ""):
    text = text.translate(TRANSFORMATIONS.get(format, {}))
    if format == "Upside down":
        text = text[::-1]
    return text


with open('format.json') as f:
    DATA: dict[str, object] = json.load(f)

for k, v in DATA.items():
    if isinstance(v, str):
        src = ascii_uppercase + ascii_lowercase
        dst = v
    else:
        src, dst = v

    TRANSFORMATIONS[k] = str.maketrans(src, dst)
    TRANSFORMATION_OPTIONS.append(create_choice(name=transform(k, k), value=k))

TRANSFORMATION_OPTIONS.append(create_choice(
    name="Hidden memo (only you can see it)", value="hidden"))


@slash.slash(
    guild_ids=GUILDS,
    options=[
        create_option(
            name="text",
            description='The text to transform!',
            option_type=STRING,
            required=True
        ),
        create_option(
            name="format",
            description="Format",
            option_type=STRING,
            required=True,
            choices=TRANSFORMATION_OPTIONS
        ),
    ]
)
async def format(ctx: SlashContext, text: str, format: str):
    '''Format text in a variety of ways! (This only appears for you.)'''
    await ctx.send(transform(text, format), hidden=True)
