from .config import CoilConfig


FIELD_LABELS = {
    "hole_radius": "Hole Radius (mm)",
    "turns": "Number of Coil Turns",
    "track_width": "Track Width (mm)",
    "spacing": "Spacing (mm)",
    "center_x": "Center X Position (mm)",
    "center_y": "Center Y Position (mm)",
    "angle": "Angle (deg)",
    "layers": "Layers",
    "direction": "Direction",
    "net_name": "Net Name",
    "via_size": "Via Size (mm)",
}


def get_required_value(raw_values, field_name):
    """
    Retrieve a required raw value by stable field name.
    Raises ValueError when the field is missing from the submission.
    """
    try:
        return raw_values[field_name]
    except KeyError as exc:
        raise ValueError(f"{FIELD_LABELS[field_name]} is missing.") from exc


def parse_float(value, field_name):
    """
    Convert a string-like value to float.
    Raises ValueError with a user-friendly message on failure.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")


def parse_int(value, field_name):
    """
    Convert a string-like value to int.
    Raises ValueError with a user-friendly message on failure.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid integer.")


def parse_config(raw_values):
    """
    Convert raw dialog values into a typed CoilConfig.
    Expects a dictionary keyed by stable config field names.
    """
    config = CoilConfig(
        hole_radius=parse_float(get_required_value(raw_values, "hole_radius"), FIELD_LABELS["hole_radius"]),
        turns=parse_float(get_required_value(raw_values, "turns"), FIELD_LABELS["turns"]),
        track_width=parse_float(get_required_value(raw_values, "track_width"), FIELD_LABELS["track_width"]),
        spacing=parse_float(get_required_value(raw_values, "spacing"), FIELD_LABELS["spacing"]),
        center_x=parse_float(get_required_value(raw_values, "center_x"), FIELD_LABELS["center_x"]),
        center_y=parse_float(get_required_value(raw_values, "center_y"), FIELD_LABELS["center_y"]),
        angle=parse_float(get_required_value(raw_values, "angle"), FIELD_LABELS["angle"]),
        layers=parse_int(get_required_value(raw_values, "layers"), FIELD_LABELS["layers"]),
        direction=str(get_required_value(raw_values, "direction")).strip(),
        net_name=str(get_required_value(raw_values, "net_name")).strip(),
        via_size=parse_float(get_required_value(raw_values, "via_size"), FIELD_LABELS["via_size"])
    )

    validate_config(config)
    return config


def validate_config(config):
    """
    Validate engineering constraints for CoilConfig.
    Raises ValueError with a user-friendly message if invalid.
    """
    if config.hole_radius < 0:
        raise ValueError("Hole Radius (mm) must be 0 or greater.")

    if config.turns <= 0:
        raise ValueError("Number of Coil Turns must be greater than 0.")

    if config.track_width <= 0:
        raise ValueError("Track Width (mm) must be greater than 0.")

    if config.spacing < 0:
        raise ValueError("Spacing (mm) must be 0 or greater.")

    if config.layers < 1:
        raise ValueError("Layers must be at least 1.")

    if config.via_size <= 0:
        raise ValueError("Via Size (mm) must be greater than 0.")

    if config.direction not in ("CW", "CCW"):
        raise ValueError("Direction must be either CW or CCW.")

    if not config.net_name:
        raise ValueError("Net Name cannot be empty.")