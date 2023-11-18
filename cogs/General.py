import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext import application_checks
from nextcord.utils import get
from utils import Utils

class General(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @nextcord.slash_command(name = "wiki", description = "Link to the CIF Wiki", guild_ids=Utils.SERVER_LIST)
    async def wiki(self, interaction: Interaction):
        await interaction.response.send_message('https://github.com/CIF-Rochester/wiki/wiki')
    
    @nextcord.slash_command(name = "website", description = "Link to the CIF Website", guild_ids=Utils.SERVER_LIST)
    async def website(self, interaction: Interaction):
        await interaction.response.send_message('https://cif.rochester.edu/')
    
    @nextcord.slash_command(name = "join-cif", description = "Link to the CIF Application", guild_ids=Utils.SERVER_LIST)
    async def join_cif(self, interaction: Interaction):
        await interaction.response.send_message('https://cif.rochester.edu/join-cif/')
    
    @nextcord.slash_command(name = "calendar", description = "Link to the CIF Calendar", guild_ids=Utils.SERVER_LIST)
    async def calendar(self, interaction: Interaction):
        await interaction.response.send_message('https://cif.rochester.edu/events-calendar/')
    
    @nextcord.slash_command(name = "lab", description = "Link to the CIF Lab Access Form", guild_ids=Utils.SERVER_LIST)
    async def lab(self, interaction: Interaction):
        await interaction.response.send_message('https://cif.rochester.edu/join-cif/')
    
    @nextcord.slash_command(name = "github", description = "Link to the CIF Github", guild_ids=Utils.SERVER_LIST)
    async def github(self, interaction: Interaction):
        await interaction.response.send_message('https://github.com/CIF-Rochester')

    @nextcord.slash_command(name = "source-code", description = "Link to The Nauticock Bot Source Code", guild_ids=Utils.SERVER_LIST)
    async def source_code(self, interaction: Interaction):
        await interaction.response.send_message('https://github.com/CIF-Rochester/NauticockBot')
    
    @nextcord.slash_command(name = "help", description = "Help for using the bot", guild_ids=Utils.SERVER_LIST)
    async def help(self, interaction: Interaction):
        help_message = '''Thanks for using **The Nauticock** bot. 
The bot was originally written in 2020, but as of 2023 has been completely re-written from the ground up to work with the new discord bot API and using nextcord rather than discord.py. Most of its uses are for behind the scenes work, but has some public commands as well.

Some commands that may be useful are:
/wiki
/website
/join-cif
/source-code

And there are many more! Just type "/" and you can see the rest of them.
'''
        await interaction.response.send_message(help_message)

def setup(client):
    client.add_cog(General(client))
