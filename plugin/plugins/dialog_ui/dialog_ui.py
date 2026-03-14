'''
@ filename: dialog_ui.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2024
@ license:  MIT License
@ description: This module implements the CoilForgeDialog class,
    which defines the user interface for the CoilForge plugin using wxPython.
    This dialog implementation is designed to be straightforward and user-friendly, 
    with clear sections for different types of parameters and appropriate default values.
'''

# --- IMPORTS --- #
from typing import Any, Optional

import wx

from ..config.config import CoilConfig

# --- CLASSES & FUNCTIONS --- #

# Default values for the dialog fields, used when no initial config is provided
DEFAULT_VALUES = {
    "hole_radius": 0.0,
    "turns": 10.0,
    "track_width": 0.25,
    "spacing": 0.20,
    "center_x": 0.0,
    "center_y": 0.0,
    "angle": 0.0,
    "layers": 2,
    "net_name": "COIL_NET",
    "via_size": 0.45,
    "direction": "CW",
}

# The TEXT_FIELD_SPECS tuple defines the structure of the dialog fields, including their section, key, and label.
TEXT_FIELD_SPECS = (
    ("Geometry", "hole_radius", "Hole Radius (mm)"),
    ("Geometry", "turns", "Number of Coil Turns"),
    ("Geometry", "track_width", "Track Width (mm)"),
    ("Geometry", "spacing", "Spacing (mm)"),
    ("Placement", "center_x", "Center X Position (mm)"),
    ("Placement", "center_y", "Center Y Position (mm)"),
    ("Placement", "angle", "Angle (deg)"),
    ("Routing", "layers", "Layers"),
    ("Routing", "via_size", "Via Size (mm)"),
    ("Connectivity", "net_name", "Net Name"),
)


class CoilForgeDialog(wx.Dialog):
    '''
    A dialog for configuring CoilForge parameters.

    Args: parent [wx.Window] - The parent window for this dialog (can be None).

    Returns: An instance of CoilForgeDialog that can be shown modally to the user.
    '''

    def __init__(self, parent: Optional[wx.Window] = None, initial_config: Optional[CoilConfig] = None) -> None:
        '''
        Initialize the dialog with input fields for coil configuration.
        '''

        # Call the base class constructor to create the dialog window
        super().__init__(
            parent,
            title="CoilForge KiCad",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

        # A dictionary to hold references to the input fields, keyed by their config field names
        self.fields = {}

        # --- Main dialog sizer ---
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Main content panel ---
        panel = wx.Panel(self)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # ---------- Helper ----------
        def add_text_field(grid, field_key, label_text, default_value):
            label = wx.StaticText(panel, label=label_text)
            field = wx.TextCtrl(panel, value=str(default_value))

            self.fields[field_key] = field

            grid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
            grid.Add(field, 1, wx.EXPAND | wx.ALL, 4)

        def make_section(title):
            box = wx.StaticBox(panel, label=title)
            box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

            grid = wx.FlexGridSizer(rows=0, cols=2, hgap=10, vgap=2)
            grid.AddGrowableCol(1, 1)

            box_sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 8)
            return box_sizer, grid

        defaults = self._build_defaults(initial_config)

        # ---------- Geometry Section ----------
        geometry_sizer, geometry_grid = make_section("Geometry")
        add_text_field(geometry_grid, "hole_radius", "Hole Radius (mm)", defaults["hole_radius"])
        add_text_field(geometry_grid, "turns", "Number of Coil Turns", defaults["turns"])
        add_text_field(geometry_grid, "track_width", "Track Width (mm)", defaults["track_width"])
        add_text_field(geometry_grid, "spacing", "Spacing (mm)", defaults["spacing"])

        panel_sizer.Add(geometry_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # ---------- Placement Section ----------
        placement_sizer, placement_grid = make_section("Placement")
        add_text_field(placement_grid, "center_x", "Center X Position (mm)", defaults["center_x"])
        add_text_field(placement_grid, "center_y", "Center Y Position (mm)", defaults["center_y"])
        add_text_field(placement_grid, "angle", "Angle (deg)", defaults["angle"])

        panel_sizer.Add(placement_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # ---------- Routing Section ----------
        routing_sizer, routing_grid = make_section("Routing")
        add_text_field(routing_grid, "layers", "Layers", defaults["layers"])
        add_text_field(routing_grid, "via_size", "Via Size (mm)", defaults["via_size"])

        direction_label = wx.StaticText(panel, label="Direction")
        self.direction = wx.RadioBox(
            panel,
            label="",
            choices=["CW", "CCW"],
            majorDimension=1,
            style=wx.RA_SPECIFY_ROWS
        )
        self.direction.SetStringSelection(defaults["direction"])

        routing_grid.Add(direction_label, 0, wx.ALIGN_TOP | wx.ALL, 4)
        routing_grid.Add(self.direction, 1, wx.EXPAND | wx.ALL, 4)

        panel_sizer.Add(routing_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)

        # ---------- Connectivity Section ----------
        connectivity_sizer, connectivity_grid = make_section("Connectivity")
        add_text_field(connectivity_grid, "net_name", "Net Name", defaults["net_name"])

        panel_sizer.Add(connectivity_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 15)

        panel.SetSizer(panel_sizer)

        # Add panel to dialog
        main_sizer.Add(panel, 1, wx.EXPAND)

        # Buttons
        button_sizer = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        if button_sizer:
            main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(main_sizer)
        self.SetSize((520, 700))
        self.SetMinSize((480, 560))
        self.Layout()
        self.Centre()

    def _build_defaults(self, initial_config: Optional[CoilConfig]) -> dict[str, Any]:
        defaults = DEFAULT_VALUES.copy()

        if initial_config is None:
            return defaults

        for field_name in defaults:
            defaults[field_name] = getattr(initial_config, field_name)

        return defaults

    def get_input_values(self) -> dict[str, str]:
        values = {field_name: ctrl.GetValue() for field_name, ctrl in self.fields.items()}
        values["direction"] = self.direction.GetStringSelection()
        return values

    def get_raw_values(self) -> dict[str, str]:
        """
        Compatibility alias for earlier code paths.
        """
        return self.get_input_values()