# validator.py

Input parsing and engineering constraints validation.

## Purpose

`validator.py` converts string input values into typed values and ensures they satisfy project constraints.

## Important Symbols

- `FIELD_LABELS`: user-facing labels for error messages.
- `get_required_value(...)`: fetches required fields with user-friendly errors.
- `parse_float(...)`: typed conversion with readable error handling.
- `parse_int(...)`: typed conversion with readable error handling.
- `parse_config(...)`: converts raw dialog values to `CoilConfig`.
- `validate_config(...)`: enforces constraints (dimensions, turns, layers, direction, net name).
