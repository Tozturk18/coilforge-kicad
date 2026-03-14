import pcbnew
import wx

from .dialog_ui import CoilForgeDialog
from .settings import load_settings, save_settings
from .validator import parse_config


class CoilForgePlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "CoilForge"
        self.category = "Coil / Motor Tools"
        self.description = "Open the CoilForge parameter dialog"
        self.show_toolbar_button = True
        self.icon_file_name = ""
        self.dark_icon_file_name = ""

    def Run(self):
        initial_config = load_settings()
        dialog = CoilForgeDialog(None, initial_config=initial_config)

        try:
            result = dialog.ShowModal()

            if result != wx.ID_OK:
                return

            raw_values = dialog.get_raw_values()

            try:
                config = parse_config(raw_values)
            except ValueError as exc:
                wx.MessageBox(
                    str(exc),
                    "Invalid Input",
                    wx.OK | wx.ICON_ERROR
                )
                return

            save_settings(config)

            summary = (
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

            wx.MessageBox(
                summary,
                "CoilForge Parameters",
                wx.OK | wx.ICON_INFORMATION
            )

        finally:
            dialog.Destroy()


