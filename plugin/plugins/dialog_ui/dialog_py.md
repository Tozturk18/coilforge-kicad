# dialog_ui.py

UI-only module for CoilForge configuration input.

## Purpose

`dialog_ui.py` builds and manages the wxPython dialog used to collect user parameters.
It exposes `pitch` as the main user-facing parameter while keeping a linked derived
`spacing` field visible to prevent accidental overlap.

## Important Symbols

- `DEFAULT_VALUES`: fallback field values used to initialize the dialog.
- `TEXT_FIELD_SPECS`: field key/label structure used by the form.
- `CoilForgeDialog`: main dialog class.
- Linked `pitch` and `spacing` fields: editing either updates the other using the current track width.
- Live warning styling: highlights the linked fields when spacing becomes negative.
- `CoilForgeDialog.get_input_values()`: returns submitted values keyed by stable field names.
- `CoilForgeDialog.get_raw_values()`: compatibility alias to `get_input_values()`.
