#!/usr/bin/env bash
# File: /scripts/package_pcm.sh
# Project: CoilForge-KiCAD
# Created: 2026-03-13
# Author: Ozgur Tuna Ozturk
# Last Modified: 2026-03-15 22:14:20
# Modified By: Ozgur Tuna Ozturk

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$ROOT/plugin"
OUT="$ROOT/coilforge_kicad.zip"
PLUGIN_SETTINGS_JSON="$PLUGIN_DIR/plugins/settings/.plugin_settings.json"
METADATA_JSON="$PLUGIN_DIR/metadata.json"

if [[ ! -f "$PLUGIN_SETTINGS_JSON" ]]; then
    echo "ERROR: Missing plugin settings file:"
    echo "  $PLUGIN_SETTINGS_JSON"
    exit 1
fi

if [[ ! -d "$PLUGIN_DIR/plugins" || ! -d "$PLUGIN_DIR/resources" || ! -d "$PLUGIN_DIR/bin" ]]; then
    echo "ERROR: Missing plugin package directories under $PLUGIN_DIR"
    exit 1
fi

cd "$PLUGIN_DIR"

python3 - "$PLUGIN_SETTINGS_JSON" "$METADATA_JSON" "$OUT" <<'PY'
import json
import sys
import zipfile
from pathlib import Path


settings_path = Path(sys.argv[1])
metadata_path = Path(sys.argv[2])
out_path = Path(sys.argv[3])

metadata_keys = [
    "$schema",
    "name",
    "description",
    "description_full",
    "identifier",
    "type",
    "author",
    "maintainer",
    "license",
    "resources",
    "versions",
]


def load_settings() -> dict:
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Invalid plugin settings: expected top-level JSON object")
    return data


def build_metadata(settings: dict) -> dict:
    metadata = {k: settings[k] for k in metadata_keys if k in settings}
    versions = metadata.get("versions")
    if not isinstance(versions, list) or not versions:
        raise SystemExit("Invalid plugin settings: missing non-empty versions list")
    if not isinstance(versions[-1], dict):
        raise SystemExit("Invalid plugin settings: versions[-1] must be an object")

    versions[-1].setdefault("download_size", 0)
    versions[-1].setdefault("install_size", 0)
    return metadata


def write_metadata(metadata: dict) -> None:
    metadata_path.write_text(json.dumps(metadata, indent=4) + "\n", encoding="utf-8")


def iter_files(base: Path):
    for entry in base.rglob("*"):
        if not entry.is_file():
            continue
        if entry.name == ".DS_Store":
            continue
        if "__MACOSX" in entry.parts:
            continue
        yield entry


def calc_install_size() -> int:
    total = metadata_path.stat().st_size
    for entry in iter_files(Path("plugins")):
        total += entry.stat().st_size
    for entry in iter_files(Path("resources")):
        total += entry.stat().st_size
    for entry in iter_files(Path("bin")):
        total += entry.stat().st_size
    return total


def build_zip() -> None:
    if out_path.exists():
        out_path.unlink()
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(Path("metadata.json"), "metadata.json")
        for entry in iter_files(Path("plugins")):
            zf.write(entry, entry.as_posix())
        for entry in iter_files(Path("resources")):
            zf.write(entry, entry.as_posix())
        for entry in iter_files(Path("bin")):
            zf.write(entry, entry.as_posix())


settings = load_settings()
metadata = build_metadata(settings)

version = metadata["versions"][-1]
current_download = int(version.get("download_size", 0))
current_install = int(version.get("install_size", 0))

max_iterations = 12
for _ in range(max_iterations):
    write_metadata(metadata)
    build_zip()

    measured_download = out_path.stat().st_size
    measured_install = calc_install_size()

    if measured_download == current_download and measured_install == current_install:
        break

    current_download = measured_download
    current_install = measured_install
    version["download_size"] = current_download
    version["install_size"] = current_install
else:
    raise SystemExit("Failed to converge download/install size values")

print("PCM package created:")
print(out_path)
print(f"download_size={current_download}")
print(f"install_size={current_install}")
PY