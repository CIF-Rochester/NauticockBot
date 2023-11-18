import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext import application_checks
import os
from utils import Utils

SERVER_LIST = Utils.SERVER_LIST
BOTTOKEN = Utils.BOTTOKEN

intents = nextcord.Intents.all() # VITAL that this is .all()

client = commands.Bot(intents=intents)

initial_extensions = []

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        initial_extensions.append("cogs." + filename[:-3])

if __name__ == '__main__':
    for extension in initial_extensions:
        client.load_extension(extension)

client.run(BOTTOKEN)