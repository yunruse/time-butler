import json

from discord.ext.commands import Bot
from discord_slash import SlashCommand

bot = Bot("/")
slash = SlashCommand(bot, sync_commands=True)
STRING = 3
GUILDS = [885908649342537810]


class Storage(dict):
    def __init__(self):
        data = {}
        try:
            with open("storage.json") as f:
                data = json.load(f)
        except FileNotFoundError:
            pass

        dict.__init__(self, data)

    def save(self):
        with open("storage.json", "w") as f:
            json.dump(self, f, indent=2)

    def __del__(self):
        print("Deleting!")
        self.save()


STORAGE = Storage()
STORAGE.save()
