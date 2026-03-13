#!/usr/bin/env bash
# Build script for macOS / Linux
set -e
mkdir -p build
cd build
cmake ..
cmake --build .
