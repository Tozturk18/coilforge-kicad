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
from typing import Any, Optional

# --- LOCAL IMPORTS --- #
from ..config.config import CoilConfig


# --- CONSTANTS --- #

_PLUGIN_SETTINGS_FILE = Path(__file__).with_name(".plugin_settings.json")

_FALLBACK_DEFAULT_CONFIG = CoilConfig(
    hole_radius    = 0.0,
    turns          = 10.0,
    track_width    = 0.25,
    pitch          = 0.45,
    arc_resolution = 2,
    center_x       = 0.0,
    center_y       = 0.0,
    angle          = 0.0,
    layers         = 2,
    direction      = "CW",
    net_name       = "COIL_NET",
    via_size       = 0.45
)

_FALLBACK_COILFORGE_SCHEMA_VERSION = 1
_FALLBACK_COILFORGE_GROUP_PREFIX = "CoilForge:"


def _read_plugin_settings_file() -> dict[str, Any]:
    """Read plugin-wide settings from the colocated hidden JSON file."""
    try:
        with _PLUGIN_SETTINGS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {}

    return data if isinstance(data, dict) else {}


def _runtime_settings() -> dict[str, Any]:
    """Return the plugin_runtime section from plugin settings JSON."""
    runtime = _PLUGIN_SETTINGS.get("plugin_runtime")
    return runtime if isinstance(runtime, dict) else {}


def _default_config_from_runtime_settings() -> CoilConfig:
    """Build DEFAULT_CONFIG from plugin settings with safe field-level fallback."""
    data = _runtime_settings().get("default_config")
    if not isinstance(data, dict):
        return _FALLBACK_DEFAULT_CONFIG

    track_width = float(data.get("track_width", _FALLBACK_DEFAULT_CONFIG.track_width))
    pitch_value = data.get("pitch")

    if pitch_value is None:
        spacing_value = float(data.get("spacing", _FALLBACK_DEFAULT_CONFIG.pitch - track_width))
        pitch = spacing_value + track_width
    else:
        pitch = float(pitch_value)

    return CoilConfig(
        hole_radius = float(data.get("hole_radius", _FALLBACK_DEFAULT_CONFIG.hole_radius)),
        turns       = float(data.get("turns",          _FALLBACK_DEFAULT_CONFIG.turns)),
        track_width = track_width,
        pitch       = pitch,
        arc_resolution = int(data.get("arc_resolution", _FALLBACK_DEFAULT_CONFIG.arc_resolution)),
        center_x    = float(data.get("center_x",    _FALLBACK_DEFAULT_CONFIG.center_x)),
        center_y    = float(data.get("center_y",    _FALLBACK_DEFAULT_CONFIG.center_y)),
        angle       = float(data.get("angle",       _FALLBACK_DEFAULT_CONFIG.angle)),
        layers      = int(data.get("layers",        _FALLBACK_DEFAULT_CONFIG.layers)),
        direction   = str(data.get("direction",     _FALLBACK_DEFAULT_CONFIG.direction)),
        net_name    = str(data.get("net_name",      _FALLBACK_DEFAULT_CONFIG.net_name)),
        via_size    = float(data.get("via_size",    _FALLBACK_DEFAULT_CONFIG.via_size)),
    )


def _schema_version_from_runtime_settings() -> int:
    """Read coilforge schema version from plugin settings, with fallback."""
    try:
        return int(_runtime_settings().get("coilforge_schema_version", _FALLBACK_COILFORGE_SCHEMA_VERSION))
    except (TypeError, ValueError):
        return _FALLBACK_COILFORGE_SCHEMA_VERSION


def _group_prefix_from_runtime_settings() -> str:
    """Read group prefix from plugin settings, with fallback."""
    value = _runtime_settings().get("coilforge_group_prefix", _FALLBACK_COILFORGE_GROUP_PREFIX)
    return str(value) if value else _FALLBACK_COILFORGE_GROUP_PREFIX


_PLUGIN_SETTINGS = _read_plugin_settings_file()


def get_plugin_settings() -> dict[str, Any]:
    """Return plugin-level settings loaded from .plugin_settings.json."""
    return dict(_PLUGIN_SETTINGS)


DEFAULT_CONFIG = _default_config_from_runtime_settings()

COILFORGE_SCHEMA_VERSION = _schema_version_from_runtime_settings()

COILFORGE_GROUP_PREFIX = _group_prefix_from_runtime_settings()

# --- INTERNAL HELPERS --- #

def _config_to_dict(config: CoilConfig) -> dict:
    """
    Convert CoilConfig into the JSON schema stored inside .kicad_pro.
    """
    return {
        "hole_radius"    : config.hole_radius,
        "turns"          : config.turns,
        "track_width"    : config.track_width,
        "pitch"          : config.pitch,
        "arc_resolution" : config.arc_resolution,
        "center_x"       : config.center_x,
        "center_y"       : config.center_y,
        "angle"          : config.angle,
        "layers"         : config.layers,
        "direction"      : config.direction,
        "net_name"       : config.net_name,
        "via_size"       : config.via_size
    }


def _is_legacy_single_config(data: dict) -> bool:
    """Return True when the payload looks like the older single-config schema."""
    return "coils" not in data and ("hole_radius" in data or "pitch" in data or "spacing" in data)


def _extract_project_config_dict(coilforge_data: dict) -> dict:
    """Extract project-level default config payload from current or legacy schema."""
    project_config = coilforge_data.get("project_config")
    if isinstance(project_config, dict):
        return project_config

    if _is_legacy_single_config(coilforge_data):
        return coilforge_data

    return {}


def _extract_coils_dict(coilforge_data: dict) -> dict[str, dict]:
    """Normalize legacy and current schema variants into a single coils dictionary."""
    coils = coilforge_data.get("coils")
    if isinstance(coils, dict):
        return coils

    if _is_legacy_single_config(coilforge_data):
        return {"coil_0001": coilforge_data}

    return {}


def _coilforge_payload_from_configs(
    project_config: CoilConfig,
    coils: dict[str, CoilConfig],
) -> dict:
    """Build the persisted coilforge JSON payload."""
    return {
        "version": COILFORGE_SCHEMA_VERSION,
        "project_config": _config_to_dict(project_config),
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


def _load_project_config_from_project_data(project_data: dict) -> CoilConfig:
    """Parse project-level default CoilForge settings from loaded .kicad_pro JSON."""
    coilforge_data = project_data.get("plugins", {}).get("coilforge", {})
    project_config_data = _extract_project_config_dict(coilforge_data)

    if not project_config_data:
        coils = _load_coils_from_project_data(project_data)
        return _first_coil_config(coils)

    try:
        return _dict_to_config(project_config_data)
    except (TypeError, ValueError):
        return DEFAULT_CONFIG


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
        return _load_project_config_from_project_data(project_data)
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

    project_config = _load_project_config_from_project_data(project_data)
    coils = _load_coils_from_project_data(project_data)
    coils[coil_id] = config

    project_data.setdefault("plugins", {})
    project_data["plugins"]["coilforge"] = _coilforge_payload_from_configs(project_config, coils)

    return _write_project_json(project_path, project_data)


def _iter_container_items(container):
    """Iterate KiCad SWIG containers across API variants."""
    if container is None:
        return

    if hasattr(container, "GetCount") and hasattr(container, "GetItem"):
        for i in range(container.GetCount()):
            yield container.GetItem(i)
        return

    if hasattr(container, "Size") and hasattr(container, "Item"):
        for i in range(container.Size()):
            yield container.Item(i)
        return

    try:
        for item in container:
            yield item
    except TypeError:
        return


def _iter_board_groups(board):
    """Yield board groups across KiCad API variants."""
    if board is None:
        return

    if hasattr(board, "Groups"):
        yield from _iter_container_items(board.Groups())
        return

    if hasattr(board, "GetGroups"):
        yield from _iter_container_items(board.GetGroups())


def _board_coil_ids(board) -> set[str]:
    """Collect CoilForge coil ids currently present on the board by group name."""
    from ..arcs.arcs import coil_id_from_group_name

    coil_ids: set[str] = set()
    for group in _iter_board_groups(board):
        group_name = group.GetName() if hasattr(group, "GetName") else ""
        coil_id = coil_id_from_group_name(group_name)
        if coil_id:
            coil_ids.add(coil_id)

    return coil_ids


def reconcile_settings(board=None) -> bool:
    """
    Remove per-coil settings that are not present in the currently loaded board.

    Project-level default settings are preserved.
    """
    if board is None:
        try:
            import pcbnew
            board = pcbnew.GetBoard()
        except Exception:
            board = None

    project_path = get_project_path()
    if project_path is None:
        return False

    project_data = _read_project_json(project_path)
    if project_data is None:
        return False

    project_config = _load_project_config_from_project_data(project_data)
    saved_coils = _load_coils_from_project_data(project_data)

    if not saved_coils:
        return True

    board_ids = _board_coil_ids(board)
    pruned_coils = {
        coil_id: config
        for coil_id, config in saved_coils.items()
        if coil_id in board_ids
    }

    if len(pruned_coils) == len(saved_coils):
        return True

    project_data.setdefault("plugins", {})
    project_data["plugins"]["coilforge"] = _coilforge_payload_from_configs(project_config, pruned_coils)

    return _write_project_json(project_path, project_data)


# Backward-compatible alias for older imports.
reconcile_coil_settings_with_board = reconcile_settings


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

    coils = _load_coils_from_project_data(project_data)

    project_data.setdefault("plugins", {})
    project_data["plugins"]["coilforge"] = _coilforge_payload_from_configs(config, coils)

    return _write_project_json(project_path, project_data)
