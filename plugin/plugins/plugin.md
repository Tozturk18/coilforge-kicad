# plugin/plugins

Python runtime package for the CoilForge KiCad plugin.

## Purpose

This package contains the KiCad Action Plugin entry point, the dialog UI,
validation and parsing logic, settings persistence, and the future bridge into
the C engine. The current flow is split so that UI code only collects input,
validation code parses and checks that input, settings code persists accepted
values, and a small controller module coordinates those parts.

## Modules

### __init__.py

Package bootstrap for KiCad.

- `CoilForgePlugin().register()` registers the action plugin with KiCad when the package is imported.

### bridge.py

Reserved integration point between the KiCad Python layer and the future C engine.

- The module currently contains only a placeholder comment and does not expose functions yet.

### config.py

Defines the typed configuration object shared across the plugin modules.

- `CoilConfig` is a dataclass that stores all validated coil parameters in one stable structure.

### controller.py

Coordinates the dialog submission flow without owning UI layout, validation rules, or JSON persistence.

- `DialogSubmission` stores the accepted `CoilConfig` plus whether the settings file was saved successfully.
- `prompt_for_config(parent=None)` loads saved settings, opens the dialog, validates submitted values, saves accepted settings, and returns the result or `None` when the dialog is cancelled.

### dialog_ui.py

Defines the wxPython dialog and keeps widget creation separate from business rules.

- `DEFAULT_VALUES` contains the UI fallback values used when no saved settings are available.
- `TEXT_FIELD_SPECS` maps each text control to a stable internal field name and a user-facing label.
- `CoilForgeDialog` is the modal dialog class shown inside KiCad.
- `CoilForgeDialog.__init__(parent=None, initial_config=None)` builds the Geometry, Placement, Routing, and Connectivity sections and preloads values from the given config.
- `CoilForgeDialog._build_defaults(initial_config)` merges the saved config with the default field values used by the dialog.
- `CoilForgeDialog.get_input_values()` returns the current dialog values keyed by stable config field names rather than UI labels.
- `CoilForgeDialog.get_raw_values()` is a compatibility alias for older call sites and currently forwards to `get_input_values()`.

### plugin.py

Defines the KiCad `ActionPlugin` entry point and user-facing success or error messages.

- `format_config_summary(config)` formats the accepted configuration into a readable summary for the message box.
- `CoilForgePlugin` is the KiCad action plugin class.
- `CoilForgePlugin.defaults()` sets the plugin metadata KiCad uses in its UI.
- `CoilForgePlugin.Run()` opens the parameter flow through `controller.py`, handles validation errors, and reports whether settings were saved.

### settings.py

Handles plugin-side persistence for accepted settings.

- `DEFAULT_CONFIG` is the fallback `CoilConfig` used when no valid user settings file exists.
- `get_settings_path()` returns the JSON file path used to store plugin settings.
- `load_settings()` reads and converts persisted JSON into a `CoilConfig`, or returns `DEFAULT_CONFIG` when the file is missing or invalid.
- `save_settings(config)` writes a validated `CoilConfig` to disk and returns `True` on success or `False` on failure.

### validator.py

Owns string-to-type conversion and engineering rule checks for submitted configuration values.

- `FIELD_LABELS` maps stable internal field names to user-facing labels used in validation messages.
- `get_required_value(raw_values, field_name)` retrieves a submitted field and raises a user-friendly error when it is missing.
- `parse_float(value, field_name)` converts a value to `float` and raises a readable `ValueError` on failure.
- `parse_int(value, field_name)` converts a value to `int` and raises a readable `ValueError` on failure.
- `parse_config(raw_values)` converts submitted dialog values into a typed `CoilConfig` and then validates it.
- `validate_config(config)` enforces engineering and UI constraints such as positive dimensions, valid layer counts, valid direction values, and a non-empty net name.
