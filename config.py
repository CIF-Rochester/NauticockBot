from typing import Union, Set
import os
import configparser
import sys
from dataclasses import dataclass

@dataclass
class API:
    key: str

@dataclass
class Gatekeeper:
    username: str
    password: str
    ip: str

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
    '''
    Load and validate the config file. Exits the program if the config is invalid.
    '''

    try:
        cfg = configparser.ConfigParser()
        cfg.read(config_path)
    except Exception as e:
        print(f"Failed to load config file from {config_path}: {e}", file=sys.stderr)
        exit(1)

    try:
        api = API(key=cfg.get('api', 'key'))

        gatekeeper = Gatekeeper(
            username=cfg.get('gatekeeper', 'username'),
            password=cfg.get('gatekeeper', 'password'),
            ip=cfg.get('gatekeeper', 'ip')
        )

        # Convert server_list to a set of integers
        server_list_str = cfg.get('servers', 'server_list').split(',')
        server_list_int = set()
        for server_id_str in server_list_str:
            try:
                server_id_int = int(server_id_str.strip())
                server_list_int.add(server_id_int)
            except ValueError:
                raise ValueError(f"Invalid server ID: {server_id_str}")

        servers = Servers(server_list=server_list_int)

        config = Config(
            api=api,
            gatekeeper=gatekeeper,
            servers=servers,
        )
    except Exception as e:
        print(f"Error in config file {config_path}: {e}", file=sys.stderr)
        exit(1)

    return config
