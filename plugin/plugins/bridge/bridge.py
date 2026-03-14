'''
@ filename: bridge.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2024
@ license:  MIT License
@ description: This module implements the bridge between the Python plugin code and the native CoilForge library.
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
    
    Args: [str] A descriptive error message.
    
    Returns: An instance of CoilForgeBridgeError with the provided message.
    '''
    pass



class CoilForgeConfig(ctypes.Structure):
    '''
    Data structure matching the expected input for the CoilForge native library.

    Args: [C Structure] A ctypes Structure with fields corresponding to the coil configuration parameters.

    Returns: An instance of CoilForgeConfig that can be passed to the native library.
    '''

    _fields_ = [
        ("hole_radius", ctypes.c_double),       # [mm]    Radius of the hole in the center of the coil
        ("turns",       ctypes.c_double),       # [#]     Number of coil turns
        ("track_width", ctypes.c_double),       # [mm]    Track width
        ("spacing",     ctypes.c_double),       # [mm]    Spacing between coil turns
        ("center_x",    ctypes.c_double),       # [mm]    Center X coordinate
        ("center_y",    ctypes.c_double),       # [mm]    Center Y coordinate
        ("angle",       ctypes.c_double),       # [deg]   Rotation angle in degrees
        ("layers",      ctypes.c_int),          # [#]     Number of layers
        ("direction",   ctypes.c_int),          # [0/!]   0 = CW, 1 = CCW
        ("via_size",    ctypes.c_double),       # [mm]    Via size in mm
        ("net_name",    ctypes.c_char * 128),   # [char*] Net name as UTF-8 string
    ]


def _get_library_name() -> Path:
    '''
    Get the appopriate library name according to the current platform/OS.

    Args: None

    Returns: A Path object representing the relative path to the native library file.
    
    Note: The actual library files should be named accordingly and placed in the "bin" directory of the plugin package.
    '''

    # Get the current operating system
    system = platform.system()

    # Determine the library name based on the OS
    if system == "Darwin":              # macOS
        return Path("macOS") / "libcoilforge.dylib"
    if system == "Windows":             # Windows
        return Path("Windows") / "coilforge.dll"
    if system == "Linux":               # Linux
        return Path("Linux") / "libcoilforge.so"

    raise CoilForgeBridgeError(f"Unsupported platform: {system}")


def _get_library_path() -> Path:
    '''
    Get the full file path to the CoilForge native library based on the current platform.

    Args: None

    Returns: A Path object representing the full path to the native library file.
    '''

    # Get the relative path to the library
    file_root = Path(__file__).resolve().parents[1]
    return file_root / "bin" / _get_library_name()


def load_library() -> ctypes.CDLL:
    '''
    Load the CoilForge native library using ctypes.
    Raises CoilForgeBridgeError if the library cannot be loaded.

    Args: None

    Returns: A ctypes.CDLL instance representing the loaded library, ready for function calls.
    '''

    # Get the library path
    lib_path = _get_library_path()

    
    try:
        # Check if the library file exists
        lib = ctypes.CDLL(str(lib_path))
    except OSError as exc:
        raise CoilForgeBridgeError(
            f"Failed to load CoilForge native library from {lib_path}: {exc}"
        ) from exc

    # Set the argument and return types for the coilforge_process_config function
    lib.coilforge_process_config.argtypes = [
        ctypes.POINTER(CoilForgeConfig),    #**< [in] Pointer to the coil configuration
        ctypes.POINTER(ctypes.c_char),      #**< [out] Buffer to receive the output string
        ctypes.c_size_t,                    #**< [in] Size of the output buffer
    ]
    lib.coilforge_process_config.restype = ctypes.c_int

    return lib


def to_c_config(config: CoilConfig) -> CoilForgeConfig:
    '''
    Convert a CoilConfig dataclass instance into a CoilForgeConfig ctypes structure for passing to the native library.

    Args: config [CoilConfig] - The coil configuration data from the plugin dialog.

    Returns: An instance of CoilForgeConfig with fields populated from the provided CoilConfig.
    '''

    c_cfg               = CoilForgeConfig()                     # Create an instance of the C config structure
    c_cfg.hole_radius   = config.hole_radius                    # Set hole radius
    c_cfg.turns         = config.turns                          # Set number of turns
    c_cfg.track_width   = config.track_width                    # Set track width
    c_cfg.spacing       = config.spacing                        # Set spacing between coil turns
    c_cfg.center_x      = config.center_x                       # Set center X coordinate
    c_cfg.center_y      = config.center_y                       # Set center Y coordinate
    c_cfg.angle         = config.angle                          # Set rotation angle
    c_cfg.layers        = config.layers                         # Set number of layers
    c_cfg.direction     = 0 if config.direction == "CW" else 1  # Convert direction string to int (0 for CW, 1 for CCW)
    c_cfg.via_size      = config.via_size                       # Set via size

    # Encode the net name as UTF-8 and ensure it fits within the 128 character limit of the C structure
    encoded_name = config.net_name.encode("utf-8")[:127]
    c_cfg.net_name      = encoded_name                          # Set net name

    return c_cfg


def run_ctypes_bridge(config: CoilConfig) -> str:
    '''
    Run the CoilForge native library function via ctypes.

    Args: config [CoilConfig] - The coil configuration data to be processed by the native library.

    Returns: A string output from the native library, decoded from UTF-8.
    Raises CoilForgeBridgeError if the native function call fails or returns an error.
    '''

    # Load the library
    lib = load_library()

    # Convert the Python config to the C struct format
    c_cfg = to_c_config(config)

    # Create a buffer to receive the output string from the native library
    out_buffer = ctypes.create_string_buffer(OUTPUT_BUFFER_SIZE)

    # Call the native function and check the return value
    ok = lib.coilforge_process_config(
        ctypes.byref(c_cfg),
        out_buffer,
        ctypes.sizeof(out_buffer),
    )

    # Check if the native function call was successful
    if not ok:
        raise CoilForgeBridgeError("coilforge_process_config returned failure")

    # Decode the output buffer as UTF-8 and return it as a Python string
    return out_buffer.value.decode("utf-8")