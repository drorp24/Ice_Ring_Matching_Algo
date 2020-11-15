import os
from pathlib import Path


def create_path_from_current_directory(file_name: Path) -> Path:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, file_name)
