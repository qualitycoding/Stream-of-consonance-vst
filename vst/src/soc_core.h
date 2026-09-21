// Stream-of-Consonance VST — core model port, public interface.
//
// This header is the CONTRACT. It is frozen alongside tests/FROZEN_MANIFEST.sha256: the
// implementer fills in soc_core.cpp and must not change these signatures. Every function
// mirrors a Python function in the `consonance` package, which is the oracle (see
// tests/fixtures/). JUCE must not be included from this file — the core is deliberately
// framework-free so it can be unit-tested without a plugin host.
//
// Units: `cents` are always relative to an explicit reference in Hz. The generator reference
// is 220 Hz; the model's internal pitch-class origin (C4, 261.6255653005986 Hz) is a separate
// constant used only inside the harmonicity term. Confusing the two is silent and costs up to
// 0.08 score units — see premortem R-001.

#pragma once

#include <cstdint>
#include <optional>
#include <stdexcept>
#include <vector>

namespace soc {

inline constexpr double kModelRefHz = 261.6255653005986;   // C4: pitch-class origin only
inline constexpr double kGeneratorRefHz = 220.0;           // A3: cents reference for streams
inline constexpr double kMaxHz = 20000.0;
inline constexpr double kHarmonicitySigmaCents = 6.83;
inline constexpr double kHarmonicityRho = 0.75;
inline constexpr int kHarmonicityBins = 1200;              // 1-cent grid over an octave
inline constexpr double kFamiliarityToleranceCents = 20.0;

struct NotImplemented : std::logic_error {
    explicit NotImplemented(const char* what) : std::logic_error(std::string("not implemented: ") + what) {}
};

// ---------------------------------------------------------------------------------------
// Timbre
// ---------------------------------------------------------------------------------------
struct Timbre {
    std::vector<double> ratios;
    std::vector<double> amps;
    bool operator==(const Timbre& o) const { return ratios == o.ratios && amps == o.amps; }
};

// incon composite defaults: 11 harmonics, amplitude 1/h^rollOff.
Timbre harmonicTimbre(int nHarmonics = 11, double rollOff = 1.0);

// ---------------------------------------------------------------------------------------
// Model terms (each mirrors one Python module)
// ---------------------------------------------------------------------------------------
struct Weights {
    double interference = -1.62001025973261;
    double harmonicity = 1.77992362857478;
    double familiarity = 0.0892234643584134;   // applied to log P
    double nNotes = 0.0;                       // disabled, as in incon
    double intercept = 0.628434666589357;
};

// Hutchinson & Knopoff roughness of simultaneous fundamentals. consonance/interference.py.
double hutchinsonRoughness(const std::vector<double>& freqsHz, const Timbre&, double maxHz = kMaxHz);

// Pitch-class harmonicity in bits. Input cents may use any reference (transposition invariant).
// consonance/harmonicity.py.
double harmonicityBits(const std::vector<double>& cents, const Timbre&);

// Corpus familiarity: log P of the bass-relative 12-TET pitch-class chord type, or nullopt when
// any interval sits further than kFamiliarityToleranceCents from equal temperament.
// consonance/familiarity.py.
std::optional<double> familiarityLogP(const std::vector<double>& cents);
double neutralLogProb();

// Full composite score of one chord. consonance/composite.py::CompositeModel::score.
double compositeScore(const std::vector<double>& freqsHz, const Timbre&, const Weights& = {});

// ---------------------------------------------------------------------------------------
// Hot path: score held ∪ {candidate} for every candidate.
// This is >99% of generation cost. See plan/DECISIONS.md D-004 (rotation identity) — every
// candidate's pitch-class spectrum is a circular rotation of one precomputed spectrum.
// consonance/composite.py::CompositeModel::score_with_candidates.
// ---------------------------------------------------------------------------------------
class CandidateScorer {
public:
    CandidateScorer(const Timbre&, const std::vector<double>& candidateCents,
                    double refHz = kGeneratorRefHz, const Weights& = {});
    ~CandidateScorer();
    // Returns one score per candidate, in candidate order.
    std::vector<double> score(const std::vector<double>& heldCents) const;
    std::size_t candidateCount() const;
    // Read-only view of the candidate cents this scorer was built with, in the same order as
    // score()'s output. Added post-freeze; see ../INTERFACE_AMENDMENT.md -- generateStream needs
    // this to report which candidate was actually chosen, and nothing else in the frozen
    // contract carries it.
    const std::vector<double>& candidateCentsView() const;
private:
    struct Impl;
    Impl* impl_;
};

// ---------------------------------------------------------------------------------------
// Pitch sets. consonance/pitchset.py.
// ---------------------------------------------------------------------------------------
enum class PitchMode { Standard, Free };

struct PitchSetSpec {
    PitchMode mode = PitchMode::Standard;
    double lowCents = -600.0;
    double highCents = 1800.0;
    int edo = 12;
    double resolutionCents = 1.0;
    double offsetCents = 0.0;
    std::vector<double> snapTo;   // empty = uniform grid
};
std::vector<double> candidateCents(const PitchSetSpec&);
extern const std::vector<double> kJustIntervalsCents;

// ---------------------------------------------------------------------------------------
// numpy-compatible PCG64. Required for bit-identical streams; see D-005.
// Seeded either from a numpy SeedSequence-equivalent seed, or directly from a state pair
// recorded in tests/fixtures/rng.json (the fallback that avoids reimplementing SeedSequence).
// ---------------------------------------------------------------------------------------
class Pcg64 {
public:
    static Pcg64 fromNumpySeed(std::uint64_t seed);
    static Pcg64 fromState(const std::string& state128Dec, const std::string& inc128Dec);
    std::uint64_t nextUint64();
    double nextDouble();                 // (x >> 11) * 2^-53, as numpy Generator.random()
private:
    __uint128_t state_ = 0, inc_ = 0;
};

// ---------------------------------------------------------------------------------------
// Sampler / stream. consonance/sampler.py.
// ---------------------------------------------------------------------------------------
struct StreamConfig {
    double target = 1.6;
    double sigma = 0.1;
    int window = 4;
    double minSeparationCents = 30.0;
    double noveltyWeight = 1.5;
    int noveltyMemory = 8;
    double noveltyWidthCents = 25.0;
    double tolerance = 0.25;
    std::vector<double> startCents{0.0, 700.0};
};

// One note. `heldCents` is the sounding sonority; returns the chosen candidate in cents.
double sampleNext(const CandidateScorer&, const std::vector<double>& heldCents,
                  const StreamConfig&, Pcg64& rng);

// n notes, matching generate_stream() exactly for the same seed and configuration.
std::vector<double> generateStream(const CandidateScorer&, const StreamConfig&, int nSteps, Pcg64& rng);

// ---------------------------------------------------------------------------------------
// MPE encoding. See D-006: free mode needs per-note pitch bend on its own channel.
// ---------------------------------------------------------------------------------------
struct MpeNote {
    int channel = 2;          // 1-based; ch 1 is the lower-zone master, members are 2-16
    int noteNumber = 60;
    int pitchBend14 = 8192;   // 0..16383, centre 8192
};
// Split a frequency into the nearest 12-TET note plus a pitch bend, given the zone's bend range.
MpeNote encodeMpe(double freqHz, int channel, double bendRangeSemitones = 2.0);
double decodeMpeHz(const MpeNote&, double bendRangeSemitones = 2.0);

}  // namespace soc
