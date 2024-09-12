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
    async def on_member_join(self, member: nextcord.Member):
        logger.info(f"New member joined: {member.name}#{member.discriminator}")

        # Find the STARTER_ROLE in the guild roles
        starter_role = nextcord.utils.get(
            member.guild.roles, name=STARTER_ROLE)

        if starter_role:
            try:
                await member.add_roles(starter_role)
                logger.info(
                    f"Assigned '{STARTER_ROLE}' role to {member.name}#{member.discriminator}")
            except Exception as e:
                logger.error(
                    f"Failed to assign role '{STARTER_ROLE}' to {member.name}#{member.discriminator}", exc_info=e)
        else:
            logger.warning(
                f"Role '{STARTER_ROLE}' not found in guild {member.guild.name} (ID: {member.guild.id})")


def setup(client):
    logger.info("Setting up Greetings cog.")
    client.add_cog(Greetings(client))
    logger.info("Greetings cog loaded successfully.")
