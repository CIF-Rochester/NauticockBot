import json
import paramiko
import logging
import globals

# Setup logger
logger = logging.getLogger(__name__)


def save_json(file: str, data: dict):
    """
    Saves data to a JSON file, overwriting existing content.
    """
    try:
        with open(file, "w") as f:
            json.dump(data, f)
        logger.info(f"Successfully saved JSON to {file}")
    except Exception as e:
        logger.error(f"Failed to save JSON to {file}", exc_info=e)


def load_json(jsonfilename: str):
    """
    Loads data from a JSON file.
    """
    try:
        with open(jsonfilename, "r") as file:
            logger.info(f"Successfully loaded JSON from {jsonfilename}")
            return json.load(file)
    except Exception as e:
        logger.error(f"Failed to load JSON from {jsonfilename}", exc_info=e)


def ssh(timestamp: str) -> str:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logger.info(f"Attempting SSH connection to {globals.config.gatekeeper.ip}")
        client.connect(
            globals.config.gatekeeper.ip,
            username=globals.config.gatekeeper.username,
            password=globals.config.gatekeeper.password,
        )

        command = globals.config.gatekeeper.command + f" --day {timestamp}"
        logger.info(f"Executing command on {globals.config.gatekeeper.ip}: {command}")
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")

        if output:
            logger.info(f"Command output: \n{output}")
            return f"```\n{output}\n```"
        if error:
            logger.error(f"Command error: \n{error}")
            return "Error: " + error
        return f"No data for day: {timestamp}"
    except Exception as e:
        logger.error("SSH connection or command execution failed", exc_info=e)
        return "Connection or execution failed."
    finally:
        client.close()
