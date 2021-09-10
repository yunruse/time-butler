import json
from string import ascii_lowercase, ascii_uppercase

from context import slash, STRING, GUILDS

from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from context import slash, STRING, GUILDS

TRANSFORMATIONS = {}
TRANSFORMATION_OPTIONS = []

with open('format.json') as f:
    DATA: dict[str, object] = json.load(f)

for k, v in DATA.items():
    if isinstance(v, str):
        src = ascii_uppercase + ascii_lowercase
        dst = v
    else:
        src, dst = v

    TRANSFORMATIONS[k] = str.maketrans(src, dst)
    TRANSFORMATION_OPTIONS.append(create_choice(
        name=k.translate(TRANSFORMATIONS[k]), value=k))


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
    '''Format text in a variety of ways!'''
    await ctx.send(text.translate(TRANSFORMATIONS.get(format, {})))
