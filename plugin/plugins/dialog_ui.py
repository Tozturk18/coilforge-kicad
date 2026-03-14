import wx


DEFAULT_VALUES = {
    "hole_radius_mm": 0.0,
    "turns": 10.0,
    "track_width_mm": 0.25,
    "spacing_mm": 0.20,
    "center_x_mm": 0.0,
    "center_y_mm": 0.0,
    "angle_deg": 0.0,
    "layers": 2,
    "net_name": "COIL_NET",
    "via_size_mm": 0.45,
    "direction": "CW",
}

TEXT_FIELD_SPECS = (
    ("Geometry", "hole_radius_mm", "Hole Radius (mm)"),
    ("Geometry", "turns", "Number of Coil Turns"),
    ("Geometry", "track_width_mm", "Track Width (mm)"),
    ("Geometry", "spacing_mm", "Spacing (mm)"),
    ("Placement", "center_x_mm", "Center X Position (mm)"),
    ("Placement", "center_y_mm", "Center Y Position (mm)"),
    ("Placement", "angle_deg", "Angle (deg)"),
    ("Routing", "layers", "Layers"),
    ("Routing", "via_size_mm", "Via Size (mm)"),
    ("Connectivity", "net_name", "Net Name"),
)


class CoilForgeDialog(wx.Dialog):
    def __init__(self, parent=None, initial_config=None):
        super().__init__(
            parent,
            title="CoilForge KiCad",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )

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
        add_text_field(geometry_grid, "hole_radius_mm", "Hole Radius (mm)", defaults["hole_radius_mm"])
        add_text_field(geometry_grid, "turns", "Number of Coil Turns", defaults["turns"])
        add_text_field(geometry_grid, "track_width_mm", "Track Width (mm)", defaults["track_width_mm"])
        add_text_field(geometry_grid, "spacing_mm", "Spacing (mm)", defaults["spacing_mm"])

        panel_sizer.Add(geometry_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # ---------- Placement Section ----------
        placement_sizer, placement_grid = make_section("Placement")
        add_text_field(placement_grid, "center_x_mm", "Center X Position (mm)", defaults["center_x_mm"])
        add_text_field(placement_grid, "center_y_mm", "Center Y Position (mm)", defaults["center_y_mm"])
        add_text_field(placement_grid, "angle_deg", "Angle (deg)", defaults["angle_deg"])

        panel_sizer.Add(placement_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # ---------- Routing Section ----------
        routing_sizer, routing_grid = make_section("Routing")
        add_text_field(routing_grid, "layers", "Layers", defaults["layers"])
        add_text_field(routing_grid, "via_size_mm", "Via Size (mm)", defaults["via_size_mm"])

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

    def _build_defaults(self, initial_config):
        defaults = DEFAULT_VALUES.copy()

        if initial_config is None:
            return defaults

        for field_name in defaults:
            defaults[field_name] = getattr(initial_config, field_name)

        return defaults

    def get_input_values(self):
        values = {field_name: ctrl.GetValue() for field_name, ctrl in self.fields.items()}
        values["direction"] = self.direction.GetStringSelection()
        return values

    def get_raw_values(self):
        """
        Compatibility alias for earlier code paths.
        """
        return self.get_input_values()