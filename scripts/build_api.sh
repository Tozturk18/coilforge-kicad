#!/usr/bin/env bash
set -euo pipefail

# 1) Optional: remove previous dylib
rm -f ./plugin/plugins/bin/macOS/libcoilforge.dylib

# 2) Create temp build dir OUTSIDE repo
TMP_BUILD_DIR="$(mktemp -d /tmp/coilforge-cmake.XXXXXX)"

# 3) Configure
cmake -S . -B "$TMP_BUILD_DIR" -DCMAKE_BUILD_TYPE=Release

# 4) Build ONLY the ctypes library target (no main.c target build)
cmake --build "$TMP_BUILD_DIR" --target coilforge --config Release

# 5) Cleanup temp build dir
rm -rf "$TMP_BUILD_DIR"

# 6) Verify output
ls -l ./plugin/plugins/bin/macOS/libcoilforge.dylib