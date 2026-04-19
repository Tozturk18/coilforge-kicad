#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File:       //plugin/plugins/config/config.py
Date:       2026-03-13
Author:     Ozgur Tuna Ozturk
Contact:    [@Tozturk18](tunaozturk2001@hotmail.com)
Last Mod:   2026-03-15
Version:    0.1.0
License:    MIT License
Description:
    This module defines the CoilConfig dataclass and functions for
    loading/saving user settings and parsing/validating dialog input values.
"""

from dataclasses import (
    dataclass           # Data structures holding coil configuration parameters
)

@dataclass
class CoilConfig:
    '''
    Data class representing the coil configuration parameters.
    '''
    hole_radius    : float  # [mm]  Inner Hole Radius
    turns          : float  # [#]   Number of Turns
    track_width    : float  # [mm]  PCB Track Width
    pitch          : float  # [mm]  PCB Pitch
    arc_resolution : int    # [#]   Number of arc segments per turn
    center_x       : float  # [mm]  X-coordinate of the coil center
    center_y       : float  # [mm]  Y-coordinate of the coil center
    angle          : float  # [deg] Orientation angle of the coil
    layers         : int    # [#]   Number of copper layers
    direction      : str    # [str] Direction of the coil winding
    net_name       : str    # [str] Name of the electrical net
    via_size       : float  # [mm]  Via Diameter
