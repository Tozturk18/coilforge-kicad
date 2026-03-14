# main

Executable entry point for the kicad-bldc-coil-generator.

## Purpose

Ties together all engine modules to:

1. Parse CLI arguments via `engine/app/cli`
2. Load configuration via `engine/app/config`
3. Generate coil geometry via `engine/geometry` and `engine/coil`
4. Write KiCad footprint output via `engine/kicad/footprint_writer`

## Usage

```bash
./kicad-bldc-coil-generator --config config.json --output out.kicad_mod
```

The current CLI-facing configuration uses `pitch` as the public turn-to-turn distance.
Legacy spacing input can still be translated internally for compatibility.
