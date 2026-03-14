from .config import CoilConfig


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
    Convert raw dialog string values into a typed CoilConfig.
    Expects a dictionary with UI field labels as keys.
    """
    config = CoilConfig(
        hole_radius_mm=parse_float(raw_values["Hole Radius (mm)"], "Hole Radius (mm)"),
        turns=parse_float(raw_values["Number of Coil Turns"], "Number of Coil Turns"),
        track_width_mm=parse_float(raw_values["Track Width (mm)"], "Track Width (mm)"),
        spacing_mm=parse_float(raw_values["Spacing (mm)"], "Spacing (mm)"),
        center_x_mm=parse_float(raw_values["Center X Position (mm)"], "Center X Position (mm)"),
        center_y_mm=parse_float(raw_values["Center Y Position (mm)"], "Center Y Position (mm)"),
        angle_deg=parse_float(raw_values["Angle (deg)"], "Angle (deg)"),
        layers=parse_int(raw_values["Layers"], "Layers"),
        direction=raw_values["Direction"],
        net_name=str(raw_values["Net Name"]).strip(),
        via_size_mm=parse_float(raw_values["Via Size (mm)"], "Via Size (mm)")
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