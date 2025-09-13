from nextcord import Intents
from nextcord.ext import commands
import nextcord
import logging
import os
import argparse
from config import load_config, Config
import globals

# Setup logger
log_file = "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def print_cfg(config: Config):
    """
    Prints the configuration in a readable format.
    """
    logger.info("Config:")
    logger.info(
        f"  Gatekeeper: Username: {config.gatekeeper.username}, IP: {config.gatekeeper.ip}"
    )
    server_list_str = ", ".join(str(id) for id in config.servers.server_list)
    logger.info(f"  Servers: Server List: {server_list_str}")


SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_CFG_PATH = os.path.join(SCRIPT_PATH, "config.cfg")

parser = argparse.ArgumentParser(description="CIF Discord Bot.")
parser.add_argument(
    "--config", "-c", help="Path to Nauticock config file.", default=DEFAULT_CFG_PATH
)

args = parser.parse_args()
path_to_cfg = args.config
config: Config = load_config(path_to_cfg)
globals.config = config
print_cfg(config)

serverIdList = config.servers.server_list
BOTTOKEN = config.api.key

logger.info("Starting bot...")


intents = Intents.all()
client = commands.Bot(intents=intents)

initial_extensions = []

print(SCRIPT_PATH)
COG_PATH = os.path.join(SCRIPT_PATH, 'cogs')
for filename in os.listdir(COG_PATH):
    if filename.endswith(".py"):
        initial_extensions.append("cogs." + filename[:-3])

if __name__ == "__main__":
    for extension in initial_extensions:
        logger.info(f"Loading extension: {extension}")
        client.load_extension(extension)

    try:
        client.run(BOTTOKEN)
    except Exception as e:
        logger.error("Error running the bot", exc_info=e)
