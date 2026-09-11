import os
import json
from pathlib import Path

project_file_dir = Path(os.path.dirname(os.path.abspath(__file__)))


def load_json(path: Path) -> dict:
    """Load and parse a single JSON file. Raises on missing file or bad JSON,
    with a clear message identifying which file failed."""
    try:
        with open(path, 'r') as file:
            return json.load(file)

    except FileNotFoundError:
        raise FileNotFoundError(f"Error: '{path}' doesn't exist") from None

    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Json decode error in '{path}': {e.msg}", e.doc, e.pos) from None


def json_file_find_path(json_file_type) -> Path:
    json_extension = "{0}.json".format(json_file_type)
    for dirpath, dirnames, filenames in os.walk(project_file_dir):
        if json_extension in filenames:
            data_file_path = os.path.join(dirpath, json_extension)

    return data_file_path

def character_package_version(char_data, type) -> None:
    versions = char_data["components"][type]["versions"]
    last_version_status = list(versions.values())[-1]
    last_version_version = list(versions.keys())[-1]
    print(last_version_version, end= " ")
    print(last_version_status["status"])


def shot_type_version(char_shot, asset_name, asset_type):
    versions = char_shot["packages"][asset_name][asset_type]
    print(versions)

def packages_data_extract(asset_type = "All"):
    
    data = load_json()
    pass

if __name__ == "__main__":
    # data_asset = project_file_dir / "data" / "packages" / "character_A" / "character_A.json"
    data_asset = "character_A"
    data_shot = "SQ010_SH010"

    # char_data = json_data_loads("character_A")
    # char_shot = load_json(data_shot)

    # character_package_version(char_data, "rig")
    # shot_type_version(char_shot, "character_A", "rig")
    json_file_path_for_asset= json_file_find_path(data_shot)
    print(json_file_path_for_asset)
    data_extracted = load_json(json_file_path_for_asset)
    print(data_extracted)
