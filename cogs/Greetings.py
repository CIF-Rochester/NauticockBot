import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext import application_checks
from utils import Utils

class Greetings(commands.Cog):

    serverIdList = Utils.SERVER_LIST
            
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # For this function to work, you need to enable intents in the developer portal.
        # https://discord.com/developers/applications
        # Bot > Bot > Presence & Server Members Intents > Toggle On

        roles = before.guild.roles
        role_index = -1
        for i in range(0, len(roles)): # roles is not iterable :/
            role = str(roles[i])
            if role == 'Friends':
                role_index = i
        
        if role_index == -1:
            return

        member = self.client.get_guild(before.guild.id).get_member(before.id)

        if before.bot or after.bot:
            return
        else:
            if before.pending == True and after.pending == False:
                await member.add_roles(roles[role_index])

def setup(client):
    client.add_cog(Greetings(client))
