import subprocess
from pathlib import Path


def get_engine_path():
    """
    Resolve the path to the development C executable.
    Adjust later for packaged/plugin-installed builds.

        
    """
    file_root = Path(__file__).resolve().parents[0]
    return file_root / "bin" / "coilforge_engine"


def run_engine(config):
    engine_path = get_engine_path()

    cmd = [
        str(engine_path),
        "-r", str(config.hole_radius),
        "-t", str(config.turns),
        "-w", str(config.track_width),
        "-s", str(config.spacing),
        "-x", str(config.center_x),
        "-y", str(config.center_y),
        "-a", str(config.angle),
        "-l", str(config.layers),
        "-d", str(config.direction),
        "-n", str(config.net_name),
        "-v", str(config.via_size),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )

    return result