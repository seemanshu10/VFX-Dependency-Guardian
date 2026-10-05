"""Load JSON data (registry, packages, shots) from the project's data folder."""
import os
import json
from pathlib import Path

# <repo>/data  (this file lives in <repo>/src)
DATA_DIR = Path(__file__).resolve().parent.parent

def load_json(path: Path) -> dict:
    """Load and parse a single JSON file. Raises on missing file or bad JSON,
    with a clear message identifying which file failed."""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)

    except FileNotFoundError:
        raise FileNotFoundError(f"Error: '{path}' doesn't exist") from None

    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Json decode error in '{path}': {e.msg}", e.doc, e.pos) from None

def json_file_find_path(json_file_type, search_dir: Path = DATA_DIR) -> Path:
    """Find '<json_file_type>.json' anywhere under search_dir (defaults to DATA_DIR)."""
    json_extension = "{0}.json".format(json_file_type)
    for dirpath, dirnames, filenames in os.walk(search_dir):
        if json_extension in filenames:
            return Path(dirpath) / json_extension

    raise FileNotFoundError(f"Error: '{json_extension}' not found under '{search_dir}'")
