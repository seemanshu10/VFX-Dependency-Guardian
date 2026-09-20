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
            return Path(dirpath) / json_extension

    raise FileNotFoundError(f"Error: '{json_extension}' not found under '{project_file_dir}'")

def get_latest_version(asset_data, component):
    
    component_data = asset_data["components"].get(component)
    if component_data is None:
        return None, None

    versions = component_data["versions"]
    latest = max(versions, key=lambda v: int(v.lstrip("v")))
    # print(latest)
    return latest, versions[latest]["status"]

def compare_shot_to_packages(packages_data) -> dict:
    report = {}
    for asset_name, shot_components in packages_data.items():
        asset_data = load_json(json_file_find_path(asset_name))
        report[asset_name] = {}

        for component, shot_version in shot_components.items():
            latest_version, latest_status = get_latest_version(asset_data, component)
            report[asset_name][component] = {
                "shot_version": shot_version,
                "latest_version": latest_version,
                "latest_status": latest_status,
                "match": shot_version == latest_version,
            }

    return report

def shot_type_version(char_shot, asset_name, asset_type):
    versions = char_shot["packages"][asset_name][asset_type]
    # print(versions)

def shot_package_data_extract(data_extracted):
    packages = data_extracted["packages"]
    # print(packages)
    return packages

def asset_dependency_data(data_extracted):

    asset_dependency = data_extracted["components"]
    return asset_dependency

def get_asset_latest_map(asset_data) -> dict:
    components = asset_dependency_data(asset_data)
    return {component: get_latest_version(asset_data, component)[0] for component in components}

def compare_asset_to_registry(registry_data) -> dict:
    report = {}
    for asset_name, asset_data in registry_data["assets"].items():
        latest_map = get_asset_latest_map(asset_data)
        report[asset_name] = {}

        for component, latest_version in latest_map.items():
            version_data = asset_data["components"][component]["versions"][latest_version]
            dependencies = {}

            for dep_component, built_on in version_data.get("dependencies", {}).items():
                dep_latest = latest_map.get(dep_component)
                dependencies[dep_component] = {
                    "built_on": built_on,
                    "latest_available": dep_latest,
                    "match": built_on == dep_latest,
                }

            report[asset_name][component] = {
                "version": latest_version,
                "dependencies": dependencies,
            }

    return report

def shot_validation(shot_name) -> dict:
    shot_data = load_json(json_file_find_path(shot_name))
    shot_package_data = shot_package_data_extract(shot_data)
    return compare_shot_to_packages(shot_package_data)

def asset_validation() -> dict:
    registry_data = load_json(json_file_find_path("registry"))
    return compare_asset_to_registry(registry_data)

def print_shot_report(shot_name, report) -> None:
    print(f"\nSHOT {shot_name}")

    for asset_name, components in report.items():
        print(f"\n  {asset_name}")

        for component, result in components.items():
            if result["latest_version"] is None:
                outcome = "MISSING IN PACKAGE"
            elif result["match"]:
                outcome = "OK"
            else:
                outcome = "OUTDATED"

            print(f"    {component}: shot={result['shot_version']} "
                  f"latest={result['latest_version']} ({result['latest_status']}) -> {outcome}")

def print_asset_report(report) -> None:
    print("\nASSET DEPENDENCIES")

    for asset_name, components in report.items():
        stale = [
            edge
            for result in components.values()
            for edge in result["dependencies"].values()
            if not edge["match"]
        ]

        print(f"\n  {asset_name}: {'OUT OF DATE' if stale else 'UP TO DATE'}")

        for component, result in components.items():
            if not result["dependencies"]:
                print(f"    {component} {result['version']}: root, no dependencies")
                continue

            for dep_component, edge in result["dependencies"].items():
                if edge["latest_available"] is None:
                    outcome = "MISSING IN REGISTRY"
                elif edge["match"]:
                    outcome = "OK"
                else:
                    outcome = "OUTDATED"

                print(f"    {component} {result['version']}: built on {dep_component} "
                      f"{edge['built_on']}, latest is {edge['latest_available']} -> {outcome}")

if __name__ == "__main__":
    data_shot = "SQ010_SH010"

    print_shot_report(data_shot, shot_validation(data_shot))
    print_asset_report(asset_validation())