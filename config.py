from typing import Union, Set
import os
import configparser
import sys
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class API:
    key: str


@dataclass
class Gatekeeper:
    username: str
    password: str
    ip: str
    command: str

    def __repr__(self):
        # Custom repr to prevent accidentally printing the password
        return f"Gatekeeper(username={repr(self.username)}, password=*****, ip={repr(self.ip)})"


@dataclass
class Servers:
    server_list: Set[int]


@dataclass
class Config:
    api: API
    gatekeeper: Gatekeeper
    servers: Servers


def load_config(config_path: os.PathLike) -> Config:
    """
    Load and validate the config file. Exits the program if the config is invalid.
    """
    logger.info(f"Loading config from {config_path}")
    try:
        cfg = configparser.ConfigParser()
        cfg.read(config_path)
    except Exception as e:
        logger.error(f"Failed to load config file from {config_path}", exc_info=e)
        exit(1)

    try:
        api = API(key=cfg.get("api", "key"))
        gatekeeper = Gatekeeper(
            username=cfg.get("gatekeeper", "username"),
            password=cfg.get("gatekeeper", "password"),
            ip=cfg.get("gatekeeper", "ip"),
            command=cfg.get("gatekeeper", "command"),
        )

        # Convert server_list to a set of integers
        server_list_str = cfg.get("servers", "server_list").split(",")
        server_list_int = {int(server_id.strip()) for server_id in server_list_str}
        servers = Servers(server_list=server_list_int)

        config = Config(api=api, gatekeeper=gatekeeper, servers=servers)
        logger.info("Config successfully loaded and parsed")
    except Exception as e:
        logger.error(f"Error in config file {config_path}", exc_info=e)
        exit(1)

    return config
