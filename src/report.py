"""Report building, kept separate from the UI.

Turns validator results into what the app shows and exports:
- summaries:    one entry per asset/shot for the results table
- item reports: dependency rows, info and plain-text report for one asset/shot
- export text:  several item reports joined under a header

Nothing here imports Qt, so a CLI or tests can use it as well.
"""
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.data_loader import load_json, get_shot_files
from src.validator import (compare_shot_to_packages, compare_asset_components, load_registry,
                           shot_issue_count, asset_issue_count, shot_result_counts,
                           asset_result_counts, overall_status, RESULT_OK)

# shown in the EXPECTED column when there is nothing to compare against (component missing)
NO_VERSION = "-"


@dataclass
class ItemSummary:
    """One row of the results table."""
    name: str        # asset name or shot name
    group: str       # asset type or sequence: what the filter combo matches on
    key: str         # asset id or shot file path: pass it back to build_*_report
    issues: int
    counts: Counter  # {result: number of checks that ended in it}

    @property
    def status(self) -> str:
        return overall_status(self.issues)


@dataclass
class ItemReport:
    """Everything the details panel and the export need for one asset or shot."""
    name: str
    status: str
    info: dict   # {label: value} shown above the dependency table
    rows: list   # (component, current, expected, result) per check
    text: str    # plain-text report


# ------------------------------------------------------------------------
#  Summaries (results table)
# ------------------------------------------------------------------------

def asset_summaries(project_name) -> list:
    """ItemSummary for every asset in the project's registry, in registry order."""
    summaries = []
    for asset_id, asset_data in load_registry(project_name)["assets"].items():
        asset_report = compare_asset_components(asset_data)
        summaries.append(ItemSummary(asset_data["name"], asset_data["type"], asset_id,
                                     asset_issue_count(asset_report),
                                     asset_result_counts(asset_report)))
    return summaries


def shot_summaries(project_name) -> list:
    """ItemSummary for every shot file in the project."""
    summaries = []
    for shot_file in get_shot_files(project_name):
        shot_data = load_json(shot_file)
        shot_report = compare_shot_to_packages(project_name, shot_data["packages"])
        summaries.append(ItemSummary(shot_data["name"], shot_data["sequence"], str(shot_file),
                                     shot_issue_count(shot_report),
                                     shot_result_counts(shot_report)))
    return summaries


# ------------------------------------------------------------------------
#  Item reports (details panel + export)
# ------------------------------------------------------------------------

def _report_text(kind, name, project_name, status, problems_title, problems, all_ok_message) -> str:
    text = (
        f"{kind + ':':<10}{name}\n"
        f"project:  {project_name}\n"
        f"status:   {status}\n\n"
    )
    if problems:
        return text + f"{problems_title}:\n\n" + "\n".join(problems)
    return text + all_ok_message


def build_shot_report(project_name, shot_file) -> ItemReport:
    """Shot tier: each package component against the highest version in the asset's package JSON."""
    shot_data = load_json(Path(shot_file))
    shot_report = compare_shot_to_packages(project_name, shot_data["packages"])
    status = overall_status(shot_issue_count(shot_report))

    rows = []
    problems = []
    for asset, components in shot_report.items():
        for component, check in components.items():
            expected = check["latest_version"] or NO_VERSION
            rows.append((f"{asset} / {component}", check["shot_version"], expected, check["result"]))

            if check["result"] != RESULT_OK:
                problems.append(
                    f" - {asset} / {component}:\n"
                    f"     current:  {check['shot_version']}\n"
                    f"     expected: {expected}\n"
                    f"     status:   {check['result']}\n"
                )

    info = {
        "Sequence": shot_data["sequence"],
        "Project": project_name,
        "Build": shot_data["build"],
        "Author": shot_data["author"],
    }
    text = _report_text("shot", shot_data["shot"], project_name, status, "components", problems,
                        "All packages match the latest published versions.")
    return ItemReport(shot_data["shot"], status, info, rows, text)


def build_asset_report(project_name, asset_id) -> ItemReport:
    """Asset tier: each component's latest version, checked against the latest of its upstream."""
    asset_data = load_registry(project_name)["assets"][asset_id]
    asset_report = compare_asset_components(asset_data)
    status = overall_status(asset_issue_count(asset_report))

    # current = the upstream version this component was built on
    rows = []
    problems = []
    for component, result in asset_report.items():
        if not result["dependencies"]:
            # root component (e.g. model): nothing upstream to be out of date with
            rows.append((component, result["version"], result["version"], RESULT_OK))
            continue

        for dep_component, edge in result["dependencies"].items():
            expected = edge["latest_available"] or NO_VERSION
            rows.append((component, edge["built_on"], expected, edge["result"]))

            if edge["result"] != RESULT_OK:
                problems.append(
                    f" - {component} / {dep_component}:\n"
                    f"     built on: {edge['built_on']}\n"
                    f"     latest:   {expected}\n"
                    f"     status:   {edge['result']}\n"
                )

    info = {
        "Type": asset_data["type"],
        "Project": project_name,
        "Path": f"/assets/{asset_data['type']}/{asset_data['name']}",
    }
    text = _report_text("asset", asset_id, project_name, status, "dependencies", problems,
                        "Every component is built on the latest version of its upstream.")
    return ItemReport(asset_id, status, info, rows, text)


# ------------------------------------------------------------------------
#  Export
# ------------------------------------------------------------------------

def build_export_text(project_name, mode_name, scope, reports, generated=None) -> str:
    """Join item reports under one header. mode_name: 'assets'/'shots', scope: 'all'/'selected'."""
    generated = generated or datetime.now()
    header = (
        f"VFX Dependency Guardian - Validation Report\n"
        f"project:   {project_name}\n"
        f"mode:      {mode_name}\n"
        f"scope:     {scope} ({len(reports)} items)\n"
        f"generated: {generated:%Y-%m-%d %H:%M:%S}\n"
    )
    separator = "\n" + "=" * 60 + "\n\n"
    return header + separator + separator.join(report.text for report in reports) + "\n"
