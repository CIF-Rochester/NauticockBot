import os
import argparse
from config import load_config, Config
import globals
from nextcord import Intents
from nextcord.ext import commands
import asyncio
import logging


async def notify():
    try:
        logger.info(f"Recieved message {args.text} from print server")
        intents = Intents.all()
        client = commands.Bot(intents=intents)

        async with client:
            channel = client.get_channel(int(config.api.channel))
            if channel:
                await channel.send(args.text)
                logger.info(f"Sent print notification to channel {config.api.channel}")
            else:
                logger.warning(f"Channel ID {config.api.channel} not found for print notification.")
            await client.close()
    except Exception as e:
        logger.error("Error sending print notification")

if __name__ == "__main__":
    log_file = "bot.log"
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)

    SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
    DEFAULT_CFG_PATH = os.path.join(SCRIPT_PATH, "config.cfg")

    parser = argparse.ArgumentParser(description="CIF Discord Bot.")
    parser.add_argument("--config", "-c", help="Path to Nauticock config file.", default=DEFAULT_CFG_PATH)
    parser.add_argument("--text", "-t", help="Message to be sent")

    args = parser.parse_args()
    path_to_cfg = args.config
    config: Config = load_config(path_to_cfg)
    asyncio.run(notify())