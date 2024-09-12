import logging
import nextcord
from nextcord.ext import commands
import globals

# Setup logger
logger = logging.getLogger(__name__)

STARTER_ROLE = 'Friends'


class Greetings(commands.Cog):

    serverIdList = globals.config.servers.server_list

    def __init__(self, client):
        self.client = client
        logger.info("Greetings cog initialized.")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        logger.debug(
            f"on_member_update triggered for member: {before.name}#{before.discriminator}")

        if before.bot or after.bot:
            logger.debug(
                f"Skipping bot member: {before.name}#{before.discriminator}")
            return

        roles = before.guild.roles
        role_index = -1

        for i, role in enumerate(roles):
            if role.name == STARTER_ROLE:
                role_index = i
                logger.debug(
                    f"Starter role '{STARTER_ROLE}' found at index {i}.")
                break

        if role_index == -1:
            logger.warning(
                f"Starter role '{STARTER_ROLE}' not found in the guild roles.")
            return

        member = self.client.get_guild(before.guild.id).get_member(before.id)

        if before.pending and not after.pending:
            logger.info(
                f"Member '{before.name}#{before.discriminator}' is no longer pending. Adding role '{STARTER_ROLE}'.")
            try:
                await member.add_roles(roles[role_index])
                logger.info(
                    f"Successfully added role '{STARTER_ROLE}' to member '{before.name}#{before.discriminator}'.")
            except Exception as e:
                logger.error(
                    f"Failed to add role '{STARTER_ROLE}' to member '{before.name}#{before.discriminator}'", exc_info=e)
        else:
            logger.debug(
                f"No role change needed for member '{before.name}#{before.discriminator}'.")


def setup(client):
    logger.info("Setting up Greetings cog.")
    client.add_cog(Greetings(client))
    logger.info("Greetings cog loaded successfully.")
