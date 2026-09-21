# ENVIRONMENT

Pinned versions. Anything not pinned here is a bug in this document.

| Component | Pinned version | Verified how |
|---|---|---|
| JUCE | tag `8.0.15` at `D:/JUCE` | tag existence confirmed via `git ls-remote --tags https://github.com/juce-framework/JUCE` (C-013) |
| C++ standard | C++17 | `tests/cpp/Makefile` builds clean with `-std=c++17` (spike, g++ 13.3.0) |
| Compiler (target) | MSVC from Visual Studio 2022, x64 Native Tools Command Prompt | inherited from the user's microtonal-guitar project |
| Compiler (core tests, portable) | any C++17 compiler; g++ 13.3.0 verified | `make -C vst/tests/cpp red` |
| CMake | ≥ 3.22 | required by `juce_add_plugin` |
| Generator | Ninja | inherited from the user's existing toolchain |
| Python (oracle only) | 3.12.3 | `python3 -V` in the planning sandbox |
| numpy (oracle only) | 2.4.4 | `python3 -c "import numpy; print(numpy.__version__)"` |
| nlohmann/json | v3.11.3, vendored at `vst/third_party/json.hpp` | sha256 prefix `9bea4c8066ef4a1c206b2be5a36302f8`; downloaded from the pinned tag |
| pluginval | latest release, strictness 10 | S-015 |
| DAW | Ableton Live 12 (MPE supported since Live 11; all Live 12 instruments are MPE-capable) | C-010 |

## Setup (execute verbatim, record each output)

```
:: 1. From the x64 Native Tools Command Prompt for VS 2022
cd /d D:\JUCE
git fetch --tags
git checkout 8.0.15
git rev-parse HEAD

:: 2. Toolchain
cmake --version
ninja --version

:: 3. Oracle (needed only to regenerate fixtures; not needed to build)
python -c "import numpy, sys; print(sys.version); print(numpy.__version__)"

:: 4. Verify the inherited freezes before building anything
cd /d <repo root>
sh scripts/verify_frozen.sh
python -m pytest
sh vst/tests/verify_frozen.sh
```

## Core test suite (no JUCE, no CMake)

```
make -C vst/tests/cpp red                                   # against the stub: must FAIL
make -C vst/tests/cpp IMPL=../../src/soc_core.cpp run       # against the real port: must PASS
```

## Known build gotchas (inherited from the user's microtonal-guitar project)

* `-DCMAKE_BUILD_TYPE=Release` must be set **explicitly**; it is not defaulted.
* `add_compile_definitions(JUCE_VST3_CAN_REPLACE_VST2=0)` must appear at directory scope
  **before** `add_subdirectory("D:/JUCE")`, or the Standalone target will not receive it.
* VST3 install permissions: either use an elevated prompt, or redirect `VST3_COPY_DIR` to
  `%LOCALAPPDATA%/Programs/Common/VST3`.
