import json
import platform
from pathlib import Path, PureWindowsPath


def __get_path(file_path):
    system = platform.system()
    filename = Path(file_path)
    if system is 'windows':
        filename = PureWindowsPath(filename)
    return Path(filename)


def from_file(file_path:str) -> dict:
    correct_path = __get_path(file_path)
    with open(correct_path, "r") as file:
        return json.load(file)


def to_file(file_path:str, data:dict):
    correct_path = __get_path(file_path)

    with open(correct_path, 'w') as file:
        json.dump(data, file, indent=2)
