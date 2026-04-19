#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File:       //plugin/plugins/controller/controller.py
Date:       2026-03-13
Author:     Ozgur Tuna Ozturk
Contact:    [@Tozturk18](tunaozturk2001@hotmail.com)
Last Mod:   2026-03-15
Version:    0.1.0
License:    MIT License
Description:
    This module contains the main controller logic for the CoilForge plugin.
"""

# === IMPORTS === #
import wx               # For creating dialogs and message boxes in the plugin UI
from dataclasses import (
    dataclass           # For defining simple data structures to hold dialog submission results
)
from typing import (
    Optional            # For type hinting optional return values from functions
)

# === INTERNAL MODULES === #
from ..config.config import (
    CoilConfig          # Coil configuration data structure
)
from ..dialog_ui.dialog_ui import (
    CoilForgeDialog     # Dialog for collecting coil configuration input
)
from ..validator.validator import (
    parse_config        # Function to parse and validate dialog input values into a CoilConfig object
)


# === FUNCTIONS === #
def prompt_config( parent: Optional[wx.Window] = None, initial_config: Optional[CoilConfig] = None) -> Optional[CoilConfig]:
    """
    Open the CoilForge dialog, validate submitted values, and persist them.

    Returns CoilConfig when the user accepts the dialog.
    Returns None when the user cancels it.
    Raises ValueError when submitted values are invalid.
    """

    # Create the dialog with default values
    dialog = CoilForgeDialog(parent, initial_config=initial_config)

    try:
        # Show the dialog and check if the user accepted it
        if dialog.ShowModal() != wx.ID_OK:
            return None # User cancelled the dialog

        # Parse and validate the submitted values
        config : CoilConfig = parse_config(dialog.get_values())
        return config
    finally:
        # Ensure the dialog is destroyed to free resources
        dialog.Destroy()


# Backward-compatible alias for older imports.
prompt_for_config = prompt_config
