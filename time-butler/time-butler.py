from enum import Enum

from discord import Message
from discord.channel import DMChannel
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from context import bot

# Actual modules
import format
import when


@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
        return
    if not isinstance(message.channel, DMChannel):
        return
    response = when.interpret(message.content, "all")
    if response.worked:
        await message.channel.send(response.msg)


@bot.event
async def on_ready():
    print(f'Signed in as {bot.user}')

with open('oauth-token.txt') as f:
    TOKEN = f.read().strip()

bot.run(TOKEN)
