import os
import json 


project_file_dir = os.path.dirname(os.path.abspath(__file__))
data = os.path.join(project_file_dir, r"data\packages\character_A\character_A.json")

with open(data, 'r') as file:
    char_data = json.load(file)

# print(char_data)

# print(char_data["asset"])
versions = char_data["components"]["rig"]["versions"]
# print(versions.items())

last_version_data = list(versions.values())[-1]
print(last_version_data["status"])

# for version, info in versions.items():
#     print(version, info["status"])
