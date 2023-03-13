from datetime import datetime
from typing import Optional

import nextcord
from nextcord import Interaction
from nextcord import SlashOption
from nextcord.ext import commands
from nextcord.utils import get

import apikeys
import sheets.subsheets as subsheets


class Participation(commands.Cog):
    serverIdList = apikeys.serverIdList()
    usermap = dict()

    def __init__(self, client):
        self.client = client

        self.ROLE_FOR_ADMIN_PERMS = "Board"
        self.NO_PERMS_MSG = "You do not have permission to use this command!"

    @nextcord.slash_command(name="pnew", description="Gives member(s) a participation point. Attaches the event to your user", guild_ids=serverIdList)
    async def pnew(self, interaction: Interaction, event: str, names: str, date=None):
        if await self.has_permission(interaction):
            if not date:
                today = datetime.today()
                date = str(today.month) + "/" + str(today.day) + "/" + str(today.year)
            event = event + " " + date
            await interaction.send("**Processing**")
            lst = names.split(",")
            for x in range(len(lst)):
                lst[x] = lst[x].removeprefix(" ").removesuffix(" ")
            response = subsheets.get_sub_sheet("Masterlist").give_points_can_create(event, lst)
            await interaction.edit_original_message(content=response.discord_format())
            self.usermap[interaction.user] = event

    @nextcord.slash_command(name="pgrant", description="Gives member(s) a participation point. Must have an event attached to your user.", guild_ids=serverIdList)
    async def pgrant(self, interaction: Interaction, names: str):
        if await self.has_permission(interaction):
            if interaction.user not in self.usermap:
                await interaction.send("**You need to select an event! Use '/pnew'**")
            else:
                await interaction.send("**Processing**")
                lst = names.split(",")
                for x in range(len(lst)):
                    lst[x] = lst[x].removeprefix(" ").removesuffix(" ")
                response = subsheets.get_sub_sheet("Masterlist").give_points_can_create(self.usermap[interaction.user], lst)
                await interaction.edit_original_message(content=response.discord_format())

    async def has_permission(self, interaction: Interaction):
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)
        if not role:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            return False
        else:
            return True


def setup(client):
    client.add_cog(Participation(client))
