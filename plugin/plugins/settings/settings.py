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
    pitch       = 0.45,
    arc_resolution = 2,
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
        "hole_radius":  config.hole_radius,
        "turns":           config.turns,
        "track_width":  config.track_width,
        "pitch":        config.pitch,
        "arc_resolution": config.arc_resolution,
        "center_x":     config.center_x,
        "center_y":     config.center_y,
        "angle":       config.angle,
        "layers":          config.layers,
        "direction":       config.direction,
        "net_name":        config.net_name,
        "via_size":     config.via_size
    }


def _is_legacy_single_config(data: dict) -> bool:
    """Return True when the payload looks like the older single-config schema."""
    return "coils" not in data and ("hole_radius" in data or "pitch" in data or "spacing" in data)


def _extract_coils_dict(coilforge_data: dict) -> dict[str, dict]:
    """Normalize legacy and current schema variants into a single coils dictionary."""
    coils = coilforge_data.get("coils")
    if isinstance(coils, dict):
        return coils

    if _is_legacy_single_config(coilforge_data):
        return {"coil_0001": coilforge_data}

    return {}


def _coilforge_payload_from_configs(coils: dict[str, CoilConfig]) -> dict:
    """Build the persisted coilforge JSON payload."""
    return {
        "version": COILFORGE_SCHEMA_VERSION,
        "coils": {coil_id: _config_to_dict(config) for coil_id, config in coils.items()},
    }


def _dict_to_config(data: dict) -> CoilConfig:
    """
    Convert a CoilForge JSON dictionary into a CoilConfig object.
    Missing or invalid values fall back to DEFAULT_CONFIG field-by-field.
    """
    track_width = float(data.get("track_width", DEFAULT_CONFIG.track_width))
    pitch_value = data.get("pitch")

    if pitch_value is None:
        spacing_value = float(data.get("spacing", DEFAULT_CONFIG.pitch - track_width))
        pitch = spacing_value + track_width
    else:
        pitch = float(pitch_value)

    return CoilConfig(
        hole_radius = float(data.get("hole_radius", DEFAULT_CONFIG.hole_radius)),
        turns       = float(data.get("turns",          DEFAULT_CONFIG.turns)),
        track_width = track_width,
        pitch       = pitch,
        arc_resolution = int(data.get("arc_resolution", DEFAULT_CONFIG.arc_resolution)),
        center_x    = float(data.get("center_x",    DEFAULT_CONFIG.center_x)),
        center_y    = float(data.get("center_y",    DEFAULT_CONFIG.center_y)),
        angle       = float(data.get("angle",      DEFAULT_CONFIG.angle)),
        layers      = int  (data.get("layers",         DEFAULT_CONFIG.layers)),
        direction   = str  (data.get("direction",      DEFAULT_CONFIG.direction)),
        net_name    = str  (data.get("net_name",       DEFAULT_CONFIG.net_name)),
        via_size    = float(data.get("via_size",    DEFAULT_CONFIG.via_size))
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


def _write_project_json(path: Path, project_data: dict) -> bool:
    """Write project JSON atomically and keep a backup for recovery."""
    try:
        temp_path = path.with_suffix(path.suffix + ".tmp")
        backup_path = path.with_suffix(path.suffix + ".bak")

        if path.exists():
            shutil.copy2(path, backup_path)

        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2)
            f.write("\n")

        temp_path.replace(path)
        return True
    except OSError:
        return False


def _load_coils_from_project_data(project_data: dict) -> dict[str, CoilConfig]:
    """Parse all CoilForge coil configs from loaded .kicad_pro JSON."""
    coilforge_data = project_data.get("plugins", {}).get("coilforge", {})
    coils_data = _extract_coils_dict(coilforge_data)

    coils: dict[str, CoilConfig] = {}
    for coil_id, config_data in coils_data.items():
        if not isinstance(coil_id, str) or not isinstance(config_data, dict):
            continue
        try:
            coils[coil_id] = _dict_to_config(config_data)
        except (TypeError, ValueError):
            continue

    return coils


def _first_coil_config(coils: dict[str, CoilConfig]) -> CoilConfig:
    """Return the first config in stable key order, or DEFAULT_CONFIG."""
    if not coils:
        return DEFAULT_CONFIG
    first_key = sorted(coils.keys())[0]
    return coils[first_key]


def _next_coil_id(existing_ids: list[str]) -> str:
    """Generate the next readable coil id in the form coil_0001."""
    used_numbers = set()
    for coil_id in existing_ids:
        if coil_id.startswith("coil_"):
            suffix = coil_id[5:]
            if suffix.isdigit():
                used_numbers.add(int(suffix))

    next_number = 1
    while next_number in used_numbers:
        next_number += 1

    return f"coil_{next_number:04d}"


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
        coils = _load_coils_from_project_data(project_data)
        return _first_coil_config(coils)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_CONFIG


def load_all_coils() -> dict[str, CoilConfig]:
    """Load all saved CoilForge coils from the current project's .kicad_pro file."""
    project_path = get_project_path()
    if project_path is None:
        return {}

    project_data = _read_project_json(project_path)
    if project_data is None:
        return {}

    return _load_coils_from_project_data(project_data)


def load_coil_settings(coil_id: str) -> Optional[CoilConfig]:
    """Load one CoilForge coil config by coil id."""
    return load_all_coils().get(coil_id)


def create_new_coil_id() -> str:
    """Create a new unique coil id for the current project."""
    coils = load_all_coils()
    return _next_coil_id(list(coils.keys()))


def save_coil_settings(coil_id: str, config: CoilConfig) -> bool:
    """Save or update one CoilForge coil config by coil id."""
    if not coil_id:
        return False

    project_path = get_project_path()
    if project_path is None:
        return False

    project_data = _read_project_json(project_path)
    if project_data is None:
        return False

    coils = _load_coils_from_project_data(project_data)
    coils[coil_id] = config

    project_data.setdefault("plugins", {})
    project_data["plugins"]["coilforge"] = _coilforge_payload_from_configs(coils)

    return _write_project_json(project_path, project_data)


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
    coils = load_all_coils()

    if coils:
        target_coil_id = sorted(coils.keys())[0]
    else:
        target_coil_id = "coil_0001"

    return save_coil_settings(target_coil_id, config)
