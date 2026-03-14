from dataclasses import dataclass


@dataclass
class CoilConfig:
    hole_radius_mm: float
    turns: float
    track_width_mm: float
    spacing_mm: float
    center_x_mm: float
    center_y_mm: float
    angle_deg: float
    layers: int
    direction: str
    net_name: str
    via_size_mm: float