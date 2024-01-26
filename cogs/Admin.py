import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext import application_checks
from nextcord.utils import get
from datetime import datetime, timedelta
import os
import utils, globals

class Admin(commands.Cog):

    serverIdList = globals.config.servers.server_list
    def __init__(self, client):
        self.json_filename = 'data/reaction_roles.json'

        if os.path.exists(self.json_filename) == False:
            f = open(self.json_filename, 'a')
            f.write("{}")
            f.close()

        self.client = client

        self.reactionRolesJson = utils.load_json(self.json_filename)

        self.ROLE_FOR_ADMIN_PERMS = "Board"
        self.NO_PERMS_MSG = "You do not have permission to use this command!"
    
    @nextcord.slash_command(name = "botsay", description = "Make the bot send a message", guild_ids=serverIdList)
    async def botsay(self, interaction: Interaction, msg:str, channel_id:str):
        channel_str = channel_id
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)
        if role in interaction.user.roles:
            channel = self.client.get_channel(int(channel_id))
            await channel.send(msg)
            await interaction.response.send_message("Message \"" + msg + "\" has been sent to channel " + channel_str + ".")
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
    
    @nextcord.slash_command(name = "add-reaction-role", description = "Add a new reaction role monitor", guild_ids=serverIdList)
    async def reactionrole(self, interaction: Interaction, msg_id:str, emoji:str, role_id:str):
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)
        if role in interaction.user.roles:
            await interaction.response.send_message(
                "Reaction role monitor added for:\n" +
                "message_id : "  + msg_id + "\n" +
                "emoji : " + emoji + "\n" +
                "role_id : " + role_id
                )

            if msg_id not in self.reactionRolesJson:
                self.reactionRolesJson[msg_id] = {emoji : {}}

            self.reactionRolesJson[msg_id][emoji] = {"role" : role_id}
            utils.save_json(self.json_filename, self.reactionRolesJson)
            self.reactionRolesJson = utils.load_json(self.json_filename)
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        if str(payload.message_id) not in self.reactionRolesJson:
            return

        guild = self.client.get_guild(payload.guild_id)
        if guild is None:
            return

        #allow for utf emojis and custom emojis
        emoji_name = payload.emoji.name
        if ":" in str(payload.emoji):
            emoji_name = str(payload.emoji)
        
        try:
            role_id = self.reactionRolesJson[str(payload.message_id)][str(emoji_name)]["role"]

            if role_id.isdigit():
                role_id = int(role_id)
            else:
                print("Error: Role at message: " + str(payload.message_id) + " with emoji: " + emoji_name + " is incorrect.")
                return
        except KeyError:
            print("error KeyError")
            return
        
        role = guild.get_role(role_id)


        await payload.member.add_roles(role)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent):
        if str(payload.message_id) not in self.reactionRolesJson:
            return

        guild = self.client.get_guild(payload.guild_id)
        if guild is None:
            return
        
        #allow for utf emojis and custom emojis
        emoji_name = payload.emoji.name
        if ":" in str(payload.emoji):
            emoji_name = str(payload.emoji)
        
        try:
            role_id = self.reactionRolesJson[str(payload.message_id)][str(emoji_name)]["role"]

            if role_id.isdigit():
                role_id = int(role_id)
            else:
                print("Error: Role at message: " + str(payload.message_id) + " with emoji: " + emoji_name + " is incorrect.")
                return
        except KeyError:
            return
        
        role = guild.get_role(role_id)

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        await member.remove_roles(role)

    @nextcord.slash_command(name="gatekeeper-log", description="Get gatekeeper logs for the current day.", guild_ids=serverIdList)
    async def gatekeeper_log(self, interaction: Interaction, yesterday: bool = False, day: str = None):
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)
        if role in interaction.user.roles:
            await interaction.response.defer()
            if day:
                try:
                    date = datetime.strptime(day, "%Y-%m-%d")
                except ValueError:
                    await interaction.followup.send("Invalid date format. Please use YYYY-MM-DD.")
                    return
            elif yesterday:
                date = datetime.now() - timedelta(days=1)
            else:
                date = datetime.now()

            timestamp = date.strftime("%Y-%m-%d")

            output = utils.ssh(timestamp)

            await interaction.followup.send(output)
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)

def setup(client):
    client.add_cog(Admin(client))
