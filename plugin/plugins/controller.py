from dataclasses import dataclass

import wx

from .config import CoilConfig
from .dialog_ui import CoilForgeDialog
from .settings import load_settings, save_settings
from .validator import parse_config


@dataclass(frozen=True)
class DialogSubmission:
    config: CoilConfig
    settings_saved: bool


def prompt_for_config(parent=None):
    """
    Open the CoilForge dialog, validate submitted values, and persist them.

    Returns DialogSubmission when the user accepts the dialog.
    Returns None when the user cancels it.
    Raises ValueError when submitted values are invalid.
    """
    initial_config = load_settings()
    dialog = CoilForgeDialog(parent, initial_config=initial_config)

    try:
        if dialog.ShowModal() != wx.ID_OK:
            return None

        config = parse_config(dialog.get_input_values())
        return DialogSubmission(config=config, settings_saved=save_settings(config))
    finally:
        dialog.Destroy()