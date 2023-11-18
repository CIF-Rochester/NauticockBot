import json, os, sys
from config import load_config, Config

class Utils:

    SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
    CFG_PATH = os.path.join(SCRIPT_PATH, "config.cfg")

    def save_json(file: str, data: dict):
        "removes old file and then replaces it with fresh data @tpowell11"
        os.remove(file)  # delete outdated data
        dumpData = json.dumps(data)
        with open(file, 'w') as f:  # open file
            f.write(dumpData)  # write the new json
            f.close()

    def load_json(jsonfilename : str):
        with open(jsonfilename, 'r') as file:
            data = file.read()
            output = json.loads(data)
            file.close()
        return output
    
    def get_discord_key():
        try:
            config: Config = load_config(Utils.DEFAULT_CFG_PATH)
            discord_key = config.bot.key
            return discord_key
        except Exception as e:
            print(e)
            sys.exit(1)

    def get_servers():
        try:
            config: Config = load_config(Utils.DEFAULT_CFG_PATH)
            servers = config.servers.servers_list
            return servers
        except Exception as e:
            print(e)
            sys.exit(1)

    def get_json_path():
        try:
            config: Config = load_config(Utils.DEFAULT_CFG_PATH)
            path = config.json.path
            return path
        except Exception as e:
            print(e)
            sys.exit(1)

    BOTTOKEN = get_discord_key()
    SERVER_LIST = get_servers()
    JSON_PATH = get_json_path()
    