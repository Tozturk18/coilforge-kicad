'''
@ filename: project_settings.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2026
@ license:  MIT License
@ description: This module implements functions for loading and saving CoilForge
    project settings directly inside the KiCad .kicad_pro file. The settings are
    stored under the JSON path:

        plugins -> coilforge

    This keeps the configuration project-scoped instead of global. If the project
    file cannot be found or read, the module falls back to a default CoilConfig.
'''

# --- IMPORTS --- #
import json
import shutil
from pathlib import Path
from typing import Optional

# --- LOCAL IMPORTS --- #
from ..config.config import CoilConfig


# --- CONSTANTS --- #

DEFAULT_CONFIG = CoilConfig(
    hole_radius = 0.0,
    turns       = 10.0,
    track_width = 0.25,
    spacing     = 0.20,
    center_x    = 0.0,
    center_y    = 0.0,
    angle       = 0.0,
    layers      = 2,
    direction   = "CW",
    net_name    = "COIL_NET",
    via_size    = 0.45
)

COILFORGE_SCHEMA_VERSION = 1


# --- INTERNAL HELPERS --- #

def _config_to_dict(config: CoilConfig) -> dict:
    """
    Convert CoilConfig into the JSON schema stored inside .kicad_pro.
    """
    return {
        "version":         COILFORGE_SCHEMA_VERSION,
        "hole_radius_mm":  config.hole_radius,
        "turns":           config.turns,
        "track_width_mm":  config.track_width,
        "spacing_mm":      config.spacing,
        "center_x_mm":     config.center_x,
        "center_y_mm":     config.center_y,
        "angle_deg":       config.angle,
        "layers":          config.layers,
        "direction":       config.direction,
        "net_name":        config.net_name,
        "via_size_mm":     config.via_size
    }


def _dict_to_config(data: dict) -> CoilConfig:
    """
    Convert a CoilForge JSON dictionary into a CoilConfig object.
    Missing or invalid values fall back to DEFAULT_CONFIG field-by-field.
    """
    return CoilConfig(
        hole_radius = float(data.get("hole_radius_mm", DEFAULT_CONFIG.hole_radius)),
        turns       = float(data.get("turns",          DEFAULT_CONFIG.turns)),
        track_width = float(data.get("track_width_mm", DEFAULT_CONFIG.track_width)),
        spacing     = float(data.get("spacing_mm",     DEFAULT_CONFIG.spacing)),
        center_x    = float(data.get("center_x_mm",    DEFAULT_CONFIG.center_x)),
        center_y    = float(data.get("center_y_mm",    DEFAULT_CONFIG.center_y)),
        angle       = float(data.get("angle_deg",      DEFAULT_CONFIG.angle)),
        layers      = int  (data.get("layers",         DEFAULT_CONFIG.layers)),
        direction   = str  (data.get("direction",      DEFAULT_CONFIG.direction)),
        net_name    = str  (data.get("net_name",       DEFAULT_CONFIG.net_name)),
        via_size    = float(data.get("via_size_mm",    DEFAULT_CONFIG.via_size))
    )


def _get_board_path() -> Optional[Path]:
    """
    Return the current board file path if available, otherwise None.
    """
    try:
        import pcbnew

        board = pcbnew.GetBoard()
        if board is None:
            return None

        board_file = board.GetFileName()
        if not board_file:
            return None

        path = Path(board_file)
        return path if path.exists() else path
    except Exception:
        return None


def get_project_path() -> Optional[Path]:
    """
    Return the current KiCad .kicad_pro file path based on the active board.

    Strategy:
    1. Get current .kicad_pcb path from pcbnew.
    2. Look in the same directory for a matching .kicad_pro file.
    3. Prefer same stem as the board file.
    4. If only one .kicad_pro exists, use it.
    5. Otherwise return None.
    """
    board_path = _get_board_path()
    if board_path is None:
        return None

    project_dir = board_path.parent
    board_stem = board_path.stem

    exact_match = project_dir / f"{board_stem}.kicad_pro"
    if exact_match.exists():
        return exact_match

    project_files = list(project_dir.glob("*.kicad_pro"))

    if len(project_files) == 1:
        return project_files[0]

    return None


def _read_project_json(path: Path) -> Optional[dict]:
    """
    Read and parse the .kicad_pro file.
    Return None on failure.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None


# --- PUBLIC API --- #

def load_settings() -> CoilConfig:
    """
    Load CoilForge settings from the current project's .kicad_pro file.

    Returns:
        CoilConfig loaded from:
            plugins -> coilforge
        or DEFAULT_CONFIG if the project file cannot be found/read or the key
        does not exist.
    """
    project_path = get_project_path()
    if project_path is None:
        return DEFAULT_CONFIG

    project_data = _read_project_json(project_path)
    if project_data is None:
        return DEFAULT_CONFIG

    try:
        coilforge_data = project_data.get("plugins", {}).get("coilforge", {})
        if not coilforge_data:
            return DEFAULT_CONFIG

        return _dict_to_config(coilforge_data)

    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_CONFIG


def save_settings(config: CoilConfig) -> bool:
    """
    Save CoilForge settings into the current project's .kicad_pro file under:

        plugins -> coilforge

    The file is written atomically:
    1. Read existing JSON
    2. Update only the CoilForge section
    3. Write to a temporary file
    4. Replace the original file

    Returns:
        True if save succeeds, otherwise False.
    """
    project_path = get_project_path()
    if project_path is None:
        return False

    project_data = _read_project_json(project_path)
    if project_data is None:
        return False

    try:
        project_data.setdefault("plugins", {})
        project_data["plugins"]["coilforge"] = _config_to_dict(config)

        temp_path = project_path.with_suffix(project_path.suffix + ".tmp")
        backup_path = project_path.with_suffix(project_path.suffix + ".bak")

        # Optional backup during development
        if project_path.exists():
            shutil.copy2(project_path, backup_path)

        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2)
            f.write("\n")

        temp_path.replace(project_path)
        return True

    except OSError:
        return False