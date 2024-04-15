# The Nauticock Discord Bot

![The Nauticock](https://github.com/CIF-Rochester/NauticockBot/blob/master/TheNauticock.png?raw=true)

Updated for 2024 with new slash commands, using [nextcord](https://github.com/nextcord/nextcord) for the API.

## Prerequisites:
* [Python >= 3.10.12](https://www.python.org/)
* [nextcord](https://pypi.org/project/nextcord/)

## Quick Start
- **(Recommended)** Create a virtual environment with `python3 -m venv .venv` and activate it with `source .venv/bin/activate`
- run `python3 -m pip install -r requirements.txt`
- copy `config.example.cfg` to `config.cfg` and adjust the configuration
- run `python3 main.py`

## Command Line Arguments

```
usage: main.py [-h] [--config CONFIG]

CIF Discord Bot.

options:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to Nauticock config file.
```

## Features Implemented

* New members will automatically be given the "Friends" role.
* Role reaction monitor abilities.
* Simple commands for public use such as /wiki and /website.

## Code Structure

* `main.py` creates a cogs list to use the modules in `cogs/`.
* `utils.py` is for json loading and saving utils.
* `apikeys.py` is for loading api keys and server Ids.
* cog modules explained below.

## Admin.py

* For admin commands, such as `/botsay`.
* Full role monitoring and adding role monitors.
* Only users with the "Board" role can use these commands.

## Greetings.py

* For `on_member_update()` functionality.
* Gives the "Friends" role to new members who pass the rules screening.

## General.py

* For general public use functions such as retrieval of commonly used links.
