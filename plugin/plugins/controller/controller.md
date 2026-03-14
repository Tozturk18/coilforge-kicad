# controller.py

Flow orchestration module between UI, validation, and persistence.

## Purpose

`controller.py` coordinates loading defaults, showing the dialog, validating input, and saving accepted settings.

## Important Symbols

- `DialogSubmission`: bundles validated config and save status.
- `prompt_for_config(parent=None)`: runs the dialog workflow and returns `DialogSubmission` or `None` when canceled.
