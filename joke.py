from dataclasses import dataclass
from typing import Optional


def contains(string, fragments):
    return any(f in string for f in fragments.split())


def joke_gif(string: str) -> str:
    msg = string.lower().strip()
    if contains(msg, "🍕 pizza spider-man spiderman spider"):
        return "https://tenor.com/view/spider-man-pizza-time-pizza-day-pizza-dinner-gif-16271126"
    if contains(msg, "hammer"):
        return "https://tenor.com/view/mc-hammer-you-cant-touch-this-dancing-90s-gif-5758313"


def joke_emoji(string: str) -> str:
    msg = string.lower().strip()
    if contains(msg, "hey hi howdy hello hola"):
        return "👋"
    elif "cake" in msg:
        return "🍰"
    elif "how are you" in msg or "how's it going" in msg or "how are things" in msg:
        return "☺️"
    elif contains(msg, "uprising overlord singularity beep boop bot"):
        return "🤖"
