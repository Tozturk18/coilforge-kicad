'''
@ filename: bridge.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2026
@ license:  MIT License
@ description: This module implements the bridge between the Python plugin code
    and the native CoilForge library.
'''

# --- IMPORTS --- #
import ctypes
import platform
from pathlib import Path

from ..config.config import CoilConfig

# --- CONSTANTS --- #
OUTPUT_BUFFER_SIZE = 2048

# --- CLASSES & FUNCTIONS --- #

class CoilForgeBridgeError(RuntimeError):
    '''
    Custom exception for errors related to the CoilForge bridge.
    '''
    pass


class CoilForgeConfig(ctypes.Structure):
    '''
    ctypes structure matching the CoilForgeConfig C struct expected by the
    native library.
    '''
    _fields_ = [
        ("hole_radius",   ctypes.c_double),      # [mm]
        ("turns",         ctypes.c_double),      # [#]
        ("track_width",   ctypes.c_double),      # [mm]
        ("pitch",         ctypes.c_double),      # [mm]
        ("arc_resolution",ctypes.c_int),         # [#]
        ("center_x",      ctypes.c_double),      # [mm]
        ("center_y",      ctypes.c_double),      # [mm]
        ("angle",         ctypes.c_double),      # [deg]
        ("layers",        ctypes.c_int),         # [#]
        ("direction",     ctypes.c_int),         # [-1/1]
        ("via_size",      ctypes.c_double),      # [mm]
        ("net_name",      ctypes.c_char * 128),  # UTF-8 string
    ]


class CoilForgeVec2(ctypes.Structure):
    '''
    ctypes structure matching the public CoilForgeVec2 C struct returned
    by the native library.
    '''
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
    ]


def _get_library_name() -> Path:
    '''
    Get the appropriate library name according to the current platform/OS.
    '''
    system = platform.system()

    if system == "Darwin":
        return Path("macOS") / "libcoilforge.dylib"
    if system == "Windows":
        return Path("Windows") / "coilforge.dll"
    if system == "Linux":
        return Path("Linux") / "libcoilforge.so"

    raise CoilForgeBridgeError(f"Unsupported platform: {system}")


def _get_library_path() -> Path:
    '''
    Get the full file path to the CoilForge native library based on the
    current platform.
    '''
    file_root = Path(__file__).resolve().parents[1]
    return file_root / "bin" / _get_library_name()


def load_library() -> ctypes.CDLL:
    '''
    Load the CoilForge native library using ctypes and configure the function
    signatures required by the plugin.
    '''
    lib_path = _get_library_path()

    try:
        lib = ctypes.CDLL(str(lib_path))
    except OSError as exc:
        raise CoilForgeBridgeError(
            f"Failed to load CoilForge native library from {lib_path}: {exc}"
        ) from exc

    # ------------------------------------------------------------------
    # coilforge_process_config(const CoilForgeConfig*, char*, size_t) -> int
    # ------------------------------------------------------------------
    lib.coilforge_process_config.argtypes = [
        ctypes.POINTER(CoilForgeConfig),
        ctypes.POINTER(ctypes.c_char),
        ctypes.c_size_t,
    ]
    lib.coilforge_process_config.restype = ctypes.c_int

    # ------------------------------------------------------------
    # coilforge_get_node_count(const CoilForgeConfig*, int*) -> int
    # ------------------------------------------------------------
    lib.coilforge_get_node_count.argtypes = [
        ctypes.POINTER(CoilForgeConfig),
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.coilforge_get_node_count.restype = ctypes.c_int

    # --------------------------------------------------------------------------
    # coilforge_generate_nodes(const CoilForgeConfig*, CoilForgeVec2*, int, int*)
    # --------------------------------------------------------------------------
    lib.coilforge_generate_nodes.argtypes = [
        ctypes.POINTER(CoilForgeConfig),
        ctypes.POINTER(CoilForgeVec2),
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
    ]
    lib.coilforge_generate_nodes.restype = ctypes.c_int

    return lib


def to_c_config(config: CoilConfig) -> CoilForgeConfig:
    '''
    Convert a Python CoilConfig dataclass instance into the ctypes structure
    expected by the native library.
    '''
    c_cfg = CoilForgeConfig()

    c_cfg.hole_radius    = config.hole_radius
    c_cfg.turns          = config.turns
    c_cfg.track_width    = config.track_width
    c_cfg.pitch          = config.pitch
    c_cfg.arc_resolution = config.arc_resolution
    c_cfg.center_x       = config.center_x
    c_cfg.center_y       = config.center_y
    c_cfg.angle          = config.angle
    c_cfg.layers         = config.layers
    c_cfg.direction      = -1 if config.direction == "CW" else 1
    c_cfg.via_size       = config.via_size

    encoded_name = config.net_name.encode("utf-8")[:127]
    c_cfg.net_name = encoded_name

    return c_cfg


def run_ctypes_bridge(config: CoilConfig) -> str:
    '''
    Call the diagnostic native function and return its formatted string output.
    '''
    lib = load_library()
    c_cfg = to_c_config(config)
    out_buffer = ctypes.create_string_buffer(OUTPUT_BUFFER_SIZE)

    ok = lib.coilforge_process_config(
        ctypes.byref(c_cfg),
        out_buffer,
        ctypes.sizeof(out_buffer),
    )

    if not ok:
        raise CoilForgeBridgeError("coilforge_process_config returned failure")

    return out_buffer.value.decode("utf-8")


def get_node_count(config: CoilConfig) -> int:
    '''
    Ask the native library how many nodes are required for the current coil.
    '''
    lib = load_library()
    c_cfg = to_c_config(config)
    out_count = ctypes.c_int(0)

    ok = lib.coilforge_get_node_count(
        ctypes.byref(c_cfg),
        ctypes.byref(out_count),
    )

    if not ok:
        raise CoilForgeBridgeError("coilforge_get_node_count returned failure")

    if out_count.value <= 0:
        raise CoilForgeBridgeError(
            f"coilforge_get_node_count returned invalid node count: {out_count.value}"
        )

    return out_count.value


def generate_nodes(config: CoilConfig) -> list[tuple[float, float]]:
    '''
    Generate the centerline node list for the current coil configuration.

    Returns:
        A Python list of (x, y) tuples in millimeters.
    '''
    lib = load_library()
    c_cfg = to_c_config(config)

    required_count = get_node_count(config)

    node_array_type = CoilForgeVec2 * required_count
    out_nodes = node_array_type()
    out_count = ctypes.c_int(0)

    ok = lib.coilforge_generate_nodes(
        ctypes.byref(c_cfg),
        out_nodes,
        required_count,
        ctypes.byref(out_count),
    )

    if not ok:
        raise CoilForgeBridgeError("coilforge_generate_nodes returned failure")

    if out_count.value < 0 or out_count.value > required_count:
        raise CoilForgeBridgeError(
            f"coilforge_generate_nodes returned invalid output count: {out_count.value}"
        )

    return [(out_nodes[i].x, out_nodes[i].y) for i in range(out_count.value)]
