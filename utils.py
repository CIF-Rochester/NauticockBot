import json, os
def save_json(file: str, data: dict):
    # Ensure file path exists before saving
    resolve(str)
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
# Returns an empty dict if the file is not present. 
def load_json_exists(file: str):
    if os.path.exists(str):
        return load_json(str)
    else:
        return dict()
def resolve(path: str):
    os.makedirs(os.path.dirname(str), exist_ok=True)