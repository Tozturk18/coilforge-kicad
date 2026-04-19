#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File:       //plugin/plugins/plugin/plugin.py
Date:       2026-03-13
Author:     Ozgur Tuna Ozturk
Contact:    [@Tozturk18](tunaozturk2001@hotmail.com)
Last Mod:   2026-03-15
Version:    0.1.0
License:    MIT License
Description:
    This module defines the main entry point for the CoilForge plugin, 
    which integrates the dialog UI and the bridge to the native library. 
    It implements the CoilForgePlugin class that inherits from pcbnew.ActionPlugin, 
    allowing it to be registered as a plugin action in KiCad. The plugin prompts the user
    for coil configuration parameters, validates them, and then calls the native CoilForge 
    library to generate the coil geometry, displaying the output or any errors in message boxes.
"""

from __future__ import annotations

# === IMPORTS === #
from pathlib import Path            # For resolving plugin resource paths
from typing import Any
import pcbnew                       # KiCad's Python API for interacting with the PCB editor
import wx                           # For creating dialogs and message boxes in the plugin UI

# === INTERNAL MODULES === #

# ___DATA STRUCTURES___ #
from ..config.config import (
    CoilConfig                      # Coil configuration data structure
)
# ___CONTROLLER___ #
from ..controller.controller import (
    prompt_config                   # Prompt user for coil configuration parameters
)
# ___CTYPES BRIDGE___ #
from ..bridge.bridge import (
    run_ctypes_bridge, 
    generate_nodes, 
    get_via_result
)
# ___KiCAD ARCS UTILS___ #
from ..arcs.arcs import (
    add_arcs_to_current_board,
    delete_group_and_items,
    get_selected_coilforge_groups,
    make_coilforge_group_name,
)

from ..settings.settings import (
    create_new_coil_id, 
    load_coil_settings, 
    load_settings, 
    reconcile_settings,
    save_coil_settings
)

from ..settings.settings import (
    save_settings
)

# --- CLASSES & FUNCTIONS --- #

def _icon_path() -> str:
    """Resolve icon path from KiCad install layout, with repo fallback for local runs."""

    # Get the current file path
    module_path = Path(__file__).resolve()

    # Installed layout:
    # .../3rdparty/plugins/<plugin_id>/plugin/plugin.py
    # .../3rdparty/resources/<plugin_id>/icon.png
    plugin_id = module_path.parents[1].name
    installed_icon = module_path.parents[2].parent / "resources" / plugin_id / "icon.png"
    if installed_icon.exists():
        return str(installed_icon)

    # Repository layout:
    # .../plugin/plugins/plugin/plugin.py
    # .../plugin/resources/icon.png
    repo_icon = module_path.parents[2] / "resources" / "icon.png"
    if repo_icon.exists():
        return str(repo_icon)

    # Fallback
    return "icon.png"

def _message_box(title: str, message: str, style: int = wx.OK | wx.ICON_INFORMATION) -> None:
    """Helper function to show a message box with the given title, message, and style."""
    wx.MessageBox(
        message,
        title,
        style
    )

def _prompt_config(initial_config: CoilConfig) -> CoilConfig | None:
    '''
    Prompt the user for coil configuration parameters using the dialog, and validate the input.

    Args: initial_config [CoilConfig] - The initial coil configuration to prefill the dialog fields.

    Returns: An instance of CoilConfig with the validated configuration parameters, or None if the user canceled the dialog.
    Raises: ValueError if the input validation fails (e.g., missing or invalid parameters).
    '''

    try:
        # Prompt the user for coil configuration parameters using the dialog, and validate the input.
        config = prompt_config(None, initial_config=initial_config)

    except ValueError as exc:
        # Show error message if validation fails
        _message_box("Invalid Input", str(exc), wx.OK | wx.ICON_ERROR)
        return

    # User Canceled the Dialog
    if config is None:
        return

    return config

def _find_board() -> pcbnew.BOARD:
    '''
    Get the current active KiCad board.

    Args: None

    Returns: The active pcbnew.BOARD object if a board is open, otherwise None. Shows an error message box if no board is open.
    Raises: None (handles the case of no open board with a message box and returns None)
    '''

    board = pcbnew.GetBoard()
    if board is None:
        _message_box( "CoilForge Error", "No active board is open in KiCad.", wx.OK | wx.ICON_ERROR )
        return None
    return board

def _find_coil(board: Any = None) -> list[tuple[object, str]]:
    '''
    Find existing CoilForge groups on the board and return them along with their coil IDs.

    Args: board [pcbnew.BOARD] - The KiCad board object to search for CoilForge groups. If None, the current active board will be used.

    Returns: A list of tuples, where each tuple contains a CoilForge group object and its associated coil ID string.
    '''

    selected_groups = get_selected_coilforge_groups(board)

    target_group = None
    if selected_groups:
        target_group, coil_id = selected_groups[0]

        if len(selected_groups) > 1:
            wx.MessageBox(
                "Multiple CoilForge groups are selected. Only the first selected CoilForge coil will be edited.",
                "CoilForge Selection",
                wx.OK | wx.ICON_WARNING
            )
    else:
        coil_id = create_new_coil_id()

    return target_group, coil_id

def _config_summary(config: CoilConfig) -> str:
    """
    Build a user-facing summary of the accepted configuration.

    Args: config [CoilConfig] - The coil configuration data to summarize.

    Returns: A formatted string summarizing the coil configuration parameters.
    """
    return (
        f"Hole Radius:    {config.hole_radius} mm\n"
        f"Turns:          {config.turns}\n"
        f"Track Width:    {config.track_width} mm\n"
        f"Pitch:          {config.pitch} mm\n"
        f"Arc Resolution: {config.arc_resolution}\n"
        f"Center:         ({config.center_x}, {config.center_y}) mm\n"
        f"Angle:          {config.angle} deg\n"
        f"Layers:         {config.layers}\n"
        f"Direction:      {config.direction}\n"
        f"Net Name:       {config.net_name}\n"
        f"Via Size:       {config.via_size} mm"
    )

def _save_settings(coil_id: str, config: CoilConfig) -> None:
    '''
    Save coil settings to the current project.

    Args:   coil_id [str] - The unique identifier for the coil, used to save per-coil settings.
            config [CoilConfig] - The coil configuration data to save.

    Returns: None. Shows a warning message box if saving settings fails.
    '''

    # Build the output message based on the config summary and the result of saving settings
    output = f"{_config_summary(config)}\n\nSettings saved successfully."
    message_style = wx.OK | wx.ICON_INFORMATION

    # Save coil specific settings
    if not save_coil_settings(coil_id, config):
        output = f"{_config_summary(config)}\n\nWarning: Settings could not be saved."
        message_style = wx.OK | wx.ICON_WARNING

    # Update project settings
    if not save_settings(config):
        output = f"{_config_summary(config)}\n\nWarning: Project defaults could not be saved."
        message_style = wx.OK | wx.ICON_WARNING

    # Show the output from the CoilForge library in a message box to the user.
    _message_box("CoilForge Output", output, message_style)


def _generate_board(config: CoilConfig, board: pcbnew.BOARD, target_group: object | None, coil_id: str) -> None:
    '''
    Generate the coil geometry on the board using the CoilForge library.

    Args:   config [CoilConfig] - The validated coil configuration data.
            board [pcbnew.BOARD] - The KiCad board object to modify.
            target_group [object | None] - An existing CoilForge group to replace, or None to create a new group.
            coil_id [str] - The unique identifier for the coil, used for saving settings.

    Returns: None. Shows an error message box if coil generation fails.
    '''

    try:
        '''TODO: Implement the call to the CoilForge native library'''
        return

    except Exception as exc:
        # If there was an error calling the CoilForge native library, show an error message box to the user with the exception details.
        wx.MessageBox(
            f"Failed to call CoilForge native library.\n\n{exc}",
            "CoilForge Error",
            wx.OK | wx.ICON_ERROR
        )
        return


class CoilForgePlugin(pcbnew.ActionPlugin):
    '''
    A KiCad plugin that integrates the CoilForge coil generation library.
    '''

    def defaults(self) -> None:
        '''
        Set the default properties for the plugin, such as name, category, description, and toolbar button visibility.
        '''
        self.name = "CoilForge"                                     # The name of the plugin as it will appear in the KiCad UI  
        self.category = "Coil / Motor Tools"                        # The category under which the plugin will be listed in the Action Plugins menu
        self.description = "Open the CoilForge parameter dialog"    # A brief description of what the plugin does, shown in the Action Plugins menu
        self.show_toolbar_button = True                             # Whether to show a toolbar button for this plugin (True/False) 
        icon_path = _icon_path()
        self.icon_file_name = icon_path                              # The icon path used for the plugin toolbar button
        self.dark_icon_file_name = icon_path                         # The icon path used for the plugin toolbar button in dark mode

    def Run(self) -> None:
        '''
        The main entry point for the plugin when it is executed. This method prompts the user for
        coil configuration parameters, validates them, and then calls the native CoilForge library to generate the coil geometry.
        It also handles displaying the output or any errors in message boxes.
        '''

        # Get the current active board with failsafe
        board = _find_board()
        if board is None:
            return  # No board is open
        
        # Check for existing coil settings
        reconcile_settings(board)

        # Find selected CoilForge groups
        target_group, coil_id = _find_coil(board)

        # Load selected coil settings or the project settings
        initial_config = load_coil_settings(coil_id) or load_settings()

        # Prompt the user for coil config
        config = _prompt_config(initial_config)
        if config is None:
            return  # Dialog canceledd or validation error

        _generate_board(config, board, target_group, coil_id)
        
        # Call the CoilForge native library via the ctypes bridge

        # Generate the board geomtry
        
        '''
        nodes = generate_nodes(config)
        via_result = get_via_result(config)

        via_centers: list[tuple[float, float]] = []
        if config.via_size > 0.0 and len(nodes) >= 1:
            # Keep two terminal access vias for the current single-layer workflow:
            # one at the inner start and one at the trimmed outer tangent endpoint.
            via_centers = [nodes[0]]

            if via_result["has_via"]:
                via_centers.append(via_result["via_center"])
            else:
                via_centers.append(nodes[-1])

        if target_group is not None:
            delete_group_and_items(board, target_group)

        add_arcs_to_current_board(
            nodes=nodes,
            width_mm=config.track_width,
            layer_name="F.Cu",
            net_name=config.net_name,
            group_name=make_coilforge_group_name(coil_id),
            via_centers_mm=via_centers,
            via_diameter_mm=config.via_size,
            save_board=False,
        )
        '''

        # Save settings and show summary
        _save_settings(coil_id, config)

        # End of Run method
        return


