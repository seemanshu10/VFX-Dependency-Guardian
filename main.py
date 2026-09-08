import os
import json 
from pathlib import Path

project_file_dir = os.path.dirname(os.path.abspath(__file__))
data_asset = os.path.join(project_file_dir, r"data\packages\character_A\character_A.json")

try :
    with open(data_asset, 'r') as file:
        char_data = json.load(file)

except FileNotFoundError:
    print(f"Error :'{data_asset} doesn't exist'")

except json.JSONDecodeError as e:
    print(f"Json decode error: {e} ")

data_shot = os.path.join(project_file_dir, r"data\shots\SQ010_SH010.json")

try :
    with open(data_shot, 'r') as file:
        char_shot = json.load(file)

except FileNotFoundError:
    print(f"Error :'{data_shot} doesn't exist'")

except json.JSONDecodeError as e:
    print(f"Json decode error: {e} ")

def character_package_version(type) -> None:
    versions = char_data["components"][type]["versions"]
    last_version_status = list(versions.values())[-1]
    last_version_version = list(versions.keys())[-1]
    print(last_version_version, end= " ")
    print(last_version_status["status"])

def shot_type_version(asset_name, asset_type):
    char_data = char_shot
    # print(char_data)
    versions = char_data["packages"][asset_name][asset_type]
    print(versions)

if __name__ == "__main__":
    character_package_version("rig")
    shot_type_version("character_A", "rig")
    root = Path(__file__).parent
    for path in root.rglob("character_B.json"):
        print(path)


    


