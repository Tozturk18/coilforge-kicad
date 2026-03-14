# plugin.py

Main KiCad action plugin entrypoint.

## Purpose

`plugin.py` defines `CoilForgePlugin`, the class KiCad loads as an action plugin.
It connects dialog flow and native bridge execution.

## Important Symbols

- `CoilForgePlugin`: subclass of `pcbnew.ActionPlugin`.
- `format_config_summary(config)`: builds a readable config summary string using the pitch-based config.
- `CoilForgePlugin.defaults()`: sets plugin metadata (name, category, icons).
- `CoilForgePlugin.Run()`: executes the plugin flow and displays success/error messages.
