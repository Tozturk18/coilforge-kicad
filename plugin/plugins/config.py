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