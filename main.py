import traceback

import nextcord
from nextcord.ext import commands
import os
import sys
import apikeys
import sheets.subsheets as sub

import sheets.sheets as sheets
import sheets.participationsheet as ps
import json

serverIdList = apikeys.serverIdList()
BOTTOKEN = apikeys.discordApiKey()
intents = nextcord.Intents.all()  # VITAL that this is .all()
client = commands.Bot(intents=intents)
GSHEETS = dict()


def load_extensions():
    print("Loading Cogs.")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            extension = "cogs." + filename[:-3]
            client.load_extension(extension)
            print("Loaded: ", extension)


# Initializes the participation sheets from keys/sheets.json
def sheets_main():
    sheets.start()
    sub.sheets_main(ps, sheets)


def get_sub_sheet(n: str):
    return GSHEETS[n]


if __name__ == '__main__':
    print("Starting Nauticock Bot...")
    if not os.path.exists('keys/discord.txt') or not os.path.exists('keys/serverids.txt'):
        print('''Please initialize the keys/ directory with discord.txt and serverids.txt.
        Put your Discord API key into discord.txt.
        Put the ID of the servers you want to allow the bot to message in.
        Therefore, you should have these files:
            keys/discord.txt
            keys/serverids.txt''')
        sys.exit(1)
    else:
        try:
            sheets_main()
            load_extensions()
            print("Running Nauticock Bot...")
            client.run(BOTTOKEN)
        except:
            traceback.print_exc()
        print("Exiting.")
