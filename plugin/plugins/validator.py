from .config import CoilConfig


FIELD_LABELS = {
    "hole_radius_mm": "Hole Radius (mm)",
    "turns": "Number of Coil Turns",
    "track_width_mm": "Track Width (mm)",
    "spacing_mm": "Spacing (mm)",
    "center_x_mm": "Center X Position (mm)",
    "center_y_mm": "Center Y Position (mm)",
    "angle_deg": "Angle (deg)",
    "layers": "Layers",
    "direction": "Direction",
    "net_name": "Net Name",
    "via_size_mm": "Via Size (mm)",
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
        hole_radius_mm=parse_float(get_required_value(raw_values, "hole_radius_mm"), FIELD_LABELS["hole_radius_mm"]),
        turns=parse_float(get_required_value(raw_values, "turns"), FIELD_LABELS["turns"]),
        track_width_mm=parse_float(get_required_value(raw_values, "track_width_mm"), FIELD_LABELS["track_width_mm"]),
        spacing_mm=parse_float(get_required_value(raw_values, "spacing_mm"), FIELD_LABELS["spacing_mm"]),
        center_x_mm=parse_float(get_required_value(raw_values, "center_x_mm"), FIELD_LABELS["center_x_mm"]),
        center_y_mm=parse_float(get_required_value(raw_values, "center_y_mm"), FIELD_LABELS["center_y_mm"]),
        angle_deg=parse_float(get_required_value(raw_values, "angle_deg"), FIELD_LABELS["angle_deg"]),
        layers=parse_int(get_required_value(raw_values, "layers"), FIELD_LABELS["layers"]),
        direction=str(get_required_value(raw_values, "direction")).strip(),
        net_name=str(get_required_value(raw_values, "net_name")).strip(),
        via_size_mm=parse_float(get_required_value(raw_values, "via_size_mm"), FIELD_LABELS["via_size_mm"])
    )

    validate_config(config)
    return config


def validate_config(config):
    """
    Validate engineering constraints for CoilConfig.
    Raises ValueError with a user-friendly message if invalid.
    """
    if config.hole_radius_mm < 0:
        raise ValueError("Hole Radius (mm) must be 0 or greater.")

    if config.turns <= 0:
        raise ValueError("Number of Coil Turns must be greater than 0.")

    if config.track_width_mm <= 0:
        raise ValueError("Track Width (mm) must be greater than 0.")

    if config.spacing_mm < 0:
        raise ValueError("Spacing (mm) must be 0 or greater.")

    if config.layers < 1:
        raise ValueError("Layers must be at least 1.")

    if config.via_size_mm <= 0:
        raise ValueError("Via Size (mm) must be greater than 0.")

    if config.direction not in ("CW", "CCW"):
        raise ValueError("Direction must be either CW or CCW.")

    if not config.net_name:
        raise ValueError("Net Name cannot be empty.")