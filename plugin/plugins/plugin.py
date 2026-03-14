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
import pcbnew
import wx

# --- INTERNAL MODULES --- #
from .controller import prompt_for_config
from .bridge import run_ctypes_bridge


def format_config_summary(config):
    """
    Build a user-facing summary of the accepted configuration.

    Args: config [CoilConfig] - The coil configuration data to summarize.

    Returns: A formatted string summarizing the coil configuration parameters.
    """
    return (
        f"Hole Radius: {config.hole_radius} mm\n"
        f"Turns: {config.turns}\n"
        f"Track Width: {config.track_width} mm\n"
        f"Spacing: {config.spacing} mm\n"
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

    def defaults(self):
        '''
        Set the default properties for the plugin, such as name, category, description, and toolbar button visibility.
        '''
        self.name = "CoilForge"                                     # The name of the plugin as it will appear in the KiCad UI  
        self.category = "Coil / Motor Tools"                        # The category under which the plugin will be listed in the Action Plugins menu
        self.description = "Open the CoilForge parameter dialog"    # A brief description of what the plugin does, shown in the Action Plugins menu
        self.show_toolbar_button = True                             # Whether to show a toolbar button for this plugin (True/False) 
        self.icon_file_name = "icon.png"                            # The filename of the icon to use for the plugin's toolbar button
        self.dark_icon_file_name = "icon.png"                       # The filename of the icon to use for the plugin's toolbar button in dark mode

    def Run(self):
        '''
        The main entry point for the plugin when it is executed. This method prompts the user for
        coil configuration parameters, validates them, and then calls the native CoilForge library to generate the coil geometry.
        It also handles displaying the output or any errors in message boxes.
        '''
        try:
            # Prompt the user for coil configuration parameters using the dialog, and validate the input.
            submission = prompt_for_config(None)
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

            # If the settings were not saved successfully, append a warning to the output and change the message box style to show a warning icon.
            if not submission.settings_saved:
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


