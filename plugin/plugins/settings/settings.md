# settings.py

Settings persistence module for plugin user preferences.

## Purpose

`settings.py` loads and saves `CoilConfig` values to the active KiCad `.kicad_pro` file.
The stored schema uses `pitch_mm`, while older `spacing_mm` data is still read for compatibility.

## Important Symbols

- `DEFAULT_CONFIG`: fallback config when no valid JSON exists.
- `load_settings()`: loads project JSON and returns typed config.
- `save_settings(config)`: writes config to the project file and reports success/failure.
