import json
import paramiko
import globals

def save_json(file: str, data: dict):
    """
    Saves data to a JSON file, overwriting existing content.
    """
    with open(file, 'w') as f:
        json.dump(data, f)

def load_json(jsonfilename: str):
    """
    Loads data from a JSON file.
    """
    with open(jsonfilename, 'r') as file:
        return json.load(file)


def ssh(timestamp: str) -> str:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to the remote server
        client.connect(globals.config.gatekeeper.ip,
                       username=globals.config.gatekeeper.username,
                       password=globals.config.gatekeeper.password)

        # Run a command
        command = globals.config.gatekeeper.command + f" --day {timestamp}"
        print(f"Executing command on {globals.config.gatekeeper.ip}:", command)
        stdin, stdout, stderr = client.exec_command(command)

        # Read the output
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        if output:
            return f"```\n{output}\n```"
        if error:
            return "Error: " + error
        return f"No data for day: {timestamp}"
    except Exception as e:
        print("SSH connection or command execution failed:", e)
        return "Connection or execution failed."
    finally:
        client.close()
