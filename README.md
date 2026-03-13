# kicad-bldc-coil-generator

A modular cross-platform PCB coil and BLDC motor generator for KiCad, powered by a native C geometry engine.

## Repository Structure

```
engine/       Core C geometry and KiCad generation modules
main/         Executable entry point
plugin/       KiCad plugin interface (Python)
external/     External dependencies
examples/     Example configurations and generated outputs
scripts/      Build and packaging helper scripts
pcm/          KiCad Plugin and Content Manager packaging
```

## Getting Started

```bash
git clone --recurse-submodules <repo-url>
# or, after cloning:
git submodule update --init --recursive
```

## Module Documentation

- [engine/app/cli/cli.md](engine/app/cli/cli.md)
- [engine/app/config/config.md](engine/app/config/config.md)
- [engine/core/types/types.md](engine/core/types/types.md)
- [engine/core/units/units.md](engine/core/units/units.md)
- [engine/core/errors/errors.md](engine/core/errors/errors.md)
- [engine/geometry/point/point.md](engine/geometry/point/point.md)
- [engine/geometry/polar/polar.md](engine/geometry/polar/polar.md)
- [engine/geometry/spiral/spiral.md](engine/geometry/spiral/spiral.md)
- [engine/coil/coil/coil.md](engine/coil/coil/coil.md)
- [engine/coil/phase/phase.md](engine/coil/phase/phase.md)
- [engine/coil/stator/stator.md](engine/coil/stator/stator.md)
- [engine/kicad/footprint_writer/footprint_writer.md](engine/kicad/footprint_writer/footprint_writer.md)
- [engine/kicad/sexpr/sexpr.md](engine/kicad/sexpr/sexpr.md)
- [engine/kicad/layer_map/layer_map.md](engine/kicad/layer_map/layer_map.md)
- [engine/util/fs/fs.md](engine/util/fs/fs.md)
- [engine/util/str/str.md](engine/util/str/str.md)
- [engine/util/log/log.md](engine/util/log/log.md)
- [main/main.md](main/main.md)
- [plugin/python/plugin.md](plugin/python/plugin.md)

## License

MIT License — see [LICENSE](LICENSE).
