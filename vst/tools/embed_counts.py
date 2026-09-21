"""Embed consonance/data/billboard_pc_chord_type_counts.json as a C++ constexpr array.

Deterministic: same input JSON always produces byte-identical output. Run from the repo root:

    python3 vst/tools/embed_counts.py > vst/src/soc_billboard.inc

The output is committed; this script is not run as part of any build.
"""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(ROOT, "consonance", "data", "billboard_pc_chord_type_counts.json")


def main() -> None:
    with open(DATA) as fh:
        d = json.load(fh)
    counts = d["counts"]
    assert len(counts) == 2048, f"expected 2048 counts (2^11 chord types), got {len(counts)}"
    assert all(isinstance(c, int) and c >= 0 for c in counts), "counts must be non-negative integers"

    out = sys.stdout
    out.write("// GENERATED FILE -- do not edit by hand.\n")
    out.write(f"// Produced by vst/tools/embed_counts.py from {os.path.relpath(DATA, ROOT)}\n")
    out.write(f"// Source: {d.get('source', '?')}; encoding: {d.get('encoding', '?')}; "
              f"smoothing_add: {d.get('smoothing_add', '?')}\n")
    out.write("#pragma once\n#include <cstdint>\n#include <array>\n\n")
    out.write("namespace soc {\n\n")
    out.write("inline constexpr double kBillboardSmoothingAdd = "
              f"{float(d.get('smoothing_add', 1.0))};\n\n")
    out.write(f"inline constexpr std::array<std::uint32_t, {len(counts)}> kBillboardChordTypeCounts = {{{{\n")
    for i in range(0, len(counts), 16):
        row = counts[i:i + 16]
        out.write("    " + ", ".join(str(c) for c in row) + ",\n")
    out.write("}};\n\n}  // namespace soc\n")


if __name__ == "__main__":
    main()
