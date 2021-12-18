def has_word(string, fragments):
    return any(f in string for f in fragments.split())


def joke_gif(string: str) -> str:
    msg = string.lower().strip()
    if has_word(msg, "🍕 pizza spider-man spiderman spider raimi"):
        return "https://tenor.com/view/spider-man-pizza-time-pizza-day-pizza-dinner-gif-16271126"
    if has_word(msg, "hammer hammertime"):
        return "https://tenor.com/view/mc-hammer-you-cant-touch-this-dancing-90s-gif-5758313"
