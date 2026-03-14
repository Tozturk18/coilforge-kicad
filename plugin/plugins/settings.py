import json
from dataclasses import asdict
from pathlib import Path

from .config import CoilConfig


DEFAULT_CONFIG = CoilConfig(
    hole_radius_mm=0.0,
    turns=10.0,
    track_width_mm=0.25,
    spacing_mm=0.20,
    center_x_mm=0.0,
    center_y_mm=0.0,
    angle_deg=0.0,
    layers=2,
    direction="CW",
    net_name="COIL_NET",
    via_size_mm=0.45
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
            hole_radius_mm=float(data.get("hole_radius_mm", DEFAULT_CONFIG.hole_radius_mm)),
            turns=float(data.get("turns", DEFAULT_CONFIG.turns)),
            track_width_mm=float(data.get("track_width_mm", DEFAULT_CONFIG.track_width_mm)),
            spacing_mm=float(data.get("spacing_mm", DEFAULT_CONFIG.spacing_mm)),
            center_x_mm=float(data.get("center_x_mm", DEFAULT_CONFIG.center_x_mm)),
            center_y_mm=float(data.get("center_y_mm", DEFAULT_CONFIG.center_y_mm)),
            angle_deg=float(data.get("angle_deg", DEFAULT_CONFIG.angle_deg)),
            layers=int(data.get("layers", DEFAULT_CONFIG.layers)),
            direction=str(data.get("direction", DEFAULT_CONFIG.direction)),
            net_name=str(data.get("net_name", DEFAULT_CONFIG.net_name)),
            via_size_mm=float(data.get("via_size_mm", DEFAULT_CONFIG.via_size_mm))
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