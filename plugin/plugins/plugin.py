import pcbnew
import wx

from .controller import prompt_for_config
from .bridge import run_engine


def format_config_summary(config):
    """
    Build a user-facing summary of the accepted configuration.
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
    def defaults(self):
        self.name = "CoilForge"
        self.category = "Coil / Motor Tools"
        self.description = "Open the CoilForge parameter dialog"
        self.show_toolbar_button = True
        self.icon_file_name = ""
        self.dark_icon_file_name = ""

    def Run(self):
        try:
            submission = prompt_for_config(None)
        except ValueError as exc:
            wx.MessageBox(
                str(exc),
                "Invalid Input",
                wx.OK | wx.ICON_ERROR
            )
            return

        if submission is None:
            return

        result = run_engine(submission.config)
        message_style = wx.OK | wx.ICON_INFORMATION

        if not submission.settings_saved:
            result.stdout = f"{result.stdout}\n\nWarning: Settings could not be saved."
            message_style = wx.OK | wx.ICON_WARNING

        if result.returncode != 0:
            wx.MessageBox(
                f"C engine failed.\n\n{result.stderr}",
                "CoilForge Error",
                wx.OK | wx.ICON_ERROR
            )
            return

        wx.MessageBox(
            result.stdout,
            "CoilForge Parameters",
            message_style
        )


