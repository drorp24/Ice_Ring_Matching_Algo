import json
import platform
from pathlib import Path, PureWindowsPath


def __get_path(file_path: Path) -> Path:
    system = platform.system()
    if system is 'windows':
        file_path = PureWindowsPath(file_path)
    return file_path


def from_file(file_path: Path) -> dict:
    correct_path = __get_path(file_path)
    with open(correct_path, "r") as file:
        return json.load(file)


def to_file(file_path: Path, data: dict) -> None:
    correct_path = __get_path(file_path)

    with open(correct_path, 'w') as file:
        json.dump(data, file, indent=2)
