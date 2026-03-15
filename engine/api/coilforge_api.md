# COIL FORGE API

The public C API accepts a `CoilForgeConfig` structure with pitch-based geometry.

- `track_width`: copper trace width in millimeters.
- `pitch`: center-to-center distance between adjacent turns in millimeters.
- `direction`: `-1` for CW and `1` for CCW.

The Python ctypes bridge mirrors this ABI exactly.
