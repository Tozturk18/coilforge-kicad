import pcbnew
import wx

from .controller import prompt_for_config


def format_config_summary(config):
    """
    Build a user-facing summary of the accepted configuration.
    """
    return (
        f"Hole Radius: {config.hole_radius_mm} mm\n"
        f"Turns: {config.turns}\n"
        f"Track Width: {config.track_width_mm} mm\n"
        f"Spacing: {config.spacing_mm} mm\n"
        f"Center: ({config.center_x_mm}, {config.center_y_mm}) mm\n"
        f"Angle: {config.angle_deg} deg\n"
        f"Layers: {config.layers}\n"
        f"Direction: {config.direction}\n"
        f"Net Name: {config.net_name}\n"
        f"Via Size: {config.via_size_mm} mm"
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

        summary = format_config_summary(submission.config)
        message_style = wx.OK | wx.ICON_INFORMATION

        if not submission.settings_saved:
            summary = f"{summary}\n\nWarning: Settings could not be saved."
            message_style = wx.OK | wx.ICON_WARNING

        wx.MessageBox(
            summary,
            "CoilForge Parameters",
            message_style
        )


