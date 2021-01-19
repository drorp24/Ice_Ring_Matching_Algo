import json
from pathlib import Path


def create_dict_from_json(file_path: Path) -> dict:
    with open(file_path, "r") as file:
        return json.load(file)


def create_json_from_dict(file_path: Path, data: dict) -> None:
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def read_json_from_file(file_path: Path) -> str:
    with open(file_path, "r") as file:
        return file.read()
