'''
@ filename: config.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2024
@ license:  MIT License
@ description: This module defines the CoilConfig dataclass and functions for
    loading/saving user settings and parsing/validating dialog input values.
'''

from dataclasses import dataclass


@dataclass
class CoilConfig:
    hole_radius: float
    turns: float
    track_width: float
    spacing: float
    center_x: float
    center_y: float
    angle: float
    layers: int
    direction: str
    net_name: str
    via_size: float