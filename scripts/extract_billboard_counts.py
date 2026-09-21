"""Reproduce consonance/data/billboard_pc_chord_type_counts.json from the MIT-licensed R package `incon`
(https://github.com/pmcharrison/incon, data/popular_1_pc_chord_type.rda; McGill Billboard corpus, Burgoyne 2011).
Requires: pip install rdata ; and the .rda downloaded to the path given as argv[1]."""
import json, sys, warnings
import rdata
warnings.simplefilter("ignore")
df = rdata.read_rda(sys.argv[1])["popular_1_pc_chord_type"]
counts = [int(c) for c in df["count"]]
assert len(counts) == 2048
json.dump({
    "source": "incon::popular_1_pc_chord_type (MIT, (c) 2018 Peter M. C. Harrison); McGill Billboard corpus (Burgoyne 2011)",
    "encoding": "id = 1 + sum(2**(11-j) for j in chord_type if j>=1); chord_type = bass-relative pitch-class set incl. 0; list index = id-1",
    "smoothing_add": 1,
    "counts": counts,
}, open(sys.argv[2], "w"))
print("wrote", sys.argv[2], "total count", sum(counts))
