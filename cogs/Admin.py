import asyncio
import logging

import nextcord
from discord.types.emoji import Emoji
from nextcord import Message
from nextcord.ext import commands
from nextcord.utils import get
from datetime import datetime, timedelta, date
import os

from python_freeipa import ClientMeta

import utils
import globals

# Setup logger
logger = logging.getLogger(__name__)


class Admin(commands.Cog):

    serverIdList = globals.config.servers.server_list

    def __init__(self, client: commands.Bot):
        self.client = client
        self.json_filename = "data/reaction_roles.json"

        if not os.path.exists(self.json_filename):
            logger.info(
                f"Reaction roles file {self.json_filename} does not exist, creating new one."
            )
            with open(self.json_filename, "a") as f:
                f.write("{}")

        self.reactionRolesJson = utils.load_json(self.json_filename)
        logger.info(f"Loaded reaction roles from {self.json_filename}")

        self.ROLE_FOR_ADMIN_PERMS = "Board"
        self.NO_PERMS_MSG = "You do not have permission to use this command!"
        logger.info("Admin cog initialized.")

    @nextcord.slash_command(
        name="botsay", description="Make the bot send a message", guild_ids=serverIdList
    )
    async def botsay(
        self, interaction: nextcord.Interaction, msg: str, channel_id: str
    ):
        logger.info(
            f"Received /botsay command from {interaction.user.name}: msg='{msg}', channel_id='{channel_id}'"
        )
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)

        if role:
            channel = self.client.get_channel(int(channel_id))
            if channel:
                await channel.send(msg)
                await interaction.response.send_message(
                    f'Message "{msg}" has been sent to channel {channel_id}.'
                )
                logger.info(
                    f"Message sent to channel {channel_id} by {interaction.user.name}"
                )
            else:
                await interaction.response.send_message(
                    f"Channel ID {channel_id} not found."
                )
                logger.warning(
                    f"Channel ID {channel_id} not found for /botsay command."
                )
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            logger.warning(
                f"Unauthorized /botsay command attempt by {interaction.user.name}"
            )

    @nextcord.slash_command(
        name="add-reaction-role",
        description="Add a new reaction role monitor",
        guild_ids=serverIdList,
    )
    async def reactionrole(
        self, interaction: nextcord.Interaction, msg_id: str, emoji: str, role_id: str
    ):
        logger.info(
            f"Received /add-reaction-role command: msg_id='{msg_id}', emoji='{emoji}', role_id='{role_id}' from {interaction.user.name}"
        )
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)

        if role:
            await interaction.response.send_message(
                f"Reaction role monitor added for:\nmessage_id: {msg_id}\nemoji: {emoji}\nrole_id: {role_id}"
            )
            logger.info(
                f"Reaction role monitor added for message_id: {msg_id}, emoji: {emoji}, role_id: {role_id}"
            )

            if msg_id not in self.reactionRolesJson:
                self.reactionRolesJson[msg_id] = {emoji: {}}

            self.reactionRolesJson[msg_id][emoji] = {"role": role_id}
            utils.save_json(self.json_filename, self.reactionRolesJson)
            self.reactionRolesJson = utils.load_json(self.json_filename)
            logger.info(f"Reaction roles updated and saved to {self.json_filename}")
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            logger.warning(
                f"Unauthorized /add-reaction-role command attempt by {interaction.user.name}"
            )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        logger.debug(
            f"on_raw_reaction_add triggered for message_id={payload.message_id}, emoji={payload.emoji}"
        )
        if str(payload.message_id) not in self.reactionRolesJson:
            logger.debug(
                f"Message ID {payload.message_id} not found in reaction roles JSON."
            )
            return

        guild = self.client.get_guild(payload.guild_id)
        if not guild:
            logger.warning(f"Guild ID {payload.guild_id} not found.")
            return

        emoji_name = payload.emoji.name
        if ":" in str(payload.emoji):
            emoji_name = str(payload.emoji)

        try:
            role_id = self.reactionRolesJson[str(payload.message_id)][str(emoji_name)][
                "role"
            ]
            role = guild.get_role(int(role_id))

            if role:
                await payload.member.add_roles(role)
                logger.info(
                    f"Added role {role.name} to user {payload.member.name} for emoji {emoji_name} on message {payload.message_id}"
                )
            else:
                logger.error(
                    f"Role ID {role_id} not found in guild for emoji {emoji_name} on message {payload.message_id}"
                )
        except KeyError:
            logger.error(
                f"KeyError: No matching role for message {payload.message_id} and emoji {emoji_name}"
            )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent):
        logger.debug(
            f"on_raw_reaction_remove triggered for message_id={payload.message_id}, emoji={payload.emoji}"
        )
        if str(payload.message_id) not in self.reactionRolesJson:
            logger.debug(
                f"Message ID {payload.message_id} not found in reaction roles JSON."
            )
            return

        guild = self.client.get_guild(payload.guild_id)
        if not guild:
            logger.warning(f"Guild ID {payload.guild_id} not found.")
            return

        emoji_name = payload.emoji.name
        if ":" in str(payload.emoji):
            emoji_name = str(payload.emoji)

        try:
            role_id = self.reactionRolesJson[str(payload.message_id)][str(emoji_name)][
                "role"
            ]
            role = guild.get_role(int(role_id))

            member = guild.get_member(payload.user_id)
            if member and role:
                await member.remove_roles(role)
                logger.info(
                    f"Removed role {role.name} from user {member.name} for emoji {emoji_name} on message {payload.message_id}"
                )
            else:
                logger.error(
                    f"Error: Role or member not found for message {payload.message_id} and emoji {emoji_name}"
                )
        except KeyError:
            logger.error(
                f"KeyError: No matching role for message {payload.message_id} and emoji {emoji_name}"
            )

    @nextcord.slash_command(
        name="gatekeeper-log",
        description="Get gatekeeper logs for the current day.",
        guild_ids=serverIdList,
    )
    async def gatekeeper_log(
        self,
        interaction: nextcord.Interaction,
        yesterday: bool = False,
        day: str = None,
    ):
        logger.info(
            f"Received /gatekeeper-log command from {interaction.user.name}: yesterday={yesterday}, day={day}"
        )
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)

        if role:
            await interaction.response.defer()

            if day:
                try:
                    date = datetime.strptime(day, "%Y-%m-%d")
                except ValueError:
                    await interaction.followup.send(
                        "Invalid date format. Please use YYYY-MM-DD."
                    )
                    logger.warning(
                        f"Invalid date format for /gatekeeper-log command: {day}"
                    )
                    return
            elif yesterday:
                date = datetime.now() - timedelta(days=1)
            else:
                date = datetime.now()

            timestamp = date.strftime("%Y-%m-%d")
            output = utils.ssh_gatekeeper(timestamp)
            await interaction.followup.send(output)
            logger.info(f"Gatekeeper log sent for {timestamp}")
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            logger.warning(
                f"Unauthorized /gatekeeper-log command attempt by {interaction.user.name}"
            )

    @nextcord.slash_command(
        name="printer-log",
        description="Get print server's logs for the current day.",
        guild_ids=serverIdList,
    )
    async def printer_log(
        self,
        interaction: nextcord.Interaction,
        yesterday: bool = False,
        day: str = None,
        all: bool = False
    ):
        logger.info(
            f"Received /printer-log command from {interaction.user.name}: yesterday={yesterday}, day={day}, all={all}"
        )
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)

        if role:
            await interaction.response.defer()
            if day:
                try:
                    date = datetime.strptime(day, "%Y-%m-%d")
                except ValueError:
                    await interaction.followup.send(
                        "Invalid date format. Please use YYYY-MM-DD."
                    )
                    logger.warning(
                        f"Invalid date format for /printer-log command: {day}"
                    )
                    return
            elif yesterday:
                date = datetime.now() - timedelta(days=1)
            else:
                date = datetime.now()

            timestamp = date.strftime("%Y-%m-%d")
            output = utils.ssh_print_server(timestamp, all)
            await interaction.followup.send(output)
            logger.info(f"Print Server log sent for {timestamp}")
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            logger.warning(
                f"Unauthorized /printer-log command attempt by {interaction.user.name}"
            )


    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if "cifai" in message.content.lower():
            logger.info(f"Reacted to {message.author.name}'s message with :cif")
            await message.add_reaction("<:cif:819374166082846730>")
        if "/ask" in message.content:
            prompt = message.content[(message.content.index("/ask") + 4):].strip()
            logger.info(
                f"Received /ask command from {message.author.name}: prompt={prompt}"
            )
            role = get(message.author.roles, name=self.ROLE_FOR_ADMIN_PERMS)

            if role:
                if not prompt:
                    await message.reply("Prompt cannot be empty")
                    return
                update_embeddings = False
                if prompt[:2] == '/u':
                    update_embeddings = True
                update = ''
                if update_embeddings:
                    update += "Updating Embeddings"
                if prompt and prompt != '/u':
                    if update:
                        update += ", "
                    update += "Thinking"
                prompt = prompt.replace('\\', '\\\\').replace('\n', '\\n').replace('\"', '\\"').replace('\'', '\\\'')
                reply_message = await message.reply(update)
                await asyncio.create_task(utils.ssh_vicuna(message.author, prompt, message.author.guild.get_channel(message.channel.id), reply_message, update=update))
            else:
                logger.warning(
                    f"Unauthorized /ask command attempt by {message.author.name}"
                )
        await self.client.process_commands(message)

    @nextcord.slash_command(name="lab-access",description="Gather information from user and create lab account",guild_ids=serverIdList)
    async def lab_access(self, interaction: nextcord.Interaction, account_name: str, member: bool = False):
        logger.info(
            f"Received /lab-access command from {interaction.user.name}: account_name={account_name}"
        )
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)

        if role:
            await interaction.response.defer()
            guild = interaction.guild
            subject = guild.get_member_named(account_name)
            output_channel = guild.get_channel(interaction.channel_id)
            if output_channel is None:
                await interaction.followup.send("Could not get output channel")
                logger.warning("Could not get output channel")
            if not subject is None:
                dm_channel = subject.dm_channel
                if dm_channel is None:
                    dm_channel = await subject.create_dm()
                    logger.info(f"Created DM Channel for {account_name}")
                asyncio.create_task(utils.dm_subject(self.client, dm_channel, subject, output_channel, member=member))
                await interaction.followup.send(f"DM sent to {account_name}")
                logger.info(f"DM sent to {account_name}")
            else:
                await interaction.followup.send(f"No user with account name {account_name} exists in guild {guild}")
                logger.warning(f"No user with account name {account_name} exists in guild {guild}")
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            logger.warning(
                f"Unauthorized /lab-access command attempt by {interaction.user.name}"
            )


    @nextcord.slash_command(name="member",description="Make user a member and give lab access if necessary",guild_ids=serverIdList)
    async def member(self, interaction: nextcord.Interaction, account_name: str):
        logger.info(
            f"Received /member command from {interaction.user.name}: account_name={account_name}"
        )
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)

        if role:
            await interaction.response.defer()
            guild = interaction.guild
            subject = guild.get_member_named(account_name)
            if not subject is None:
                logger.info(f"Found subject {subject}")
                friend_role = nextcord.utils.get(subject.roles, name="Friends")
                logger.info(f"Retrieved role {friend_role}")
                member_role = nextcord.utils.get(subject.roles, name="Members")
                logger.info(f"Retrieved role {member_role}")
                static_member_role = nextcord.utils.get(guild.roles, name="Members")
                logger.info(f"Found following roles: {friend_role}, {member_role}")
                if friend_role:
                    logger.info("Removing Friends role")
                    await subject.remove_roles(friend_role)
                if not member_role:
                    logger.info("Adding Members Role")
                    await subject.add_roles(static_member_role)
                else:
                    logger.info("No roles need to be changed")
                try:
                    logger.info("Attempting to SSH into Citadel")
                    citadel_client = ClientMeta(globals.config.citadel.ip, verify_ssl=globals.config.citadel.verify_ssl)
                    citadel_client.login(globals.config.citadel.username, globals.config.citadel.password)
                except Exception as e:
                    await interaction.followup.send("Unable to connect to citadel")
                    return
                user = citadel_client.user_find(o_street=subject.name)['result']
                if len(user) == 0:
                    output_channel = guild.get_channel(interaction.channel_id)
                    if output_channel is None:
                        await interaction.followup.send("Could not get output channel")
                        logger.warning("Could not get output channel")
                    dm_channel = subject.dm_channel
                    if dm_channel is None:
                        dm_channel = await subject.create_dm()
                        logger.info(f"Created DM Channel for {account_name}")
                    asyncio.create_task(utils.dm_subject(self.client, dm_channel, subject, output_channel, member=True))
                    await interaction.followup.send(f"Roles changed for user {account_name}\nDM sent to {account_name}")
                    logger.info(f"{account_name} made a Member\nDM sent to {account_name}")
                else:
                    if not "cif_full_members" in user[0]['memberof_group']:
                        citadel_client.group_add_member(a_cn="cif_full_members", o_user=user[0]['uid'][0])
                        logger.info(f"User {user[0]['uid'][0]} moved to cif_full_members in citadel")
                    await interaction.followup.send(f"{account_name} made a Member")
                    logger.info(f"{account_name} made a Member")
                citadel_client.logout()
            else:
                await interaction.followup.send(f"No user with account name {account_name} exists in guild {guild}")
                logger.warning(f"No user with account name {account_name} exists in guild {guild}")
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            logger.warning(
                f"Unauthorized /member command attempt by {interaction.user.name}"
            )

    @nextcord.slash_command(name="remove-member", description="Removes Member role in discord and removes lab account from cif_full_members group if possible",
                            guild_ids=serverIdList)
    async def remove_member(self, interaction: nextcord.Interaction, account_name: str):
        logger.info(
            f"Received /remove-member command from {interaction.user.name}: account_name={account_name}"
        )
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)

        if role:
            await interaction.response.defer()
            guild = interaction.guild
            subject = guild.get_member_named(account_name)
            if not subject is None:
                output = utils.remove_member(subject, guild)
                await interaction.followup.send(output)
            else:
                await interaction.followup.send(f"No user with account name {account_name} exists in guild {guild}")
                logger.warning(f"No user with account name {account_name} exists in guild {guild}")
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            logger.warning(
                f"Unauthorized /member command attempt by {interaction.user.name}"
            )

    @nextcord.slash_command(name="update-members", description="Deactivates graduated citadel accounts and updates discord roles based on citadel",
                            guild_ids=serverIdList)
    async def update_members(self, interaction: nextcord.Interaction):
        logger.info(
            f"Received /update-members command from {interaction.user.name}"
        )
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)

        if role:
            await interaction.response.defer()
            current_date = date.today()
            guild = interaction.guild
            output_channel = guild.get_channel(interaction.channel_id)
            output = await utils.update_members(self.client, guild, current_date, output_channel)
            await interaction.followup.send(output)
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            logger.warning(
                f"Unauthorized /update-members command attempt by {interaction.user.name}"
            )

    @nextcord.slash_command(name="emails", description="Retrieves desired emails from citadel", guild_ids=serverIdList)
    async def emails(self, interaction: nextcord.Interaction, friends: bool, members: bool, alumni: bool):
        logger.info(
            f"Received /update-members command from {interaction.user.name}"
        )
        role = get(interaction.user.roles, name=self.ROLE_FOR_ADMIN_PERMS)

        if role:
            await interaction.response.defer()
            output = utils.get_emails(friends, members, alumni)
            await interaction.followup.send(output)
        else:
            await interaction.response.send_message(self.NO_PERMS_MSG)
            logger.warning(
                f"Unauthorized /update-members command attempt by {interaction.user.name}"
            )

def setup(client):
    logger.info("Setting up Admin cog.")
    client.add_cog(Admin(client))
    logger.info("Admin cog loaded successfully.")
