import wx


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
        def add_text_field(grid, label_text, default_value):
            label = wx.StaticText(panel, label=label_text)
            field = wx.TextCtrl(panel, value=str(default_value))

            self.fields[label_text] = field

            grid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
            grid.Add(field, 1, wx.EXPAND | wx.ALL, 4)

        def make_section(title):
            box = wx.StaticBox(panel, label=title)
            box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

            grid = wx.FlexGridSizer(rows=0, cols=2, hgap=10, vgap=2)
            grid.AddGrowableCol(1, 1)

            box_sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 8)
            return box_sizer, grid

        # Resolve defaults
        defaults = {
            "Hole Radius (mm)": 0.0,
            "Number of Coil Turns": 10.0,
            "Track Width (mm)": 0.25,
            "Spacing (mm)": 0.20,
            "Center X Position (mm)": 0.0,
            "Center Y Position (mm)": 0.0,
            "Angle (deg)": 0.0,
            "Layers": 2,
            "Net Name": "COIL_NET",
            "Via Size (mm)": 0.45,
            "Direction": "CW",
        }

        if initial_config is not None:
            defaults.update({
                "Hole Radius (mm)": initial_config.hole_radius_mm,
                "Number of Coil Turns": initial_config.turns,
                "Track Width (mm)": initial_config.track_width_mm,
                "Spacing (mm)": initial_config.spacing_mm,
                "Center X Position (mm)": initial_config.center_x_mm,
                "Center Y Position (mm)": initial_config.center_y_mm,
                "Angle (deg)": initial_config.angle_deg,
                "Layers": initial_config.layers,
                "Net Name": initial_config.net_name,
                "Via Size (mm)": initial_config.via_size_mm,
                "Direction": initial_config.direction,
            })

        # ---------- Geometry Section ----------
        geometry_sizer, geometry_grid = make_section("Geometry")
        add_text_field(geometry_grid, "Hole Radius (mm)", defaults["Hole Radius (mm)"])
        add_text_field(geometry_grid, "Number of Coil Turns", defaults["Number of Coil Turns"])
        add_text_field(geometry_grid, "Track Width (mm)", defaults["Track Width (mm)"])
        add_text_field(geometry_grid, "Spacing (mm)", defaults["Spacing (mm)"])

        panel_sizer.Add(geometry_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # ---------- Placement Section ----------
        placement_sizer, placement_grid = make_section("Placement")
        add_text_field(placement_grid, "Center X Position (mm)", defaults["Center X Position (mm)"])
        add_text_field(placement_grid, "Center Y Position (mm)", defaults["Center Y Position (mm)"])
        add_text_field(placement_grid, "Angle (deg)", defaults["Angle (deg)"])

        panel_sizer.Add(placement_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # ---------- Routing Section ----------
        routing_sizer, routing_grid = make_section("Routing")
        add_text_field(routing_grid, "Layers", defaults["Layers"])
        add_text_field(routing_grid, "Via Size (mm)", defaults["Via Size (mm)"])

        direction_label = wx.StaticText(panel, label="Direction")
        self.direction = wx.RadioBox(
            panel,
            label="",
            choices=["CW", "CCW"],
            majorDimension=1,
            style=wx.RA_SPECIFY_ROWS
        )
        self.direction.SetStringSelection(defaults["Direction"])

        routing_grid.Add(direction_label, 0, wx.ALIGN_TOP | wx.ALL, 4)
        routing_grid.Add(self.direction, 1, wx.EXPAND | wx.ALL, 4)

        panel_sizer.Add(routing_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 15)

        # ---------- Connectivity Section ----------
        connectivity_sizer, connectivity_grid = make_section("Connectivity")
        add_text_field(connectivity_grid, "Net Name", defaults["Net Name"])

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

    def get_raw_values(self):
        values = {label: ctrl.GetValue() for label, ctrl in self.fields.items()}
        values["Direction"] = self.direction.GetStringSelection()
        return values