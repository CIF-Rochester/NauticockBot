import json

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
