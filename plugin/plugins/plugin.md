# plugin

KiCad Action Plugin interface for kicad-bldc-coil-generator.

## Purpose

Provides a KiCad GUI plugin that wraps the C engine, allowing users to
generate PCB coils directly from within KiCad.

## Files

- `action_plugin.py` — KiCad `ActionPlugin` subclass registration
- `bridge.py` — Calls into the C engine via subprocess or ctypes
