import json

from discord.ext.commands import Bot
from discord_slash import SlashCommand

bot = Bot("/")
slash = SlashCommand(bot, sync_commands=True)
STRING = 3
