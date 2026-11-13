# ── App window ────────────────────────────────────────────────────────────────
APP_TITLE     = "VFX Dependency Gaurdian"
WINDOW_WIDTH  = 1200
WINDOW_HEIGHT = 900



ASSET_TYPE = ["All", "Character", "Prop", "Environment", "FX"]

# ── Mode labels ───────────────────────────────────────────────────────────────
# Text that changes when switching between the Assets and Shots tabs
MODE_ASSETS = "assets"
MODE_SHOTS  = "shots"
MODE_LABELS = {
    MODE_ASSETS: {
        "all_radio":      "All  Assets",
        "selected_radio": "Selected Assets",
        "single_radio":   "Single Asset",
        "type_filter":    "Asset Type",
        "search":         "⌕  Search assets...",
        "table_headers":  ["", "ASSET", "TYPE", "STATUS", "ISSUES"],
        "name_col":       1,
        "type_col":       2,
        # hover text; same keys in both modes
        "tooltips": {
            "all_radio":      "Check every asset in the project.",
            "selected_radio": "Check only the assets you ticked in the table below.",
            "type_filter":    "Show only one kind of asset, e.g. Character or Prop.\nPick 'All' to see everything.",
            "search":         "Type part of an asset name to find it quickly.",
            "table":          "Every asset in the project and whether its parts are up to date.\n"
                              "Click a row to see the details on the right. Click a column title to sort.",
            "headers": [
                "Tick assets here to check only those ones.",
                "Name of the asset.",
                "What kind of asset it is, e.g. Character, Prop, FX.",
                "OK = everything is up to date.\nFAILED = at least one part needs fixing.",
                "How many problems were found. 0 means all good.",
            ],
            "dependency_table": "Each part of the asset (model, rig, texture...) and the version it was built on,\n"
                                "compared with the newest version that exists.",
            "dependency_headers": [
                "The part of the asset being checked.",
                "The version this part was built on.",
                "The newest version available. It should match CURRENT.",
                "Whether CURRENT and EXPECTED match.",
            ],
        },
    },
    MODE_SHOTS: {
        "all_radio":      "All Shots",
        "selected_radio": "Selected Shots",
        "single_radio":   "Single Shot",
        "type_filter":    "Sequence",
        "search":         "⌕  Search shots...",
        "table_headers":  ["", "SEQUENCE", "SHOT", "STATUS", "ISSUES"],
        "name_col":       2,
        "type_col":       1,
        # hover text; same keys in both modes
        "tooltips": {
            "all_radio":      "Check every shot in the project.",
            "selected_radio": "Check only the shots you ticked in the table below.",
            "type_filter":    "Show only the shots from one sequence.\nPick 'All' to see everything.",
            "search":         "Type part of a shot name to find it quickly.",
            "table":          "Every shot in the project and whether the assets it uses are up to date.\n"
                              "Click a row to see the details on the right. Click a column title to sort.",
            "headers": [
                "Tick shots here to check only those ones.",
                "The sequence (group of shots) this shot belongs to.",
                "Name of the shot.",
                "OK = everything is up to date.\nFAILED = at least one asset needs updating.",
                "How many problems were found. 0 means all good.",
            ],
            "dependency_table": "Each asset part this shot uses and its version,\n"
                                "compared with the newest version published for that asset.",
            "dependency_headers": [
                "The asset and the part of it (model, rig, texture...) used in this shot.",
                "The version the shot is using now.",
                "The newest version available. It should match CURRENT.",
                "Whether CURRENT and EXPECTED match.",
            ],
        },
    },
}
# ── Tooltips ──────────────────────────────────────────────────────────────────
# What each status badge means, shown when hovering over it
STATUS_TOOLTIPS = {
    "OK":       "All good: this is using the newest version.",
    "FAILED":   "Something needs fixing. Click the row to see what.",
    "OUTDATED": "A newer version exists. This should be updated to it.",
    "MISSING":  "This part could not be found. It may have been deleted or never published.",
    "INVALID":  "This version does not exist in the published list, so it can't be trusted.",
}

# Hover text for the counters in the Validation Summary bar
SUMMARY_TOOLTIPS = {
    "ok":       "Checks that passed: the newest version is being used.",
    "outdated": "Checks that use an old version when a newer one exists.",
    "missing":  "Checks that point to something that can't be found.",
    "invalid":  "Checks that use a version that was never published.",
}
