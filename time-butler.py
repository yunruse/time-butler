from enum import Enum

from discord import Message
from discord.channel import DMChannel
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from context import bot

# Actual modules
import when
import format


def contains(string, fragments):
    return any(f in string for f in fragments.split())


@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
        return
    if not isinstance(message.channel, DMChannel):
        return
    worked, response = when.interpret(message.content, "all")
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
