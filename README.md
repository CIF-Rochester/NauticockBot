# The Nauticock Discord Bot

![The Nauticock](https://github.com/CIF-Rochester/NauticockBot/blob/master/TheNauticock.png?raw=true)

Updated for 2025 with new slash commands, now using [nextcord](https://github.com/nextcord/nextcord).

## Prerequisites
- [Python >= 3.10.12](https://www.python.org/)
- [nextcord](https://pypi.org/project/nextcord/)

## Quick Start
1. **(Recommended)** Create a virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2. Install dependencies:
    ```bash
    python3 -m pip install -r requirements.txt
    ```
3. Copy `config.example.cfg` to `config.cfg` and adjust it to fit your server and bot settings.
4. Run the bot:
    ```bash
    python3 main.py
    ```

## Command Line Arguments

```
usage: main.py [-h] [--config CONFIG]

CIF Discord Bot.

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to Nauticock config file.
```

## Features

- Automatically assigns the "Friends" role to new members.
- Role reaction monitor functionality.
- Public commands such as `/wiki`, `/website`, and more.
- Admin commands restricted to users with the "Board" role.
- Log integration with both GateKeeper and the print server

## Code Structure

- **`main.py`**: Initializes the bot and loads cogs (modules) from the `cogs/` folder.
- **`utils.py`**: Handles utility functions, like JSON loading and saving.
- **`globals.py`**: Stores global configuration loaded from the config file.
- **`config.py`**: Handles configuration file parsing and validation.

### Cogs

- **`Admin.py`**: Handles admin-specific commands (e.g., `/botsay`, role management).
- **`Greetings.py`**: Automatically assigns the "Friends" role to new members.
- **`General.py`**: Public commands for retrieving important links (e.g., `/wiki`, `/website`).

## Future Plans
- Integration with the attendance Google sheet for better tracking.
- Lab account signups directly through Discord.
