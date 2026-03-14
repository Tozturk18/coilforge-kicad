# settings.py

Settings persistence module for plugin user preferences.

## Purpose

`settings.py` loads and saves `CoilConfig` values to `user_settings.json`.

## Important Symbols

- `DEFAULT_CONFIG`: fallback config when no valid JSON exists.
- `get_settings_path()`: resolves settings file path.
- `load_settings()`: loads JSON and returns typed config.
- `save_settings(config)`: writes config to JSON and reports success/failure.
