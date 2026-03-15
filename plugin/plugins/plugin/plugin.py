'''
@ filename: plugin.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2024
@ license:  MIT License
@ description: This module defines the main entry point for the CoilForge plugin, 
    which integrates the dialog UI and the bridge to the native library. 
    It implements the CoilForgePlugin class that inherits from pcbnew.ActionPlugin, 
    allowing it to be registered as a plugin action in KiCad. The plugin prompts the user
    for coil configuration parameters, validates them, and then calls the native CoilForge 
    library to generate the coil geometry, displaying the output or any errors in message boxes.
'''

# --- IMPORTS --- #
from pathlib import Path

import pcbnew
import wx

# --- INTERNAL MODULES --- #
from ..config.config import CoilConfig
from ..controller.controller import prompt_for_config
from ..bridge.bridge import run_ctypes_bridge, generate_nodes
from ..arcs.arcs import (
    add_arcs_to_current_board,
    delete_group_and_items,
    get_selected_coilforge_groups,
    make_coilforge_group_name,
)
from ..settings.settings import create_new_coil_id, load_coil_settings, load_settings, save_coil_settings


def _resolve_icon_path() -> str:
    """Resolve plugin icon path for both dev and installed KiCad layouts."""
    module_paths = [Path(__file__).absolute(), Path(__file__).resolve()]
    package_roots = []

    for module_path in module_paths:
        package_root = module_path.parents[1]
        if package_root not in package_roots:
            package_roots.append(package_root)

    candidates = []
    for package_root in package_roots:
        module_dir = package_root / "plugin"
        resource_dir = package_root.parent / "resources"
        plugin_id_resource_dir = package_root.parent.parent / "resources" / package_root.name

        candidates.extend([
            module_dir / "icon.png",
            package_root / "icon.png",
            resource_dir / "icon.png",
            plugin_id_resource_dir / "icon.png",
        ])

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    # Fallback keeps behavior deterministic even if icon is missing.
    return "icon.png"


def format_config_summary(config: CoilConfig) -> str:
    """
    Build a user-facing summary of the accepted configuration.

    Args: config [CoilConfig] - The coil configuration data to summarize.

    Returns: A formatted string summarizing the coil configuration parameters.
    """
    return (
        f"Hole Radius: {config.hole_radius} mm\n"
        f"Turns: {config.turns}\n"
        f"Track Width: {config.track_width} mm\n"
        f"Pitch: {config.pitch} mm\n"
        f"Arc Resolution: {config.arc_resolution}\n"
        f"Center: ({config.center_x}, {config.center_y}) mm\n"
        f"Angle: {config.angle} deg\n"
        f"Layers: {config.layers}\n"
        f"Direction: {config.direction}\n"
        f"Net Name: {config.net_name}\n"
        f"Via Size: {config.via_size} mm"
    )


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
        icon_path = _resolve_icon_path()
        self.icon_file_name = icon_path                              # The icon path used for the plugin toolbar button
        self.dark_icon_file_name = icon_path                         # The icon path used for the plugin toolbar button in dark mode

    def Run(self) -> None:
        '''
        The main entry point for the plugin when it is executed. This method prompts the user for
        coil configuration parameters, validates them, and then calls the native CoilForge library to generate the coil geometry.
        It also handles displaying the output or any errors in message boxes.
        '''
        board = pcbnew.GetBoard()
        if board is None:
            wx.MessageBox(
                "No active board is open in KiCad.",
                "CoilForge Error",
                wx.OK | wx.ICON_ERROR
            )
            return

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

        initial_config = load_coil_settings(coil_id) or load_settings()

        try:
            # Prompt the user for coil configuration parameters using the dialog, and validate the input.
            submission = prompt_for_config(None, initial_config=initial_config)
        except ValueError as exc:
            # If there was a validation error (e.g., missing or invalid input), show an error message box to the user.
            wx.MessageBox(
                str(exc),
                "Invalid Input",
                wx.OK | wx.ICON_ERROR
            )
            return

        # If the user canceled the dialog (submission is None), simply return without doing anything.
        if submission is None:
            return
        
        try:
            # Call the CoilForge native library via the ctypes bridge with the validated configuration, and capture the output.
            output = run_ctypes_bridge(submission.config)
            message_style = wx.OK | wx.ICON_INFORMATION

            nodes = generate_nodes(submission.config)

            if target_group is not None:
                delete_group_and_items(board, target_group)

            add_arcs_to_current_board(
                nodes=nodes,
                width_mm=submission.config.track_width,
                layer_name="F.Cu",
                net_name=submission.config.net_name,
                group_name=make_coilforge_group_name(coil_id),
                save_board=False,
            )

            if not save_coil_settings(coil_id, submission.config):
                output = f"{output}\n\nWarning: Settings could not be saved."
                message_style = wx.OK | wx.ICON_WARNING

            # Show the output from the CoilForge library in a message box to the user.
            wx.MessageBox(
                output,
                "CoilForge Output",
                message_style
            )

        except Exception as exc:
            # If there was an error calling the CoilForge native library, show an error message box to the user with the exception details.
            wx.MessageBox(
                f"Failed to call CoilForge native library.\n\n{exc}",
                "CoilForge Error",
                wx.OK | wx.ICON_ERROR
            )
            return


