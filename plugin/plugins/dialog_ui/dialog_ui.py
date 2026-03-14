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
    "pitch": 0.45,
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
    ("Geometry", "pitch", "Pitch (mm)"),
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
        self._linked_field_source = "pitch"

        # --- Main dialog sizer ---
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Main content panel ---
        panel = wx.Panel(self)
        self._panel = panel
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        sections_grid = wx.GridBagSizer(hgap=12, vgap=12)
        self._sections_hgap = 12
        self._sections_outer_padding = 12
        sections_grid.AddGrowableCol(0, 1)
        sections_grid.AddGrowableCol(1, 1)
        sections_grid.AddGrowableRow(0, 1)
        self._warning_wrap_width = 250
        self._warning_min_height = 42

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

            box_sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 8)
            return box_sizer, grid

        def wrap_section(section_sizer):
            wrapper = wx.BoxSizer(wx.VERTICAL)
            wrapper.Add(section_sizer, 1, wx.EXPAND | wx.ALL, 6)
            return wrapper

        defaults = self._build_defaults(initial_config)

        # ---------- Geometry Section ----------
        geometry_sizer, geometry_grid = make_section("Geometry")
        add_text_field(geometry_grid, "hole_radius", "Hole Radius (mm)", defaults["hole_radius"])
        add_text_field(geometry_grid, "turns", "Number of Coil Turns", defaults["turns"])
        add_text_field(geometry_grid, "track_width", "Track Width (mm)", defaults["track_width"])

        spacing_pitch_sizer = wx.BoxSizer(wx.HORIZONTAL)

        spacing_sizer = wx.BoxSizer(wx.VERTICAL)
        spacing_label = wx.StaticText(panel, label="Spacing (mm)")
        spacing_field = wx.TextCtrl(panel, value=str(defaults["spacing"]))
        self.fields["spacing"] = spacing_field
        self._normal_field_bg = spacing_field.GetBackgroundColour()
        self._warning_field_bg = wx.Colour(255, 235, 235)
        spacing_sizer.Add(spacing_label, 0, wx.BOTTOM, 4)
        spacing_sizer.Add(spacing_field, 0, wx.EXPAND)

        pitch_sizer = wx.BoxSizer(wx.VERTICAL)
        pitch_label = wx.StaticText(panel, label="Pitch (mm)")
        pitch_field = wx.TextCtrl(panel, value=str(defaults["pitch"]))
        self.fields["pitch"] = pitch_field
        pitch_sizer.Add(pitch_label, 0, wx.BOTTOM, 4)
        pitch_sizer.Add(pitch_field, 0, wx.EXPAND)

        spacing_pitch_sizer.Add(spacing_sizer, 1, wx.EXPAND | wx.RIGHT, 6)
        spacing_pitch_sizer.Add(pitch_sizer, 1, wx.EXPAND | wx.LEFT, 6)
        geometry_sizer.Add(spacing_pitch_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.pitch_spacing_warning = wx.StaticText(panel, label="")
        self.pitch_spacing_warning.SetForegroundColour(wx.Colour(180, 0, 0))
        self.pitch_spacing_warning.Wrap(self._warning_wrap_width)
        self.pitch_spacing_warning.SetMinSize((self._warning_wrap_width, self._warning_min_height))
        geometry_sizer.Add(self.pitch_spacing_warning, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.fields["track_width"].Bind(wx.EVT_TEXT, self._on_track_width_changed)
        self.fields["spacing"].Bind(wx.EVT_TEXT, self._on_spacing_changed)
        self.fields["pitch"].Bind(wx.EVT_TEXT, self._on_pitch_changed)

        # ---------- Placement Section ----------
        placement_sizer, placement_grid = make_section("Placement")
        add_text_field(placement_grid, "center_x", "Center X Position (mm)", defaults["center_x"])
        add_text_field(placement_grid, "center_y", "Center Y Position (mm)", defaults["center_y"])
        add_text_field(placement_grid, "angle", "Angle (deg)", defaults["angle"])

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

        # ---------- Connectivity Section ----------
        connectivity_sizer, connectivity_grid = make_section("Connectivity")
        add_text_field(connectivity_grid, "net_name", "Net Name", defaults["net_name"])

        geometry_wrap = wrap_section(geometry_sizer)
        placement_wrap = wrap_section(placement_sizer)
        routing_wrap = wrap_section(routing_sizer)
        connectivity_wrap = wrap_section(connectivity_sizer)

        self._left_column_sections = (geometry_wrap, routing_wrap)
        self._right_column_sections = (placement_wrap, connectivity_wrap)

        sections_grid.Add(geometry_wrap, pos=(0, 0), flag=wx.EXPAND | wx.ALIGN_TOP)
        sections_grid.Add(placement_wrap, pos=(0, 1), flag=wx.EXPAND | wx.ALIGN_TOP)
        sections_grid.Add(routing_wrap, pos=(1, 0), flag=wx.EXPAND | wx.ALIGN_TOP)
        sections_grid.Add(connectivity_wrap, pos=(1, 1), flag=wx.EXPAND | wx.ALIGN_TOP)

        panel_sizer.Add(sections_grid, 1, wx.EXPAND | wx.ALL, 12)

        panel.SetSizer(panel_sizer)

        # Add panel to dialog
        main_sizer.Add(panel, 1, wx.EXPAND)

        # Buttons
        button_sizer = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
        if button_sizer:
            main_sizer.Add(button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        self.SetSizer(main_sizer)
        self.SetSize((700, 550))
        self.SetMinSize((480, 460))
        self.Bind(wx.EVT_SIZE, self._on_dialog_resized)
        self._sync_column_widths()
        self._update_pitch_spacing_warning()
        self.Layout()
        self.Centre()

    def _sync_column_widths(self) -> None:
        panel_width = self._panel.GetClientSize().GetWidth()
        if panel_width <= 0:
            return

        available_width = (
            panel_width
            - (2 * self._sections_outer_padding)
            - self._sections_hgap
        )
        column_width = max(150, available_width // 2)

        for section in self._left_column_sections:
            section.SetMinSize((column_width, -1))

        for section in self._right_column_sections:
            section.SetMinSize((column_width, -1))

    def _on_dialog_resized(self, event: wx.SizeEvent) -> None:
        self._sync_column_widths()
        event.Skip()

    def _build_defaults(self, initial_config: Optional[CoilConfig]) -> dict[str, Any]:
        defaults = DEFAULT_VALUES.copy()

        if initial_config is None:
            defaults["spacing"] = defaults["pitch"] - defaults["track_width"]
            return defaults

        for field_name in defaults:
            defaults[field_name] = getattr(initial_config, field_name)

        defaults["spacing"] = defaults["pitch"] - defaults["track_width"]
        return defaults

    def _parse_float_field(self, field_name: str) -> Optional[float]:
        value = self.fields[field_name].GetValue().strip()

        if not value:
            return None

        try:
            return float(value)
        except ValueError:
            return None

    def _set_field_value(self, field_name: str, value: float) -> None:
        self.fields[field_name].ChangeValue(f"{value:g}")

    def _update_pitch_spacing_warning(self) -> None:
        def fit_warning_height() -> None:
            self.pitch_spacing_warning.InvalidateBestSize()
            best_height = self.pitch_spacing_warning.GetBestSize().GetHeight()
            self.pitch_spacing_warning.SetMinSize(
                (self._warning_wrap_width, max(self._warning_min_height, best_height))
            )

        spacing = self._parse_float_field("spacing")
        has_warning = spacing is not None and spacing <= 0
        has_danger = spacing is not None and 0 < spacing < 0.0762

        field_bg = self._warning_field_bg if has_warning else self._normal_field_bg
        self.fields["spacing"].SetBackgroundColour(field_bg)
        self.fields["pitch"].SetBackgroundColour(field_bg)
        self.fields["spacing"].Refresh()
        self.fields["pitch"].Refresh()

        if has_warning:
            self.pitch_spacing_warning.SetLabel(
                "Warning: Pitch is smaller than track width, so adjacent traces overlap."
            )
            self.pitch_spacing_warning.Wrap(self._warning_wrap_width)
            fit_warning_height()
        elif has_danger:
            self.pitch_spacing_warning.SetLabel(
                "Danger: Pitch is less than 0.0762 mm (3 mil), which may cause manufacturing issues."
            )
            self.pitch_spacing_warning.Wrap(self._warning_wrap_width)
            fit_warning_height()
        else:
            self.pitch_spacing_warning.SetLabel(" ")
            self.pitch_spacing_warning.Wrap(self._warning_wrap_width)
            self.pitch_spacing_warning.SetMinSize((self._warning_wrap_width, self._warning_min_height))

    def _sync_pitch_from_spacing(self) -> None:
        spacing = self._parse_float_field("spacing")
        track_width = self._parse_float_field("track_width")

        if spacing is None or track_width is None:
            return

        self._set_field_value("pitch", spacing + track_width)

    def _sync_spacing_from_pitch(self) -> None:
        pitch = self._parse_float_field("pitch")
        track_width = self._parse_float_field("track_width")

        if pitch is None or track_width is None:
            return

        self._set_field_value("spacing", pitch - track_width)

    def _on_spacing_changed(self, event: wx.CommandEvent) -> None:
        self._linked_field_source = "spacing"
        self._sync_pitch_from_spacing()
        self._update_pitch_spacing_warning()
        self.Layout()
        event.Skip()

    def _on_pitch_changed(self, event: wx.CommandEvent) -> None:
        self._linked_field_source = "pitch"
        self._sync_spacing_from_pitch()
        self._update_pitch_spacing_warning()
        self.Layout()
        event.Skip()

    def _on_track_width_changed(self, event: wx.CommandEvent) -> None:
        if self._linked_field_source == "pitch":
            self._sync_spacing_from_pitch()
        else:
            self._sync_pitch_from_spacing()

        self._update_pitch_spacing_warning()
        self.Layout()
        event.Skip()

    def get_input_values(self) -> dict[str, str]:
        values = {
            field_name: ctrl.GetValue()
            for field_name, ctrl in self.fields.items()
            if field_name != "spacing"
        }
        values["direction"] = self.direction.GetStringSelection()
        return values

    def get_raw_values(self) -> dict[str, str]:
        """
        Compatibility alias for earlier code paths.
        """
        return self.get_input_values()