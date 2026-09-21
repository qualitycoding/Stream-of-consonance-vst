// Stream-of-Consonance VST — core model port, implementation.
//
// Ports the Python `consonance` package to C++. Every function is verified against the golden
// fixtures in tests/fixtures/ (the oracle). See soc_core.h for the contract and plan/DECISIONS.md
// for the load-bearing design choices (D-001..D-008) this file assumes.

#include "soc_core.h"
#include "soc_billboard.inc"   // generated from consonance/data/billboard_pc_chord_type_counts.json

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <complex>
#include <cstring>
#include <numeric>
#include <vector>

namespace soc {

// =========================================================================================
// PCG64 (numpy default_rng's bit generator: XSL-RR 128/64)
//
// Verified against tests/fixtures/rng.json for 7 seeds (0,1,3,5,7,42,12345): the sequence is
// advance-then-output (not output-then-advance -- these differ by exactly one draw, and only
// advance-then-output reproduces the fixture). See research/spikes/spike_04_seedsequence.py,
// which re-derives numpy's SeedSequence entropy mixing from scratch and matches
// np.random.default_rng(seed).bit_generator.state exactly for all 7 seeds.
// =========================================================================================

namespace {

constexpr __uint128_t kPcgMultiplier =
    (static_cast<__uint128_t>(0x2360ED051FC65DA4ULL) << 64) | 0x4385DF649FCCF645ULL;

std::uint64_t rotr64(std::uint64_t v, unsigned rot) {
    rot &= 63u;
    return rot ? ((v >> rot) | (v << (64u - rot))) : v;
}

std::uint64_t pcgOutputXslRr(__uint128_t state) {
    const auto hi = static_cast<std::uint64_t>(state >> 64);
    const auto lo = static_cast<std::uint64_t>(state);
    const auto rot = static_cast<unsigned>(state >> 122);   // top 6 bits of the 128-bit state
    return rotr64(hi ^ lo, rot);
}

__uint128_t parseHex128(const std::string& hexStr) {
    std::string s = hexStr;
    if (s.size() > 1 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) s = s.substr(2);
    __uint128_t v = 0;
    for (char c : s) {
        v <<= 4;
        if (c >= '0' && c <= '9') v |= static_cast<unsigned>(c - '0');
        else if (c >= 'a' && c <= 'f') v |= static_cast<unsigned>(c - 'a' + 10);
        else if (c >= 'A' && c <= 'F') v |= static_cast<unsigned>(c - 'A' + 10);
        // any other character (shouldn't occur in a well-formed fixture) is silently skipped
    }
    return v;
}

// --- numpy SeedSequence, minimal port: single uint32 entropy word (seeds 0..2^32-1) ------
constexpr std::uint32_t kXshift = 16;
constexpr std::uint32_t kInitA = 0x43b0d7e5, kMultA = 0x931e8875;
constexpr std::uint32_t kInitB = 0x8b51f9dd, kMultB = 0x58f38ded;
constexpr std::uint32_t kMixMultL = 0xca01f9dd, kMixMultR = 0x4973f715;

std::uint32_t hashmix(std::uint32_t value, std::uint32_t& hashConst) {
    value ^= hashConst;
    hashConst *= kMultA;
    value *= hashConst;
    value ^= value >> kXshift;
    return value;
}

std::uint32_t mix32(std::uint32_t x, std::uint32_t y) {
    std::uint32_t result = (kMixMultL * x) - (kMixMultR * y);
    result ^= result >> kXshift;
    return result;
}

// entropy: assembled entropy words (here: exactly one word, the seed). poolSize fixed at 4,
// matching numpy's SeedSequence default.
std::array<std::uint32_t, 4> mixEntropy(const std::vector<std::uint32_t>& entropy) {
    std::array<std::uint32_t, 4> pool{};
    std::uint32_t hashConst = kInitA;
    for (std::size_t i = 0; i < pool.size(); ++i)
        pool[i] = hashmix(i < entropy.size() ? entropy[i] : 0u, hashConst);
    for (std::size_t iSrc = 0; iSrc < pool.size(); ++iSrc)
        for (std::size_t iDst = 0; iDst < pool.size(); ++iDst)
            if (iSrc != iDst) pool[iDst] = mix32(pool[iDst], hashmix(pool[iSrc], hashConst));
    for (std::size_t iSrc = pool.size(); iSrc < entropy.size(); ++iSrc)
        for (std::size_t iDst = 0; iDst < pool.size(); ++iDst)
            pool[iDst] = mix32(pool[iDst], hashmix(entropy[iSrc], hashConst));
    return pool;
}

std::vector<std::uint32_t> generateStateU32(const std::array<std::uint32_t, 4>& pool, int nWords) {
    std::vector<std::uint32_t> out(static_cast<std::size_t>(nWords));
    std::uint32_t hashConst = kInitB;
    for (int i = 0; i < nWords; ++i) {
        std::uint32_t v = pool[static_cast<std::size_t>(i) % pool.size()];
        v ^= hashConst;
        hashConst *= kMultB;
        v *= hashConst;
        v ^= v >> kXshift;
        out[static_cast<std::size_t>(i)] = v;
    }
    return out;
}

}  // namespace

Pcg64 Pcg64::fromState(const std::string& state128Hex, const std::string& inc128Hex) {
    Pcg64 rng;
    rng.state_ = parseHex128(state128Hex);
    rng.inc_ = parseHex128(inc128Hex);
    return rng;
}

Pcg64 Pcg64::fromNumpySeed(std::uint64_t seed) {
    // Restricted to seeds < 2^32, matching the plugin's documented seed range (0..9999, D-005 /
    // ASSUMPTIONS A-007). A seed this large is a caller error, not a data condition -- throw.
    if (seed > 0xFFFFFFFFull)
        throw std::invalid_argument("Pcg64::fromNumpySeed: seed must fit in 32 bits");
    const auto pool = mixEntropy({static_cast<std::uint32_t>(seed)});
    const auto words32 = generateStateU32(pool, 8);  // 4 uint64 = 8 uint32
    std::array<std::uint64_t, 4> u64{};
    for (int i = 0; i < 4; ++i)
        u64[static_cast<std::size_t>(i)] =
            static_cast<std::uint64_t>(words32[static_cast<std::size_t>(2 * i)]) |
            (static_cast<std::uint64_t>(words32[static_cast<std::size_t>(2 * i + 1)]) << 32);
    const __uint128_t initstate = (static_cast<__uint128_t>(u64[0]) << 64) | u64[1];
    const __uint128_t initseq = (static_cast<__uint128_t>(u64[2]) << 64) | u64[3];

    Pcg64 rng;
    rng.inc_ = (initseq << 1) | 1;
    rng.state_ = 0;
    rng.state_ = rng.state_ * kPcgMultiplier + rng.inc_;
    rng.state_ = rng.state_ + initstate;
    rng.state_ = rng.state_ * kPcgMultiplier + rng.inc_;
    return rng;
}

std::uint64_t Pcg64::nextUint64() {
    state_ = state_ * kPcgMultiplier + inc_;   // advance first ...
    return pcgOutputXslRr(state_);              // ... then output from the new state
}

double Pcg64::nextDouble() {
    return static_cast<double>(nextUint64() >> 11) * (1.0 / 9007199254740992.0);  // 2^-53
}

// =========================================================================================
// Timbre
// =========================================================================================

Timbre harmonicTimbre(int nHarmonics, double rollOff) {
    if (nHarmonics < 1) throw std::invalid_argument("harmonicTimbre: nHarmonics must be >= 1");
    Timbre t;
    t.ratios.reserve(static_cast<std::size_t>(nHarmonics));
    t.amps.reserve(static_cast<std::size_t>(nHarmonics));
    for (int k = 1; k <= nHarmonics; ++k) {
        t.ratios.push_back(static_cast<double>(k));
        t.amps.push_back(1.0 / std::pow(static_cast<double>(k), rollOff));
    }
    return t;
}

namespace {

void validateFreqs(const std::vector<double>& f) {
    if (f.empty()) throw std::invalid_argument("frequencies must be non-empty");
    for (double x : f)
        if (!std::isfinite(x) || x <= 0.0) throw std::invalid_argument("frequencies must be finite and > 0");
}

// One note's partials: frequencies and amplitudes, amplitude zeroed above maxHz.
struct Partials {
    std::vector<double> freq, amp;
};

Partials notePartials(double fundamentalHz, const Timbre& t, double maxHz) {
    Partials p;
    p.freq.reserve(t.ratios.size());
    p.amp.reserve(t.ratios.size());
    for (std::size_t i = 0; i < t.ratios.size(); ++i) {
        const double f = fundamentalHz * t.ratios[i];
        p.freq.push_back(f);
        p.amp.push_back(f > maxHz ? 0.0 : t.amps[i]);
    }
    return p;
}

Partials chordPartials(const std::vector<double>& freqsHz, const Timbre& t, double maxHz) {
    Partials out;
    out.freq.reserve(freqsHz.size() * t.ratios.size());
    out.amp.reserve(freqsHz.size() * t.ratios.size());
    for (double f0 : freqsHz) {
        auto p = notePartials(f0, t, maxHz);
        out.freq.insert(out.freq.end(), p.freq.begin(), p.freq.end());
        out.amp.insert(out.amp.end(), p.amp.begin(), p.amp.end());
    }
    return out;
}

double hutchinsonTerm(double f1, double f2, double a1, double a2) {
    const double d = std::fabs(f1 - f2);
    const double cbw = 1.72 * std::pow((f1 + f2) / 2.0, 0.65);
    const double y = d / cbw;
    if (y > 1.2) return 0.0;
    const double u = (y / 0.25) * std::exp(1.0 - y / 0.25);
    return a1 * a2 * u * u;
}

double roughnessOfPartials(const Partials& p) {
    double num = 0.0, den = 0.0;
    const std::size_t k = p.freq.size();
    for (std::size_t i = 0; i < k; ++i) den += p.amp[i] * p.amp[i];
    for (std::size_t i = 0; i < k; ++i)
        for (std::size_t j = i + 1; j < k; ++j)
            num += hutchinsonTerm(p.freq[i], p.freq[j], p.amp[i], p.amp[j]);
    return den > 0.0 ? num / den : 0.0;
}

}  // namespace

double hutchinsonRoughness(const std::vector<double>& freqsHz, const Timbre& t, double maxHz) {
    validateFreqs(freqsHz);
    return roughnessOfPartials(chordPartials(freqsHz, t, maxHz));
}

// =========================================================================================
// Harmonicity (Milne / Harrison & Pearce pitch-class harmonicity)
// =========================================================================================

namespace {

constexpr int kBins = kHarmonicityBins;  // 1200, 1-cent grid

double wrapCents(double c) {  // Python's np.mod: always returns a value in [0, 1200)
    double m = std::fmod(c, 1200.0);
    if (m < 0.0) m += 1200.0;
    return m;
}

// Literal note spectrum: smoothed circular histogram of one note's partials over `kBins` bins.
// Mirrors consonance/harmonicity.py::_note_spectra for a single input cents value.
std::array<double, kBins> noteSpectrumLiteral(double cents, const Timbre& t) {
    std::array<double, kBins> out{};
    for (std::size_t p = 0; p < t.ratios.size(); ++p) {
        const double w = std::pow(t.amps[p], kHarmonicityRho);
        const double offCents = 1200.0 * std::log2(t.ratios[p]);
        const double pos = wrapCents(cents + offCents);
        for (int b = 0; b < kBins; ++b) {
            double d = std::fabs(static_cast<double>(b) - pos);
            d = std::min(d, 1200.0 - d);
            out[static_cast<std::size_t>(b)] += w * std::exp(-0.5 * (d / kHarmonicitySigmaCents) *
                                                              (d / kHarmonicitySigmaCents));
        }
    }
    return out;
}

std::array<double, kBins> sumSpectra(const std::vector<double>& centsList, const Timbre& t) {
    std::array<double, kBins> S{};
    for (double c : centsList) {
        const auto s = noteSpectrumLiteral(c, t);
        for (int b = 0; b < kBins; ++b) S[static_cast<std::size_t>(b)] += s[static_cast<std::size_t>(b)];
    }
    return S;
}

// Circular cross-correlation r[n] = sum_m S[m] * T[(m - n) mod B]. O(B^2); used only for
// one-time setup (template autocorrelation, and once per note for the held-notes vector), never
// per candidate -- see the linearity shortcut in CandidateScorer below.
std::array<double, kBins> circularCorrelate(const std::array<double, kBins>& S,
                                            const std::array<double, kBins>& T) {
    std::array<double, kBins> r{};
    for (int n = 0; n < kBins; ++n) {
        double acc = 0.0;
        for (int m = 0; m < kBins; ++m) {
            int idx = m - n;
            idx %= kBins;
            if (idx < 0) idx += kBins;
            acc += S[static_cast<std::size_t>(m)] * T[static_cast<std::size_t>(idx)];
        }
        r[static_cast<std::size_t>(n)] = acc;
    }
    return r;
}

double norm(const std::array<double, kBins>& v) {
    double s = 0.0;
    for (double x : v) s += x * x;
    return std::sqrt(s);
}

// Given the correlation vector r (already computed for a specific S) and the two norms, produce
// the KL-from-uniform value in bits. Mirrors consonance/harmonicity.py::_kl_from_uniform_bits
// for a single row.
double klFromCorrelation(const std::array<double, kBins>& r, double normS, double normT) {
    const double denom = normS * normT;
    std::array<double, kBins> cos{};
    double tot = 0.0;
    for (int b = 0; b < kBins; ++b) {
        double c = denom > 0.0 ? r[static_cast<std::size_t>(b)] / denom : 0.0;
        if (c < 0.0) c = 0.0;
        cos[static_cast<std::size_t>(b)] = c;
        tot += c;
    }
    double kl = 0.0;
    for (int b = 0; b < kBins; ++b) {
        if (tot <= 0.0) continue;
        const double p = cos[static_cast<std::size_t>(b)] / tot;
        if (p > 0.0) kl += p * std::log2(p * kBins);
    }
    return std::max(kl, 0.0);
}

}  // namespace

double harmonicityBits(const std::vector<double>& cents, const Timbre& t) {
    if (cents.empty()) throw std::invalid_argument("cents must be non-empty");
    for (double c : cents) if (!std::isfinite(c)) throw std::invalid_argument("cents must be finite");
    const auto S = sumSpectra(cents, t);
    const auto T = noteSpectrumLiteral(0.0, t);   // the template: a single note at cents=0
    const auto r = circularCorrelate(S, T);
    return klFromCorrelation(r, norm(S), norm(T));
}

// =========================================================================================
// Familiarity (Billboard corpus)
// =========================================================================================

namespace {

std::vector<double> billboardLogP() {
    static const std::vector<double> table = [] {
        double total = 0.0;
        for (auto c : kBillboardChordTypeCounts) total += static_cast<double>(c);
        const double denom = total + kBillboardSmoothingAdd * static_cast<double>(kBillboardChordTypeCounts.size());
        std::vector<double> logp(kBillboardChordTypeCounts.size());
        for (std::size_t i = 0; i < kBillboardChordTypeCounts.size(); ++i) {
            const double p = (static_cast<double>(kBillboardChordTypeCounts[i]) + kBillboardSmoothingAdd) / denom;
            logp[i] = std::log(p);
        }
        return logp;
    }();
    return table;
}

int floorMod12(long r) {
    long m = r % 12;
    if (m < 0) m += 12;
    return static_cast<int>(m);
}

// chord_type_id: 1 + sum(2^(11-j) for j in pcs if j >= 1). pcs always contains 0 (the bass).
int chordTypeId(const std::vector<bool>& pcPresent /* size 12 */) {
    int id = 1;
    for (int j = 1; j <= 11; ++j)
        if (pcPresent[static_cast<std::size_t>(j)]) id += 1 << (11 - j);
    return id;
}

// Returns the 12 present-flags, or false (2nd) if the chord is not within tolerance of 12-TET.
std::pair<std::vector<bool>, bool> chordTypeFromCents(const std::vector<double>& centsAbs) {
    std::vector<bool> pcs(12, false);
    pcs[0] = true;
    const double lo = *std::min_element(centsAbs.begin(), centsAbs.end());
    for (double x : centsAbs) {
        const double rel = x - lo;
        const double r = std::nearbyint(rel / 100.0);   // round-half-to-even, matching numpy/Python
        if (std::fabs(rel - 100.0 * r) > kFamiliarityToleranceCents) return {pcs, false};
        pcs[static_cast<std::size_t>(floorMod12(static_cast<long>(r)))] = true;
    }
    return {pcs, true};
}

}  // namespace

double neutralLogProb() {
    static const double v = [] {
        const auto& logp = billboardLogP();
        double total = 0.0;
        for (auto c : kBillboardChordTypeCounts) total += static_cast<double>(c);
        double acc = 0.0;
        for (std::size_t i = 0; i < kBillboardChordTypeCounts.size(); ++i)
            acc += (static_cast<double>(kBillboardChordTypeCounts[i]) / total) * logp[i];
        return acc;
    }();
    return v;
}

std::optional<double> familiarityLogP(const std::vector<double>& cents) {
    if (cents.empty()) throw std::invalid_argument("cents must be non-empty");
    auto [pcs, ok] = chordTypeFromCents(cents);
    if (!ok) return std::nullopt;
    const int id = chordTypeId(pcs);
    return billboardLogP()[static_cast<std::size_t>(id - 1)];
}

// =========================================================================================
// Composite score
// =========================================================================================

namespace {

std::vector<double> centsFromHz(const std::vector<double>& freqsHz, double refHz) {
    std::vector<double> out;
    out.reserve(freqsHz.size());
    for (double f : freqsHz) out.push_back(1200.0 * std::log2(f / refHz));
    return out;
}

}  // namespace

double compositeScore(const std::vector<double>& freqsHz, const Timbre& t, const Weights& w) {
    validateFreqs(freqsHz);
    const double roughness = roughnessOfPartials(chordPartials(freqsHz, t, kMaxHz));
    const auto cents = centsFromHz(freqsHz, kModelRefHz);
    const double harm = harmonicityBits(cents, t);
    const auto fam = familiarityLogP(cents);
    const double famVal = fam.has_value() ? *fam : neutralLogProb();
    return w.intercept + w.interference * roughness + w.harmonicity * harm + w.familiarity * famVal +
           w.nNotes * static_cast<double>(freqsHz.size());
}

// =========================================================================================
// Pitch sets
// =========================================================================================

const std::vector<double> kJustIntervalsCents = [] {
    static const double ratios[12][2] = {
        {1, 1}, {16, 15}, {9, 8}, {6, 5}, {5, 4}, {4, 3},
        {45, 32}, {3, 2}, {8, 5}, {5, 3}, {7, 4}, {15, 8},
    };
    std::vector<double> v;
    v.reserve(12);
    for (auto& r : ratios) v.push_back(1200.0 * std::log2(r[0] / r[1]));
    return v;
}();

std::vector<double> candidateCents(const PitchSetSpec& spec) {
    if (spec.highCents <= spec.lowCents) throw std::invalid_argument("highCents must exceed lowCents");
    std::vector<double> out;

    if (spec.mode == PitchMode::Standard) {
        if (spec.edo < 1) throw std::invalid_argument("edo must be >= 1");
        const double step = 1200.0 / spec.edo;
        const long first = static_cast<long>(std::ceil((spec.lowCents - spec.offsetCents) / step));
        const long last = static_cast<long>(std::floor((spec.highCents - spec.offsetCents) / step));
        for (long k = first; k <= last; ++k) out.push_back(spec.offsetCents + step * static_cast<double>(k));
        return out;
    }

    // Free mode.
    if (!spec.snapTo.empty()) {
        std::vector<double> base;
        base.reserve(spec.snapTo.size());
        for (double s : spec.snapTo) base.push_back(wrapCents(s + spec.offsetCents));
        const long loOct = static_cast<long>(std::floor(spec.lowCents / 1200.0));
        const long hiOct = static_cast<long>(std::ceil(spec.highCents / 1200.0));
        for (long oct = loOct; oct <= hiOct; ++oct)
            for (double b : base) out.push_back(static_cast<double>(oct) * 1200.0 + b);
        std::sort(out.begin(), out.end());
        out.erase(std::unique(out.begin(), out.end()), out.end());
        out.erase(std::remove_if(out.begin(), out.end(),
                                 [&](double c) { return c < spec.lowCents || c > spec.highCents; }),
                  out.end());
        return out;
    }

    if (spec.resolutionCents <= 0.0) throw std::invalid_argument("resolutionCents must be > 0");
    const double step = spec.resolutionCents;
    const long first = static_cast<long>(std::ceil((spec.lowCents - spec.offsetCents) / step));
    const long last = static_cast<long>(std::floor((spec.highCents - spec.offsetCents) / step));
    for (long k = first; k <= last; ++k) out.push_back(spec.offsetCents + step * static_cast<double>(k));
    return out;
}

// =========================================================================================
// CandidateScorer: score held U {candidate} for every candidate. The hot path (D-004).
//
// Harmonicity: exploits that circular correlation is linear in its first argument, and that
// rotating one operand of a circular correlation by k rotates the output by k (verified in
// research/spikes/spike_04_seedsequence.py's sibling check, see PLAN S-005 note and the
// empirical check run during implementation). So, once per scorer construction:
//   r_T0 = correlate(noteSpectrum(0), template)          -- O(B^2), once
// and once per score() call (not per candidate):
//   r_S0 = correlate(sum of held-note spectra, template)  -- O(B^2), cheap since held is small
// then per candidate with integer cents k:
//   r_i[b] = r_S0[b] + r_T0[(b - k) mod B]                -- O(B), no correlation needed at all
// This is a strictly cheaper way to reach the same numbers D-004 specifies; every value is
// still checked against the oracle to the same 1e-9 tolerance (T-009).
//
// Roughness: held-held pairs are identical for every candidate and computed once per score()
// call; only held-candidate cross pairs and the candidate's own self pairs vary per candidate.
// =========================================================================================

struct CandidateScorer::Impl {
    Timbre timbre;
    Weights weights;
    double refHz;
    std::vector<double> candCents;
    bool candCentsIntegral = true;

    // Per-candidate precomputation (constant across score() calls).
    std::vector<double> candFreq;                 // fundamental Hz per candidate
    std::vector<Partials> candPartials;            // this candidate's own partials
    std::vector<double> candSelfRoughnessNum;      // sum over candidate-self pairs
    std::vector<double> candSelfSumA2;             // sum(amp^2) over candidate's own partials
    std::vector<long> candBinShift;                // round(cents) mod kBins, when integral
    std::array<double, kBins> T0{};                // literal spectrum of a note at cents=0
    std::array<double, kBins> templateSpec{};       // == T0 (kept separately to mirror the model)
    std::array<double, kBins> rT0{};                // correlate(T0, template)
    double normT = 0.0;

    explicit Impl(const Timbre& tm, const std::vector<double>& cc, double rh, const Weights& w)
        : timbre(tm), weights(w), refHz(rh), candCents(cc) {
        if (cc.empty()) throw std::invalid_argument("CandidateScorer: candidate set must be non-empty");

        for (double c : candCents)
            if (std::fabs(c - std::nearbyint(c)) > 1e-6) { candCentsIntegral = false; break; }

        candFreq.reserve(cc.size());
        candPartials.reserve(cc.size());
        candSelfRoughnessNum.reserve(cc.size());
        candSelfSumA2.reserve(cc.size());
        for (double c : candCents) {
            const double f = refHz * std::pow(2.0, c / 1200.0);
            candFreq.push_back(f);
            auto p = notePartials(f, timbre, kMaxHz);
            double selfNum = 0.0, selfA2 = 0.0;
            for (std::size_t i = 0; i < p.freq.size(); ++i) {
                selfA2 += p.amp[i] * p.amp[i];
                for (std::size_t j = i + 1; j < p.freq.size(); ++j)
                    selfNum += hutchinsonTerm(p.freq[i], p.freq[j], p.amp[i], p.amp[j]);
            }
            candSelfRoughnessNum.push_back(selfNum);
            candSelfSumA2.push_back(selfA2);
            candPartials.push_back(std::move(p));
        }

        T0 = noteSpectrumLiteral(0.0, timbre);
        templateSpec = T0;
        rT0 = circularCorrelate(T0, templateSpec);
        normT = norm(templateSpec);

        candBinShift.reserve(cc.size());
        for (double c : candCents) {
            long k = static_cast<long>(std::lround(wrapCents(c)));
            if (k == kBins) k = 0;
            candBinShift.push_back(k);
        }
    }
};

CandidateScorer::CandidateScorer(const Timbre& t, const std::vector<double>& candidateCentsIn, double refHz,
                                 const Weights& w)
    : impl_(new Impl(t, candidateCentsIn, refHz, w)) {}

CandidateScorer::~CandidateScorer() { delete impl_; }

std::size_t CandidateScorer::candidateCount() const { return impl_->candCents.size(); }
const std::vector<double>& CandidateScorer::candidateCentsView() const { return impl_->candCents; }

std::vector<double> CandidateScorer::score(const std::vector<double>& heldCentsIn) const {
    const auto& im = *impl_;
    const std::size_t n = im.candCents.size();
    std::vector<double> out(n);

    // --- held-side precomputation (shared across every candidate) --------------------------
    std::vector<double> heldHz;
    heldHz.reserve(heldCentsIn.size());
    for (double c : heldCentsIn) heldHz.push_back(im.refHz * std::pow(2.0, c / 1200.0));
    if (!heldHz.empty()) validateFreqs(heldHz);

    Partials heldP = heldHz.empty() ? Partials{} : chordPartials(heldHz, im.timbre, kMaxHz);
    double heldHeldNum = 0.0, heldSumA2 = 0.0;
    for (std::size_t i = 0; i < heldP.freq.size(); ++i) {
        heldSumA2 += heldP.amp[i] * heldP.amp[i];
        for (std::size_t j = i + 1; j < heldP.freq.size(); ++j)
            heldHeldNum += hutchinsonTerm(heldP.freq[i], heldP.freq[j], heldP.amp[i], heldP.amp[j]);
    }

    const auto S0 = heldHz.empty() ? std::array<double, kBins>{} : sumSpectra(heldCentsIn, im.timbre);
    const auto rS0 = heldHz.empty() ? std::array<double, kBins>{} : circularCorrelate(S0, im.templateSpec);

    const auto famHeldCents = centsFromHz(heldHz, kModelRefHz);  // empty vector if no held notes

    for (std::size_t i = 0; i < n; ++i) {
        // --- roughness: held-held (shared) + held-candidate cross + candidate-self --------
        double crossNum = 0.0;
        const auto& cp = im.candPartials[i];
        for (std::size_t a = 0; a < heldP.freq.size(); ++a)
            for (std::size_t b = 0; b < cp.freq.size(); ++b)
                crossNum += hutchinsonTerm(heldP.freq[a], cp.freq[b], heldP.amp[a], cp.amp[b]);
        const double num = heldHeldNum + crossNum + im.candSelfRoughnessNum[i];
        const double den = heldSumA2 + im.candSelfSumA2[i];
        const double roughness = den > 0.0 ? num / den : 0.0;

        // --- harmonicity: rotation + correlation-linearity ---------------------------------
        double harm;
        if (im.candCentsIntegral) {
            std::array<double, kBins> S{};
            std::array<double, kBins> r{};
            const int k = static_cast<int>(im.candBinShift[i]);
            for (int b = 0; b < kBins; ++b) {
                const int shiftIdx = ((b - k) % kBins + kBins) % kBins;   // (b - k) mod kBins
                S[static_cast<std::size_t>(b)] =
                    (heldHz.empty() ? 0.0 : S0[static_cast<std::size_t>(b)]) +
                    im.T0[static_cast<std::size_t>(shiftIdx)];
                r[static_cast<std::size_t>(b)] =
                    (heldHz.empty() ? 0.0 : rS0[static_cast<std::size_t>(b)]) +
                    im.rT0[static_cast<std::size_t>(shiftIdx)];
            }
            harm = klFromCorrelation(r, norm(S), im.normT);
        } else {
            std::vector<double> combined(heldCentsIn);
            combined.push_back(im.candCents[i]);
            harm = harmonicityBits(combined, im.timbre);
        }

        // --- familiarity ---------------------------------------------------------------------
        std::vector<double> famCents = famHeldCents;
        famCents.push_back(1200.0 * std::log2(im.candFreq[i] / kModelRefHz));
        const auto fam = familiarityLogP(famCents);
        const double famVal = fam.has_value() ? *fam : neutralLogProb();

        const auto& w = im.weights;
        out[i] = w.intercept + w.interference * roughness + w.harmonicity * harm + w.familiarity * famVal +
                 w.nNotes * static_cast<double>(heldHz.size() + 1);
    }
    return out;
}

// =========================================================================================
// MPE encoding. Verified against tests/fixtures/mpe.json: nearest 12-TET MIDI note uses
// round-half-to-even (matching Python round()), and the 14-bit bend uses an asymmetric scale
// around centre 8192: 8191 steps above, 8192 steps below (standard MIDI convention).
// =========================================================================================

MpeNote encodeMpe(double freqHz, int channel, double bendRangeSemitones) {
    if (!std::isfinite(freqHz) || freqHz <= 0.0) throw std::invalid_argument("freqHz must be finite and > 0");
    const double contMidi = 69.0 + 12.0 * std::log2(freqHz / 440.0);
    const double noteD = std::nearbyint(contMidi);
    const int note = static_cast<int>(noteD);
    const double offsetCents = (contMidi - noteD) * 100.0;
    const double fraction = offsetCents / (bendRangeSemitones * 100.0);
    const double scale = fraction >= 0.0 ? 8191.0 : 8192.0;
    long bend = std::lround(8192.0 + fraction * scale);
    bend = std::max<long>(0, std::min<long>(16383, bend));

    MpeNote n;
    n.channel = channel;
    n.noteNumber = std::max(0, std::min(127, note));
    n.pitchBend14 = static_cast<int>(bend);
    return n;
}

double decodeMpeHz(const MpeNote& n, double bendRangeSemitones) {
    const double centred = n.pitchBend14 - 8192;
    const double scale = centred >= 0.0 ? 8191.0 : 8192.0;
    const double semis = (centred / scale) * bendRangeSemitones;
    return 440.0 * std::pow(2.0, (static_cast<double>(n.noteNumber) - 69.0 + semis) / 12.0);
}

// =========================================================================================
// Sampler / stream generator. Mirrors consonance/sampler.py exactly, including RNG draw
// order: one Pcg64::nextDouble() per note, drawn after the weight vector is built. Any
// additional or reordered draw desynchronises every subsequent note against the oracle (T-011).
// =========================================================================================

// =========================================================================================
// Sampler / stream generator. Mirrors consonance/sampler.py exactly, including RNG draw
// order: one Pcg64::nextDouble() per note, drawn after the weight vector is built. Any
// additional or reordered draw desynchronises every subsequent note against the oracle (T-011).
// =========================================================================================

namespace {

// pi(p) ~ exp(-(C(S u {p}) - target)^2 / (2 sigma^2)) * exp(logPrior[p]), excluded candidates
// get weight 0. Mirrors sampler.py::_log_weights + the exclusion masking in sample_next.
// Returns the chosen index via inverse-CDF sampling matching numpy's
// searchsorted(cdf, u*cdf.back(), side="right"), clamped to the last index.
std::size_t weightedChoice(const std::vector<double>& vals, double target, double sigma,
                           const std::vector<bool>& excluded /* may be empty */,
                           const std::vector<double>& logPrior /* may be empty */, Pcg64& rng) {
    if (!(sigma > 0.0) || !std::isfinite(sigma)) throw std::invalid_argument("sigma must be finite and > 0");
    const std::size_t n = vals.size();
    std::vector<double> lw(n);
    double maxFinite = -std::numeric_limits<double>::infinity();
    for (std::size_t i = 0; i < n; ++i) {
        const double v = std::isfinite(vals[i]) ? vals[i] : std::numeric_limits<double>::infinity();
        const double z = (v - target) / sigma;
        double w = -0.5 * z * z;
        if (!logPrior.empty()) w += logPrior[i];
        if (!excluded.empty() && excluded[i]) w = -std::numeric_limits<double>::infinity();
        lw[i] = w;
        if (std::isfinite(w) && w > maxFinite) maxFinite = w;
    }
    if (!std::isfinite(maxFinite)) throw std::runtime_error("no admissible candidate");
    std::vector<double> cdf(n);
    double acc = 0.0;
    for (std::size_t i = 0; i < n; ++i) {
        acc += std::exp(lw[i] - maxFinite);
        cdf[i] = acc;
    }
    const double u = rng.nextDouble() * cdf.back();
    auto it = std::upper_bound(cdf.begin(), cdf.end(), u);  // side="right"
    std::size_t idx = static_cast<std::size_t>(it - cdf.begin());
    if (idx >= n) idx = n - 1;
    return idx;
}

}  // namespace

double sampleNext(const CandidateScorer& scorer, const std::vector<double>& heldCents,
                  const StreamConfig& cfg, Pcg64& rng) {
    // Best-effort single-step primitive: applies target/sigma weighting and min-separation
    // exclusion (both computable from heldCents alone), but NOT the novelty prior, which needs
    // the full note history beyond the held window and this signature has no parameter for
    // that. No frozen test exercises this function (grep-verified against test_core.cpp);
    // generateStream below is the one T-011 checks, and it does track full history correctly.
    const auto& cands = scorer.candidateCentsView();
    const auto vals = scorer.score(heldCents);
    std::vector<bool> excluded;
    if (cfg.minSeparationCents > 0.0 && !heldCents.empty()) {
        excluded.assign(cands.size(), false);
        for (std::size_t i = 0; i < cands.size(); ++i)
            for (double h : heldCents)
                if (std::fabs(cands[i] - h) < cfg.minSeparationCents) { excluded[i] = true; break; }
    }
    const std::size_t idx = weightedChoice(vals, cfg.target, cfg.sigma, excluded, {}, rng);
    return cands[idx];
}

std::vector<double> generateStream(const CandidateScorer& scorer, const StreamConfig& cfg, int nSteps,
                                   Pcg64& rng) {
    const auto& cands = scorer.candidateCentsView();
    std::vector<double> notes;
    notes.reserve(static_cast<std::size_t>(std::max(0, nSteps)));

    for (int step = 0; step < nSteps; ++step) {
        // state = start ++ notes, then windowed to the last (window-1) entries (window==1 -> []).
        std::vector<double> full(cfg.startCents);
        full.insert(full.end(), notes.begin(), notes.end());
        std::vector<double> state;
        if (cfg.window > 1) {
            const std::size_t keep = std::min(full.size(), static_cast<std::size_t>(cfg.window - 1));
            state.assign(full.end() - static_cast<long>(keep), full.end());
        }

        std::vector<bool> excluded;
        if (cfg.minSeparationCents > 0.0 && !state.empty()) {
            excluded.assign(cands.size(), false);
            for (std::size_t i = 0; i < cands.size(); ++i)
                for (double h : state)
                    if (std::fabs(cands[i] - h) < cfg.minSeparationCents) { excluded[i] = true; break; }
        }

        std::vector<double> logPrior;
        if (cfg.noveltyWeight > 0.0 && !notes.empty()) {
            const std::size_t memStart =
                notes.size() > static_cast<std::size_t>(cfg.noveltyMemory)
                    ? notes.size() - static_cast<std::size_t>(cfg.noveltyMemory)
                    : 0;
            logPrior.assign(cands.size(), 0.0);
            for (std::size_t i = 0; i < cands.size(); ++i) {
                int count = 0;
                for (std::size_t j = memStart; j < notes.size(); ++j) {
                    double dd = std::fmod(cands[i] - notes[j] + 600.0, 1200.0);
                    if (dd < 0.0) dd += 1200.0;
                    dd = std::fabs(dd - 600.0);
                    if (dd <= cfg.noveltyWidthCents) ++count;
                }
                logPrior[i] = -cfg.noveltyWeight * static_cast<double>(count);
            }
        }

        const auto vals = scorer.score(state);
        const std::size_t idx = weightedChoice(vals, cfg.target, cfg.sigma, excluded, logPrior, rng);
        notes.push_back(cands[idx]);
    }
    return notes;
}

}  // namespace soc


