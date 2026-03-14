#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# CoilForge KiCad dev installer
# -----------------------------
# Creates symlinks from this repo into KiCad's 3rdparty plugin folders.
# macOS target shown here for KiCad 10.0.
#
# Installed symlinks:
#   ~/Documents/KiCAD/10.0/3rdparty/plugins/com_github_tozturk18_coilforge-kicad
#   ~/Documents/KiCAD/10.0/3rdparty/resources/com_github_tozturk18_coilforge-kicad
#
# Source folders in repo:
#   plugin/plugins
#   plugin/resources

PLUGIN_ID="com_github_tozturk18_coilforge-kicad"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

SRC_PLUGINS_DIR="$REPO_ROOT/plugin/plugins"
SRC_RESOURCES_DIR="$REPO_ROOT/plugin/resources"

KICAD_3RDPARTY_DIR="$HOME/Documents/KiCAD/10.0/3rdparty"
DST_PLUGINS_PARENT="$KICAD_3RDPARTY_DIR/plugins"
DST_RESOURCES_PARENT="$KICAD_3RDPARTY_DIR/resources"

DST_PLUGIN_LINK="$DST_PLUGINS_PARENT/$PLUGIN_ID"
DST_RESOURCE_LINK="$DST_RESOURCES_PARENT/$PLUGIN_ID"

echo "Repo root: $REPO_ROOT"
echo "KiCad 3rdparty dir: $KICAD_3RDPARTY_DIR"

# Check source folders exist
if [[ ! -d "$SRC_PLUGINS_DIR" ]]; then
    echo "ERROR: Missing source plugins directory:"
    echo "  $SRC_PLUGINS_DIR"
    exit 1
fi

if [[ ! -d "$SRC_RESOURCES_DIR" ]]; then
    echo "ERROR: Missing source resources directory:"
    echo "  $SRC_RESOURCES_DIR"
    exit 1
fi

# Ensure KiCad destination parents exist
mkdir -p "$DST_PLUGINS_PARENT"
mkdir -p "$DST_RESOURCES_PARENT"

# Remove any old files/folders/symlinks at destination
rm -rf "$DST_PLUGIN_LINK"
rm -rf "$DST_RESOURCE_LINK"

# Create symlinks
ln -s "$SRC_PLUGINS_DIR" "$DST_PLUGIN_LINK"
ln -s "$SRC_RESOURCES_DIR" "$DST_RESOURCE_LINK"

echo
echo "Installed development symlinks:"
echo "  $DST_PLUGIN_LINK -> $SRC_PLUGINS_DIR"
echo "  $DST_RESOURCE_LINK -> $SRC_RESOURCES_DIR"
echo
echo "Done."
echo "Restart KiCad or use the Action Plugins refresh button if needed."