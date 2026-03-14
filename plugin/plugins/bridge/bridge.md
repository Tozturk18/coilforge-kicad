# bridge.py

ctypes bridge between Python plugin code and the native CoilForge library.

## Purpose

`bridge.py` finds and loads the platform-specific shared library, converts Python config to C struct format, and invokes the C API.

## Important Symbols

- `CoilForgeBridgeError`: bridge-level runtime exception.
- `CoilForgeConfig`: ctypes struct matching the C ABI layout.
- `_get_library_name()`: chooses library filename by OS.
- `_get_library_path()`: resolves path under `plugin/plugins/bin/<platform>`.
- `load_library()`: loads shared library and configures ctypes signatures.
- `to_c_config(config)`: converts validated config into ctypes struct.
- `run_ctypes_bridge(config)`: performs the native call and returns decoded output.
