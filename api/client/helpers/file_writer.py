import os
import json

CURRENT_DIR = os.getcwd()


def write_as_json_file(dictionary: dict, filename: str):
    json_data = json.dumps(dictionary)
    with open(filename, 'w') as file:
        file.write(json_data)
