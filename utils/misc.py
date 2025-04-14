import os
from shutil import rmtree

def get_project_root(levels_up: int = 2) -> str:
    """
    Returns the absolute path to the project root directory.
    `levels_up` defines how many levels to go up from the current file.
    By default, it goes up 2 levels (e.g., from src/main.py to project root).
    """
    current_path = os.path.abspath(__file__)
    for _ in range(levels_up):
        current_path = os.path.dirname(current_path)
    return current_path

def remove_directory(dirPath):
    try:
        rmtree(dirPath, ignore_errors=True)
    except:
        return None
