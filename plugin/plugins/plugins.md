# plugins

Main package documentation for `plugin/plugins`.

## Folder Scheme

- `__init__.py`: package bootstrap that registers the KiCad action plugin.
- `plugins.md`: this file.
- `plugin/plugin.py`: KiCad `ActionPlugin` entrypoint and runtime flow.
- `plugin/plugin.md`: docs specific to `plugin.py`.
- `dialog_ui/dialog_ui.py`: wxPython dialog UI definitions.
- `dialog_ui/dialog_py.md`: docs specific to `dialog_ui.py`.
- `bridge/bridge.py`: ctypes bridge to native C shared library.
- `bridge/bridge.md`: docs specific to `bridge.py`.
- `config/config.py`: shared typed config dataclass.
- `config/config.md`: docs specific to `config.py`.
- `controller/controller.py`: orchestration between UI, validation, and settings.
- `controller/controller.md`: docs specific to `controller.py`.
- `settings/settings.py`: JSON load/save utilities.
- `settings/settings.md`: docs specific to `settings.py`.
- `validator/validator.py`: parsing and validation rules.
- `validator/validator.md`: docs specific to `validator.py`.

## Runtime Flow

1. `__init__.py` registers `CoilForgePlugin`.
2. `plugin/plugin.py` starts the flow on `Run()`.
3. `controller/controller.py` loads defaults, opens dialog, validates, and saves.
4. `bridge/bridge.py` calls the C API via ctypes.
5. `settings/settings.py` persists accepted values to `user_settings.json`.
