import os
from typing import Optional

import nextcord
from nextcord import Interaction
from nextcord import SlashOption
from nextcord.ext import commands
from nextcord.utils import get

import apikeys
import utils
import sheets.subsheets as subsheets


class Admin(commands.Cog):
    serverIdList = apikeys.serverIdList()

    def __init__(self, client):
        self.json_filename = 'cogs/reaction_roles.json'

        if not os.path.exists(self.json_filename):
            f = open(self.json_filename, 'a')
            f.write("{}")
            f.close()

        self.client = client

        self.json_filename = 'cogs/reaction_roles.json'
        self.reactionRolesJson = utils.load_json(self.json_filename)

        self.ROLE_FOR_ADMIN_PERMS = "Board"
        self.NO_PERMS_MSG = "You do not have permission to use this command!"

    @nextcord.slash_command(name="botsay", description="Make the bot send a message", guild_ids=serverIdList)
    async def botsay(self, interaction: Interaction, msg: str, channel_id: str):
        channel_str = channel_id
        if self.has_permission(interaction):
            channel = self.client.get_channel(int(channel_id))
            await channel.send(msg)
            await interaction.response.send_message(
                "Message \"" + msg + "\" has been sent to channel " + channel_str + ".")

    @nextcord.slash_command(name="add-reaction-role", description="Add a new reaction role monitor",
                            guild_ids=serverIdList)
    async def reactionrole(self, interaction: Interaction, msg_id: str, emoji: str, role_id: str):
        if self.has_permission(interaction):
            await interaction.response.send_message(
                "Reaction role monitor added for:\n" +
                "message_id : " + msg_id + "\n" +
                "emoji : " + emoji + "\n" +
                "role_id : " + role_id
            )

            if msg_id not in self.reactionRolesJson:
                self.reactionRolesJson[msg_id] = {emoji: {}}

            self.reactionRolesJson[msg_id][emoji] = {"role": role_id}
            utils.save_json(self.json_filename, self.reactionRolesJson)
            self.reactionRolesJson = utils.load_json(self.json_filename)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        if str(payload.message_id) not in self.reactionRolesJson:
            return

        guild = self.client.get_guild(payload.guild_id)
        if guild is None:
            return

        # allow for utf emojis and custom emojis
        emoji_name = payload.emoji.name
        if ":" in str(payload.emoji):
            emoji_name = str(payload.emoji)

        try:
            role_id = self.reactionRolesJson[str(payload.message_id)][str(emoji_name)]["role"]

            if role_id.isdigit():
                role_id = int(role_id)
            else:
                print("Error: Role at message: " + str(
                    payload.message_id) + " with emoji: " + emoji_name + " is incorrect.")
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

        # allow for utf emojis and custom emojis
        emoji_name = payload.emoji.name
        if ":" in str(payload.emoji):
            emoji_name = str(payload.emoji)

        try:
            role_id = self.reactionRolesJson[str(payload.message_id)][str(emoji_name)]["role"]

            if role_id.isdigit():
                role_id = int(role_id)
            else:
                print("Error: Role at message: " + str(
                    payload.message_id) + " with emoji: " + emoji_name + " is incorrect.")
                return
        except KeyError:
            return

        role = guild.get_role(role_id)

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        await member.remove_roles(role)

    async def has_permission(self, interaction: Interaction):
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)
        if not role:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            return False
        else:
            return True


def setup(client):
    client.add_cog(Admin(client))
