"""Validation logic, kept separate from the UI.

Two tiers, each with its own idea of "latest":
- Shots are checked against the asset package JSONs (projects/<project>/assets).
  Latest = highest version number, whatever its status. The registry is not read.
- Assets are checked against registry.json: is each component built on the
  latest version of its upstream components?
"""
from pathlib import Path

from src.data_loader import load_json, json_file_find_path, get_project_folder

# per-component outcomes
RESULT_OK       = "OK"
RESULT_OUTDATED = "OUTDATED"
RESULT_MISSING  = "MISSING"


def get_latest_version(asset_data, component):
    """(latest version, its status) of one component, or (None, None) if the asset doesn't have it."""
    component_data = asset_data["components"].get(component)
    if component_data is None:
        return None, None

    versions = component_data["versions"]
    latest = max(versions, key=lambda v: int(v.lstrip("v")))
    return latest, versions[latest]["status"]


def get_result(found_version, expected_version):
    if expected_version is None:
        return RESULT_MISSING
    if found_version == expected_version:
        return RESULT_OK
    return RESULT_OUTDATED


# ------------------------------------------------------------------------
#  Shot validation
# ------------------------------------------------------------------------

def get_asset_package_file(project_name, asset_name) -> Path:
    return get_project_folder(project_name) / "assets" / asset_name / f"{asset_name}.json"


def compare_shot_to_packages(project_name, packages_data) -> dict:
    """{asset: {component: result}} for every component the shot uses."""
    report = {}
    for asset_name, shot_components in packages_data.items():
        package_file = get_asset_package_file(project_name, asset_name)
        # a shot can reference an asset that was never published: every component is missing
        asset_data = load_json(package_file) if package_file.is_file() else {"components": {}}
        report[asset_name] = {}

        for component, shot_version in shot_components.items():
            latest_version, latest_status = get_latest_version(asset_data, component)
            report[asset_name][component] = {
                "shot_version": shot_version,
                "latest_version": latest_version,
                "latest_status": latest_status,
                "match": shot_version == latest_version,
                "result": get_result(shot_version, latest_version),
            }

    return report


def shot_validation(project_name, shot_file) -> dict:
    shot_data = load_json(Path(shot_file))
    return compare_shot_to_packages(project_name, shot_data["packages"])


# ------------------------------------------------------------------------
#  Asset validation
# ------------------------------------------------------------------------

def get_asset_latest_map(asset_data) -> dict:
    """{component: latest version} for one asset."""
    return {component: get_latest_version(asset_data, component)[0]
            for component in asset_data["components"]}


def compare_asset_components(asset_data) -> dict:
    """{component: {version, dependencies}} where each dependency says if it's built on the latest upstream."""
    latest_map = get_asset_latest_map(asset_data)
    report = {}

    for component, latest_version in latest_map.items():
        version_data = asset_data["components"][component]["versions"][latest_version]
        dependencies = {}

        for dep_component, built_on in version_data.get("dependencies", {}).items():
            dep_latest = latest_map.get(dep_component)
            dependencies[dep_component] = {
                "built_on": built_on,
                "latest_available": dep_latest,
                "match": built_on == dep_latest,
                "result": get_result(built_on, dep_latest),
            }

        report[component] = {
            "version": latest_version,
            "dependencies": dependencies,
        }

    return report


def load_registry(project_name) -> dict:
    return load_json(json_file_find_path("registry", get_project_folder(project_name)))


def asset_validation(project_name, asset_name=None) -> dict:
    """{asset: component report} for every asset in the registry, or just asset_name."""
    registry_assets = load_registry(project_name)["assets"]
    if asset_name is not None:
        registry_assets = {asset_name: registry_assets[asset_name]}

    return {name: compare_asset_components(asset_data)
            for name, asset_data in registry_assets.items()}


# ------------------------------------------------------------------------
#  Summaries
# ------------------------------------------------------------------------

def shot_issue_count(shot_report) -> int:
    return sum(1
               for components in shot_report.values()
               for result in components.values()
               if result["result"] != RESULT_OK)


def asset_issue_count(asset_report) -> int:
    """Issues for ONE asset's component report."""
    return sum(1
               for result in asset_report.values()
               for edge in result["dependencies"].values()
               if edge["result"] != RESULT_OK)


# ------------------------------------------------------------------------
#  Console output, for running this file directly
# ------------------------------------------------------------------------

def print_shot_report(shot_name, report) -> None:
    print(f"\nSHOT {shot_name}")

    for asset_name, components in report.items():
        print(f"\n  {asset_name}")

        for component, result in components.items():
            print(f"    {component}: shot={result['shot_version']} "
                  f"latest={result['latest_version']} ({result['latest_status']}) -> {result['result']}")


def print_asset_report(report) -> None:
    print("\nASSET DEPENDENCIES")

    for asset_name, components in report.items():
        stale = asset_issue_count(components)
        print(f"\n  {asset_name}: {'OUT OF DATE' if stale else 'UP TO DATE'}")

        for component, result in components.items():
            if not result["dependencies"]:
                print(f"    {component} {result['version']}: root, no dependencies")
                continue

            for dep_component, edge in result["dependencies"].items():
                print(f"    {component} {result['version']}: built on {dep_component} "
                      f"{edge['built_on']}, latest is {edge['latest_available']} -> {edge['result']}")


if __name__ == "__main__":
    from src.data_loader import get_shot_files

    project = "demo_project"
    for shot in get_shot_files(project):
        print_shot_report(shot.stem, shot_validation(project, shot))
    print_asset_report(asset_validation(project))
