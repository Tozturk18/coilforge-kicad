'''
@ filename: controller.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2024
@ license:  MIT License
@ description: This module contains the main controller logic for the CoilForge plugin.
'''

# --- IMPORTS --- #
from dataclasses import dataclass

import wx

from .config import CoilConfig
from .dialog_ui import CoilForgeDialog
from .settings import load_settings, save_settings
from .validator import parse_config


# --- CLASSES & FUNCTIONS --- #

@dataclass(frozen=True)
class DialogSubmission:
    '''
    Data class representing the result of a successful dialog submission.
    '''
    config: CoilConfig      # The validated configuration submitted by the user
    settings_saved: bool    # Whether the settings were successfully saved to disk


def prompt_for_config(parent=None):
    """
    Open the CoilForge dialog, validate submitted values, and persist them.

    Returns DialogSubmission when the user accepts the dialog.
    Returns None when the user cancels it.
    Raises ValueError when submitted values are invalid.
    """

    # Load initial settings to pre-populate the dialog fields
    initial_config = load_settings()

    # Create and show the dialog
    dialog = CoilForgeDialog(parent, initial_config=initial_config)

    try:
        # Show the dialog and check if the user accepted it
        if dialog.ShowModal() != wx.ID_OK:
            return None

        # Parse and validate the submitted values, then save settings
        config = parse_config(dialog.get_input_values())
        return DialogSubmission(config=config, settings_saved=save_settings(config))
    finally:
        # Ensure the dialog is destroyed to free resources
        dialog.Destroy()