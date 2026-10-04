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
    },
    MODE_SHOTS: {
        "all_radio":      "All Shots",
        "selected_radio": "Selected Shots",
        "single_radio":   "Single Shot",
        "type_filter":    "Sequence",
        "search":         "⌕  Search shots...",
        "table_headers":  ["", "SHOT", "SEQUENCE", "STATUS", "ISSUES"],
    },
}