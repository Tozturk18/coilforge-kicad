'''
@ filename: controller.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2024
@ license:  MIT License
@ description: This module contains the main controller logic for the CoilForge plugin.
'''

# --- IMPORTS --- #
from dataclasses import dataclass
from typing import Optional

import wx

from ..config.config import CoilConfig
from ..dialog_ui.dialog_ui import CoilForgeDialog
from ..validator.validator import parse_config


# --- CLASSES & FUNCTIONS --- #

@dataclass(frozen=True)
class DialogSubmission:
    '''
    Data class representing the result of a successful dialog submission.
    '''
    config: CoilConfig      # The validated configuration submitted by the user


def prompt_for_config(
    parent: Optional[wx.Window] = None,
    initial_config: Optional[CoilConfig] = None,
) -> Optional["DialogSubmission"]:
    """
    Open the CoilForge dialog, validate submitted values, and persist them.

    Returns DialogSubmission when the user accepts the dialog.
    Returns None when the user cancels it.
    Raises ValueError when submitted values are invalid.
    """

    # Create and show the dialog
    dialog = CoilForgeDialog(parent, initial_config=initial_config)

    try:
        # Show the dialog and check if the user accepted it
        if dialog.ShowModal() != wx.ID_OK:
            return None

        # Parse and validate the submitted values
        config = parse_config(dialog.get_input_values())
        return DialogSubmission(config=config)
    finally:
        # Ensure the dialog is destroyed to free resources
        dialog.Destroy()
