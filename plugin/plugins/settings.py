'''
@ filename: settings.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2024
@ license:  MIT License
@ description: This module implements functions for loading and saving user settings
    for the CoilForge plugin. The settings are stored in a JSON file located next 
    to the plugin code, and include all the parameters that the user can configure 
    in the dialog. The module also defines a default configuration that is used when 
    no settings file exists or when the file is invalid. The load_settings function 
    reads the JSON file and returns a CoilConfig object, while the save_settings function
    takes a CoilConfig object and writes it to the JSON file, returning a boolean indicating
    success or failure.
'''

# --- IMPORTS --- #
import json
from dataclasses import asdict
from pathlib import Path

# --- LOCAL IMPORTS --- #
from .config import CoilConfig

# --- CLASSES & FUNCTIONS --- #

# The default configuration used when no settings file exists or when the file is invalid.
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

def get_settings_path() -> Path:
    """
    Returns the JSON settings file path stored next to this plugin package.

    Args: None

    Returns: A Path object representing the relative path to the user_settings.json file.
    """
    return Path(__file__).resolve().parent / "user_settings.json"


def load_settings() -> CoilConfig:
    """
    Load saved settings from JSON.
    If the file does not exist or is invalid, return DEFAULT_CONFIG.

    Args: None

    Returns: An instance of CoilConfig with the loaded settings, or DEFAULT_CONFIG if loading fails.
    """
    # Get the path to the settings file
    path = get_settings_path()

    # If the settings file does not exist, return the default configuration.
    if not path.exists():
        return DEFAULT_CONFIG

    try:
        # Open the settings file and load the JSON data into a dictionary.
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert the loaded dictionary into a CoilConfig object, using default values for any missing fields.
        return CoilConfig(
            hole_radius = float(data.get("hole_radius", DEFAULT_CONFIG.hole_radius)),
            turns       = float(data.get("turns",       DEFAULT_CONFIG.turns)),
            track_width = float(data.get("track_width", DEFAULT_CONFIG.track_width)),
            spacing     = float(data.get("spacing",     DEFAULT_CONFIG.spacing)),
            center_x    = float(data.get("center_x",    DEFAULT_CONFIG.center_x)),
            center_y    = float(data.get("center_y",    DEFAULT_CONFIG.center_y)),
            angle       = float(data.get("angle",       DEFAULT_CONFIG.angle)),
            layers      = int  (data.get("layers",      DEFAULT_CONFIG.layers)),
            direction   = str  (data.get("direction",   DEFAULT_CONFIG.direction)),
            net_name    = str  (data.get("net_name",    DEFAULT_CONFIG.net_name)),
            via_size    = float(data.get("via_size",    DEFAULT_CONFIG.via_size))
        )

    # If there was an error reading the file or parsing the JSON, return the default configuration.
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_CONFIG


def save_settings(config: CoilConfig) -> bool:
    """
    Save CoilConfig to JSON.
    Returns True on success, False on failure.

    Args: config [CoilConfig] - The coil configuration data to save to the JSON file.

    Returns: A boolean indicating whether the settings were saved successfully (True) or if there was an error (False).
    """

    # Get the path to the settings file
    path = get_settings_path()

    try:
        # Open the settings file for writing and dump the CoilConfig data as JSON. The asdict function converts the dataclass instance into a dictionary for JSON serialization.
        with path.open("w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=4)
        return True
    except OSError:
        return False