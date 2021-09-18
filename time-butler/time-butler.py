from enum import Enum

from discord import Message
from discord.channel import DMChannel
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from context import bot

# Actual modules
import joke
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
    else:
        GIF = joke.joke_gif(message.content)
        if GIF:
            await message.channel.send(GIF)
            return
        await message.add_reaction(joke.joke_emoji(message.content) or "❓")


@bot.event
async def on_ready():
    print(f'Signed in as {bot.user}')

with open('oauth-token.txt') as f:
    TOKEN = f.read().strip()

bot.run(TOKEN)
