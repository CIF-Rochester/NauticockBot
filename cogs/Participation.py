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
    async def pnew(self, interaction: Interaction, event: str, names: str, date=None, misc=False):
        if await self.has_permission(interaction):
            if not date:
                today = datetime.today()
                date = str(today.month) + "/" + str(today.day) + "/" + str(today.year)
            event = event + " " + date
            await interaction.send("**Processing**")
            lst = names.split(",")
            # Remove extraneous spaces.
            for x in range(len(lst)):
                while lst[x].startswith(" "):
                    lst[x] = lst[x].removeprefix(" ")
                while lst[x].endswith(" "):
                    lst[x] = lst[x].removesuffix(" ")
            sht = "Masterlist"
            if misc:
                sht = "Misc"
            response = subsheets.get_sub_sheet(sht).give_points_can_create(event, lst)
            await interaction.edit_original_message(content=response.discord_format())
            if misc:
                event = "M!" + event
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
                event = self.usermap[interaction.user]
                sht = "Masterlist"
                if event.startswith("M!"):
                    event = event.removeprefix("M!")
                    sht = "Misc"
                response = subsheets.get_sub_sheet(sht).give_points_can_create(event, lst)
                await interaction.edit_original_message(content=response.discord_format())

    @nextcord.slash_command(name="pusernew", description="Adds a new member to the participation sheet", guild_ids=serverIdList)
    async def pusernew(self, interaction: Interaction, name: str, codename: str,):
        if await self.has_permission(interaction):
            await interaction.send("Processing Request...")
            if not subsheets.get_sub_sheet("Masterlist").has_name(name):
                if not subsheets.get_sub_sheet("Masterlist").has_codename(codename):
                    for ss in subsheets.get_sheets():
                        ss.new_user(name, codename)
                        # ss.sort()
                    await interaction.edit_original_message(content="Successfully added **" + name + "** as **" + codename + "**")
                else:
                    await interaction.edit_original_message(content="A person already has that codename")
            else:
                await interaction.edit_original_message(content="A person with that name already exists :skull:")

    async def has_permission(self, interaction: Interaction):
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)
        if not role:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            return False
        else:
            return True


def setup(client):
    client.add_cog(Participation(client))
