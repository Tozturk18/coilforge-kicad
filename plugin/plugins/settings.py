import json
from dataclasses import asdict
from pathlib import Path

from .config import CoilConfig


DEFAULT_CONFIG = CoilConfig(
    hole_radius=0.0,
    turns=10.0,
    track_width=0.25,
    spacing=0.20,
    center_x=0.0,
    center_y=0.0,
    angle=0.0,
    layers=2,
    direction="CW",
    net_name="COIL_NET",
    via_size=0.45
)


def get_settings_path():
    """
    Returns the JSON settings file path stored next to this plugin package.
    """
    return Path(__file__).resolve().parent / "user_settings.json"


def load_settings():
    """
    Load saved settings from JSON.
    If the file does not exist or is invalid, return DEFAULT_CONFIG.
    """
    path = get_settings_path()

    if not path.exists():
        return DEFAULT_CONFIG

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return CoilConfig(
            hole_radius=float(data.get("hole_radius", DEFAULT_CONFIG.hole_radius)),
            turns=float(data.get("turns", DEFAULT_CONFIG.turns)),
            track_width=float(data.get("track_width", DEFAULT_CONFIG.track_width)),
            spacing=float(data.get("spacing", DEFAULT_CONFIG.spacing)),
            center_x=float(data.get("center_x", DEFAULT_CONFIG.center_x)),
            center_y=float(data.get("center_y", DEFAULT_CONFIG.center_y)),
            angle=float(data.get("angle", DEFAULT_CONFIG.angle)),
            layers=int(data.get("layers", DEFAULT_CONFIG.layers)),
            direction=str(data.get("direction", DEFAULT_CONFIG.direction)),
            net_name=str(data.get("net_name", DEFAULT_CONFIG.net_name)),
            via_size=float(data.get("via_size", DEFAULT_CONFIG.via_size))
        )

    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_CONFIG


def save_settings(config):
    """
    Save CoilConfig to JSON.
    Returns True on success, False on failure.
    """
    path = get_settings_path()

    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=4)
        return True
    except OSError:
        return False