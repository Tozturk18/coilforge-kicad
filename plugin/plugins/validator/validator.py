'''
@ filename: validator.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2024
@ license:  MIT License
@ description: This module implements functions for validating and parsing user
    input values from the dialog. The main function, parse_config, takes a dictionary
    of raw string values from the dialog, converts them to the appropriate types, 
    and returns a CoilConfig object. It also performs validation checks on the values 
    to ensure they meet engineering constraints, raising ValueError with user-friendly 
    messages if any values are invalid. Helper functions are defined for parsing floats 
    and integers, as well as for retrieving required values from the input dictionary.
'''

# --- IMPORTS --- #
from typing import Any

from ..config.config import CoilConfig

# --- CLASSES & FUNCTIONS --- #

# A mapping of config field names to their user-friendly labels, used for error messages.
FIELD_LABELS = {
    "hole_radius" : "Hole Radius (mm)",
    "turns"       : "Number of Coil Turns",
    "track_width" : "Track Width (mm)",
    "pitch"       : "Pitch (mm)",
    "arc_resolution": "Arc Resolution",
    "center_x"    : "Center X Position (mm)",
    "center_y"    : "Center Y Position (mm)",
    "angle"       : "Angle (deg)",
    "layers"      : "Layers",
    "direction"   : "Direction",
    "net_name"    : "Net Name",
    "via_size"    : "Via Size (mm)",
}


def get_required_value(raw_values: dict[str, Any], field_name: str) -> Any:
    """
    Retrieve a required raw value by stable field name.
    Raises ValueError when the field is missing from the submission.

    Args: raw_values [dict] - A dictionary of raw input values from the dialog, keyed by stable field names.
          field_name [str] - The stable field name to retrieve from the raw values.

    Returns: The raw value corresponding to the specified field name. If the field is missing, a ValueError is raised with a message indicating which field is required.
    """
    try:
        return raw_values[field_name]
    except KeyError as exc:
        raise ValueError(f"{FIELD_LABELS[field_name]} is missing.") from exc


def parse_float(value: Any, field_name: str) -> float:
    """
    Convert a string-like value to float.
    Raises ValueError with a user-friendly message on failure.

    Args: value - The raw input value to convert to a float. This is typically a string from the dialog input.
          field_name [str] - The stable field name corresponding to this value, used for error messages.

    Returns: The input value converted to a float. If the conversion fails (e.g., if the input is not a valid number), a ValueError is raised with a message indicating which field must be a valid number.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{FIELD_LABELS[field_name]} must be a valid number.")


def parse_int(value: Any, field_name: str) -> int:
    """
    Convert a string-like value to int.
    Raises ValueError with a user-friendly message on failure.

    Args: value - The raw input value to convert to an integer. This is typically a string from the dialog input.
          field_name [str] - The stable field name corresponding to this value, used for error messages.

    Returns: The input value converted to an integer. If the conversion fails (e.g., if the input is not a valid integer), a ValueError is raised with a message indicating which field must be a valid integer.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{FIELD_LABELS[field_name]} must be a valid integer.")


def parse_config(raw_values: dict[str, Any]) -> CoilConfig:
    """
    Convert raw dialog values into a typed CoilConfig.
    Expects a dictionary keyed by stable config field names.

    Args: raw_values [dict] - A dictionary of raw input values from the dialog, keyed by stable field names.

    Returns: An instance of CoilConfig with fields populated from the raw input values. The function also performs validation checks on the values, and if any value is invalid (e.g., missing required fields, non-numeric input where a number is expected), it raises a ValueError with a user-friendly message indicating which field is invalid and what the issue is.
    """
    config = CoilConfig(
        hole_radius = parse_float(get_required_value(raw_values, "hole_radius"), "hole_radius"),
        turns       = parse_float(get_required_value(raw_values, "turns"),       "turns"),
        track_width = parse_float(get_required_value(raw_values, "track_width"), "track_width"),
        pitch       = parse_float(get_required_value(raw_values, "pitch"),       "pitch"),
        arc_resolution = parse_int(get_required_value(raw_values, "arc_resolution"), "arc_resolution"),
        center_x    = parse_float(get_required_value(raw_values, "center_x"),    "center_x"),
        center_y    = parse_float(get_required_value(raw_values, "center_y"),    "center_y"),
        angle       = parse_float(get_required_value(raw_values, "angle"),       "angle"),
        layers      = parse_int  (get_required_value(raw_values, "layers"),      "layers"),
        direction   = str        (get_required_value(raw_values, "direction")).strip(),
        net_name    = str        (get_required_value(raw_values, "net_name")).strip(),
        via_size    = parse_float(get_required_value(raw_values, "via_size"),    "via_size")
    )

    # Validate and return the config
    validate_config(config)
    return config


def validate_config(config: CoilConfig) -> None:
    """
    Validate engineering constraints for CoilConfig.
    Raises ValueError with a user-friendly message if invalid.

    Args: config [CoilConfig] - The coil configuration data to validate.

    Returns: None or an error
    """
    if config.hole_radius < 0:
        raise ValueError("Hole Radius (mm) must be 0 or greater.")

    if config.turns <= 0:
        raise ValueError("Number of Coil Turns must be greater than 0.")

    if config.track_width <= 0:
        raise ValueError("Track Width (mm) must be greater than 0.")

    if config.pitch <= 0:
        raise ValueError("Pitch (mm) must be greater than 0.")

    if config.pitch < config.track_width:
        raise ValueError("Pitch (mm) must be greater than or equal to Track Width (mm).")

    if config.arc_resolution < 2:
        raise ValueError("Arc Resolution must be at least 2.")

    if config.arc_resolution % 2 != 0:
        raise ValueError("Arc Resolution must be a multiple of 2.")

    if config.layers < 1:
        raise ValueError("Layers must be at least 1.")

    if config.via_size <= 0:
        raise ValueError("Via Size (mm) must be greater than 0.")

    if config.direction not in ("CW", "CCW"):
        raise ValueError("Direction must be either CW or CCW.")

    if not config.net_name:
        raise ValueError("Net Name cannot be empty.")
