import logging
import nextcord
from nextcord.ext import commands
from nextcord.utils import get
from datetime import datetime, timedelta
import os
import utils
import globals

# Setup logger
logger = logging.getLogger(__name__)


class Admin(commands.Cog):

    serverIdList = globals.config.servers.server_list

    def __init__(self, client):
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
        name="print-log",
        description="Get print server's logs for the current day.",
        guild_ids=serverIdList,
    )
    async def print_log(
        self,
        interaction: nextcord.Interaction,
        yesterday: bool = False,
        day: str = None,
        all: bool = False
    ):
        logger.info(
            f"Received /print-log command from {interaction.user.name}: yesterday={yesterday}, day={day}, all={all}"
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
                        f"Invalid date format for /print-log command: {day}"
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
                f"Unauthorized /print-log command attempt by {interaction.user.name}"
            )


def setup(client):
    logger.info("Setting up Admin cog.")
    client.add_cog(Admin(client))
    logger.info("Admin cog loaded successfully.")
