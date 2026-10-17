import os
from pathlib import Path

DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
projects_folder = os.path.join(DATA_DIR, r"data\projects")
PROJECTS_DIR = DATA_DIR / "src" / "data" / "projects"

# project_folder_names = os.listdir(projects_folder)
# print(project_folder_names)

def get_project_folder(project_name) -> Path:
    """Root folder of one project; pass it as search_dir so lookups stay inside that project."""
    return PROJECTS_DIR / project_name

def get_shot_files(project_name):
    print("I ran")
    """Gets All the Shot JSon files for one project , empty if no shots present """
    shots_directory = get_project_folder(project_name) / "shots"
    if not shots_directory.is_dir():
        return []
    print(shots_directory)
    # return shots_directory


get_shot_files("demo_project")