// FROZEN — DO NOT MODIFY
//
// Core-model conformance tests for the Stream-of-Consonance VST.
// Every assertion here compares the C++ port against golden values produced by the frozen
// Python `consonance` package (tests/fixtures/, oracle). No live network, no randomness beyond
// the seeded PCG64 the fixtures pin, no wall-clock dependence except T-013 which is explicitly
// a performance budget.
//
// Changing any test in this file requires the unfreeze procedure in tests/FROZEN.md.
// Run: see tests/cpp/Makefile. Red verification (Phase 2.3) is recorded in
// research/spikes/red_verify_output.txt.

#include "../../src/soc_core.h"
#include "../../third_party/json.hpp"

#include <chrono>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <functional>
#include <string>
#include <vector>

using nlohmann::json;

// ---------------------------------------------------------------------------------------
// Minimal harness. A test "passes" only if it runs to completion with no failed checks;
// an escaping exception (including NotImplemented) is a failure, never a crash.
// ---------------------------------------------------------------------------------------
namespace {

int g_checks = 0, g_failed_checks = 0;
std::string g_current;

void check(bool ok, const std::string& what) {
    ++g_checks;
    if (!ok) {
        ++g_failed_checks;
        if (g_failed_checks < 200) std::printf("      FAIL %s: %s\n", g_current.c_str(), what.c_str());
    }
}

void checkClose(double got, double want, double tol, const std::string& what) {
    const double d = std::fabs(got - want);
    check(d <= tol, what + " (got " + std::to_string(got) + ", want " + std::to_string(want) +
                        ", |d|=" + std::to_string(d) + " > " + std::to_string(tol) + ")");
}

std::string fixtureDir() {
    if (const char* e = std::getenv("SOC_FIXTURES")) return std::string(e);
    return "../fixtures";
}

json loadFixture(const std::string& name) {
    const std::string path = fixtureDir() + "/" + name;
    std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open fixture: " + path);
    json j;
    in >> j;
    return j;
}

std::vector<double> hzFromCents(const std::vector<double>& cents, double refHz) {
    std::vector<double> out;
    out.reserve(cents.size());
    for (double c : cents) out.push_back(refHz * std::pow(2.0, c / 1200.0));
    return out;
}

struct Test {
    const char* id;
    const char* doc;
    std::function<void()> fn;
};
std::vector<Test>& registry() { static std::vector<Test> r; return r; }
struct Reg {
    Reg(const char* id, const char* doc, std::function<void()> fn) { registry().push_back({id, doc, std::move(fn)}); }
};
#define TEST(id, doc) \
    static void test_##id(); \
    static Reg reg_##id(#id, doc, test_##id); \
    static void test_##id()

// ---------------------------------------------------------------------------------------
// T-001 .. T-007: model terms against the Python oracle.
// ---------------------------------------------------------------------------------------

TEST(T_000, "Every fixture loads, declares its cents reference, and is non-empty. Calls no soc:: function, so it PASSES in the red state and proves the other tests' inputs exist. SC-1; R-001.")
{
    // Without this, a test that throws on its first soc:: call never reaches its fixture, and a
    // missing or malformed fixture would hide behind a not-implemented failure.
    const char* names[] = {"timbre.json", "interference.json", "harmonicity.json", "familiarity.json",
                           "composite.json", "candidates.json", "score_with_candidates.json",
                           "streams.json", "mpe.json", "rng.json"};
    for (const char* n : names) {
        const json f = loadFixture(n);
        check(f.contains("ref_hz"), std::string(n) + " must declare ref_hz");
        if (f.contains("ref_hz")) checkClose(f["ref_hz"].get<double>(), 220.0, 0.0, std::string(n) + " ref_hz");
        if (f.contains("cases")) check(!f["cases"].empty(), std::string(n) + " has cases");
    }
}

TEST(T_001, "harmonicTimbre(11, 1.0) reproduces the incon default spectrum. Enforces SC-1; claims C-001.")
{
    const json f = loadFixture("timbre.json");
    const soc::Timbre t = soc::harmonicTimbre(f["n_harmonics"].get<int>(), f["roll_off"].get<double>());
    const auto ratios = f["ratios"].get<std::vector<double>>();
    const auto amps = f["amps"].get<std::vector<double>>();
    check(t.ratios.size() == ratios.size(), "ratio count");
    check(t.amps.size() == amps.size(), "amp count");
    for (std::size_t i = 0; i < ratios.size() && i < t.ratios.size(); ++i) {
        checkClose(t.ratios[i], ratios[i], 0.0, "ratio[" + std::to_string(i) + "]");
        checkClose(t.amps[i], amps[i], 1e-15, "amp[" + std::to_string(i) + "]");
    }
}

TEST(T_002, "Hutchinson-Knopoff roughness matches the oracle for 13 chords incl. clusters and wide spacings. SC-1; C-002.")
{
    const json f = loadFixture("interference.json");
    const double ref = f["ref_hz"].get<double>(), tol = f["tolerance_abs"].get<double>();
    const soc::Timbre t = soc::harmonicTimbre(11, 1.0);
    for (const auto& c : f["cases"]) {
        const auto hz = hzFromCents(c["cents"].get<std::vector<double>>(), ref);
        checkClose(soc::hutchinsonRoughness(hz, t), c["hutchinson"].get<double>(), tol,
                   "roughness " + c["name"].get<std::string>());
    }
}

TEST(T_003, "Pitch-class harmonicity in bits matches the oracle, including microtonal chords. SC-1; C-003, C-006.")
{
    const json f = loadFixture("harmonicity.json");
    const double tol = f["tolerance_abs"].get<double>();
    const soc::Timbre t = soc::harmonicTimbre(11, 1.0);
    for (const auto& c : f["cases"]) {
        checkClose(soc::harmonicityBits(c["cents"].get<std::vector<double>>(), t),
                   c["bits"].get<double>(), tol, "harmonicity " + c["name"].get<std::string>());
    }
}

TEST(T_004, "Familiarity returns log P for 12-TET chords and nullopt beyond the 20-cent tolerance. SC-1; C-004.")
{
    const json f = loadFixture("familiarity.json");
    const double tol = f["tolerance_abs"].get<double>();
    for (const auto& c : f["cases"]) {
        const auto got = soc::familiarityLogP(c["cents"].get<std::vector<double>>());
        const bool supported = c["supported"].get<bool>();
        check(got.has_value() == supported, "supported flag " + c["name"].get<std::string>());
        if (supported && got.has_value())
            checkClose(*got, c["log_prob"].get<double>(), tol, "log_prob " + c["name"].get<std::string>());
    }
    checkClose(soc::neutralLogProb(), f["neutral_log_prob"].get<double>(), tol, "neutral_log_prob");
}

TEST(T_005, "Familiarity boundary: 19 cents sharp is supported, 21 cents sharp is not. SC-1; C-004.")
{
    // Guards the exact inequality at the tolerance edge (> vs >=), a classic off-by-one.
    check(soc::familiarityLogP({0.0, 400.0, 719.0}).has_value(), "19 cents must be inside tolerance");
    check(!soc::familiarityLogP({0.0, 400.0, 721.0}).has_value(), "21 cents must be outside tolerance");
}

TEST(T_006, "Composite score matches the oracle for all fixture chords. SC-1; C-005.")
{
    const json f = loadFixture("composite.json");
    const double ref = f["ref_hz"].get<double>(), tol = f["tolerance_abs"].get<double>();
    const soc::Timbre t = soc::harmonicTimbre(11, 1.0);
    for (const auto& c : f["cases"]) {
        const auto hz = hzFromCents(c["cents"].get<std::vector<double>>(), ref);
        checkClose(soc::compositeScore(hz, t), c["score"].get<double>(), tol,
                   "score " + c["name"].get<std::string>());
    }
}

TEST(T_007, "Invalid input is rejected rather than silently scored. SC-1; R-008.")
{
    const soc::Timbre t = soc::harmonicTimbre(11, 1.0);
    bool threwEmpty = false, threwNeg = false, threwNan = false;
    try { soc::compositeScore({}, t); } catch (const soc::NotImplemented&) { throw; } catch (...) { threwEmpty = true; }
    try { soc::compositeScore({220.0, -1.0}, t); } catch (const soc::NotImplemented&) { throw; } catch (...) { threwNeg = true; }
    try { soc::compositeScore({220.0, std::nan("")}, t); } catch (const soc::NotImplemented&) { throw; } catch (...) { threwNan = true; }
    check(threwEmpty, "empty chord must throw");
    check(threwNeg, "non-positive frequency must throw");
    check(threwNan, "NaN frequency must throw");
}

// ---------------------------------------------------------------------------------------
// T-008 .. T-009: pitch sets and the hot path.
// ---------------------------------------------------------------------------------------

TEST(T_008, "candidateCents reproduces every fixture pitch set, by count, endpoints and digest. SC-2; C-007.")
{
    const json f = loadFixture("candidates.json");
    for (const auto& c : f["cases"]) {
        soc::PitchSetSpec spec;
        spec.mode = c["mode"].get<std::string>() == "standard" ? soc::PitchMode::Standard : soc::PitchMode::Free;
        spec.lowCents = c["low_cents"].get<double>();
        spec.highCents = c["high_cents"].get<double>();
        const auto& p = c["params"];
        if (p.contains("edo")) spec.edo = p["edo"].get<int>();
        if (p.contains("resolution_cents")) spec.resolutionCents = p["resolution_cents"].get<double>();
        if (p.contains("offset_cents")) spec.offsetCents = p["offset_cents"].get<double>();
        if (p.contains("snap_to")) spec.snapTo = p["snap_to"].get<std::vector<double>>();
        const auto got = soc::candidateCents(spec);
        const std::string name = c["name"].get<std::string>();
        check(got.size() == c["n"].get<std::size_t>(), "candidate count " + name);
        if (!got.empty()) {
            checkClose(got.front(), c["first"].get<double>(), 1e-9, "first " + name);
            checkClose(got.back(), c["last"].get<double>(), 1e-9, "last " + name);
        }
        const auto sample = c["sample"].get<std::vector<double>>();
        for (std::size_t i = 0; i < sample.size() && i < got.size(); ++i)
            checkClose(got[i], sample[i], 1e-9, "candidate[" + std::to_string(i) + "] " + name);
    }
}

TEST(T_009, "CandidateScorer reproduces score_with_candidates elementwise for every held set. SC-1, SC-3; C-005, C-006.")
{
    const json f = loadFixture("score_with_candidates.json");
    const double ref = f["ref_hz"].get<double>(), tol = f["tolerance_abs"].get<double>();
    const soc::Timbre t = soc::harmonicTimbre(11, 1.0);
    for (const auto& c : f["cases"]) {
        soc::PitchSetSpec spec;
        spec.mode = c["candidate_mode"].get<std::string>() == "standard" ? soc::PitchMode::Standard : soc::PitchMode::Free;
        const auto& p = c["candidate_params"];
        if (p.contains("edo")) spec.edo = p["edo"].get<int>();
        if (p.contains("resolution_cents")) spec.resolutionCents = p["resolution_cents"].get<double>();
        if (p.contains("snap_to")) spec.snapTo = p["snap_to"].get<std::vector<double>>();
        const soc::CandidateScorer scorer(t, soc::candidateCents(spec), ref);
        const auto got = scorer.score(c["held_cents"].get<std::vector<double>>());
        const auto want = c["values"].get<std::vector<double>>();
        const std::string name = c["name"].get<std::string>();
        check(got.size() == want.size(), "value count " + name);
        for (std::size_t i = 0; i < want.size() && i < got.size(); ++i)
            checkClose(got[i], want[i], tol, "value[" + std::to_string(i) + "] " + name);
    }
}

// ---------------------------------------------------------------------------------------
// T-010 .. T-011: RNG conformance and end-to-end stream determinism.
// ---------------------------------------------------------------------------------------

TEST(T_010, "PCG64 reproduces numpy Generator.random() bit-for-bit for every fixture seed. SC-4; C-008.")
{
    const json f = loadFixture("rng.json");
    for (const auto& c : f["cases"]) {
        auto rng = soc::Pcg64::fromState(c["initial_state_hex"].get<std::string>(),
                                         c["initial_inc_hex"].get<std::string>());
        const auto want = c["first_doubles"].get<std::vector<double>>();
        for (std::size_t i = 0; i < want.size(); ++i)
            checkClose(rng.nextDouble(), want[i], 0.0, "draw[" + std::to_string(i) + "] seed " +
                                                          std::to_string(c["seed"].get<int>()));
    }
}

TEST(T_011, "generateStream reproduces the oracle note sequences exactly for every fixture stream. SC-4; C-009.")
{
    const json f = loadFixture("streams.json");
    const double tolCents = f["tolerance_cents"].get<double>();
    const double tolScore = f["tolerance_score_abs"].get<double>();
    const soc::Timbre t = soc::harmonicTimbre(11, 1.0);
    for (const auto& c : f["cases"]) {
        soc::PitchSetSpec spec;
        const auto& g = c["generator"];
        spec.mode = g["pitch_mode"].get<std::string>() == "standard" ? soc::PitchMode::Standard : soc::PitchMode::Free;
        if (g.contains("edo")) spec.edo = g["edo"].get<int>();
        if (g.contains("resolution_cents")) spec.resolutionCents = g["resolution_cents"].get<double>();
        if (g.contains("snap_to")) spec.snapTo = g["snap_to"].get<std::vector<double>>();

        soc::StreamConfig cfg;
        cfg.target = c["call"]["target"].get<double>();
        cfg.startCents = c["call"]["start"].get<std::vector<double>>();
        cfg.sigma = c["sigma"].get<double>();
        cfg.window = c["window"].get<int>();
        cfg.minSeparationCents = c["min_separation_cents"].get<double>();
        cfg.noveltyWeight = c["novelty_weight"].get<double>();

        const soc::CandidateScorer scorer(t, soc::candidateCents(spec), f["ref_hz"].get<double>());
        auto rng = soc::Pcg64::fromNumpySeed(c["call"]["seed"].get<std::uint64_t>());
        const auto got = soc::generateStream(scorer, cfg, c["call"]["n_steps"].get<int>(), rng);
        const auto want = c["notes_cents"].get<std::vector<double>>();
        const std::string name = c["name"].get<std::string>();
        check(got.size() == want.size(), "note count " + name);
        for (std::size_t i = 0; i < want.size() && i < got.size(); ++i)
            checkClose(got[i], want[i], tolCents, "note[" + std::to_string(i) + "] " + name);

        // The realised consonance of each sounding window must also match, not just the notes.
        const auto wantScores = c["realised_scores"].get<std::vector<double>>();
        std::vector<double> state = cfg.startCents;
        for (std::size_t i = 0; i < wantScores.size() && i < got.size(); ++i) {
            state.push_back(got[i]);
            if ((int)state.size() > cfg.window) state.erase(state.begin(), state.end() - cfg.window);
            checkClose(soc::compositeScore(hzFromCents(state, f["ref_hz"].get<double>()), t),
                       wantScores[i], tolScore, "realised[" + std::to_string(i) + "] " + name);
        }
    }
}

// ---------------------------------------------------------------------------------------
// T-012: MPE encoding.
// ---------------------------------------------------------------------------------------

TEST(T_012, "MPE note+bend encoding lands within 0.05 cents and round-trips. SC-5; C-010, C-011.")
{
    const json f = loadFixture("mpe.json");
    const double ref = f["ref_hz"].get<double>();
    const double range = f["bend_range_semitones"].get<double>();
    const double maxErr = f["max_error_cents"].get<double>();
    for (const auto& c : f["cases"]) {
        const double hz = c["freq_hz"].get<double>();
        const soc::MpeNote n = soc::encodeMpe(hz, 2, range);
        check(n.noteNumber == c["midi_note"].get<int>(), "midi note for " + std::to_string(hz));
        check(n.pitchBend14 == c["bend14"].get<int>(), "bend14 for " + std::to_string(hz));
        check(n.channel >= 2 && n.channel <= 16, "member channel must be 2-16");
        check(n.pitchBend14 >= 0 && n.pitchBend14 <= 16383, "bend must be 14-bit");
        const double back = soc::decodeMpeHz(n, range);
        checkClose(1200.0 * std::log2(back / hz), 0.0, maxErr, "round-trip cents for " + std::to_string(hz));
    }
    (void)ref;
}

// ---------------------------------------------------------------------------------------
// T-013: operational budget. The generator thread must stay ahead of the note clock.
// ---------------------------------------------------------------------------------------

TEST(T_013, "Free-mode 1-cent scoring of 2401 candidates completes within the 40 ms budget. SC-3; C-012, R-002.")
{
    const soc::Timbre t = soc::harmonicTimbre(11, 1.0);
    soc::PitchSetSpec spec;
    spec.mode = soc::PitchMode::Free;
    spec.resolutionCents = 1.0;
    const soc::CandidateScorer scorer(t, soc::candidateCents(spec), soc::kGeneratorRefHz);
    const std::vector<double> held{0.0, 700.0, 400.0};
    scorer.score(held);  // warm caches; not timed
    const auto t0 = std::chrono::steady_clock::now();
    const int reps = 10;
    for (int i = 0; i < reps; ++i) (void)scorer.score(held);
    const double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count() / reps;
    std::printf("      [T-013] %.2f ms per candidate-scoring pass\n", ms);
    check(ms < 40.0, "scoring pass must stay under the 40 ms budget, measured " + std::to_string(ms) + " ms");
}

TEST(T_014, "Scoring with an empty held set is valid and equals scoring each candidate alone. SC-1; boundary case.")
{
    const soc::Timbre t = soc::harmonicTimbre(11, 1.0);
    soc::PitchSetSpec spec;  // standard 12-TET, 25 candidates
    const auto cands = soc::candidateCents(spec);
    const soc::CandidateScorer scorer(t, cands, soc::kGeneratorRefHz);
    const auto got = scorer.score({});
    check(got.size() == cands.size(), "one value per candidate for empty held set");
    for (std::size_t i = 0; i < cands.size() && i < got.size(); ++i) {
        const double alone = soc::compositeScore(hzFromCents({cands[i]}, soc::kGeneratorRefHz), t);
        checkClose(got[i], alone, 1e-9, "empty-held candidate[" + std::to_string(i) + "]");
    }
}

}  // namespace

int main() {
    int failedTests = 0;
    std::printf("Stream-of-Consonance core conformance suite (%zu tests)\n", registry().size());
    for (const auto& t : registry()) {
        g_current = t.id;
        const int before = g_failed_checks;
        std::string verdict;
        try {
            t.fn();
            verdict = (g_failed_checks == before) ? "PASS" : "FAIL";
        } catch (const soc::NotImplemented& e) {
            verdict = std::string("FAIL (not implemented: ") + e.what() + ")";
        } catch (const std::exception& e) {
            verdict = std::string("FAIL (exception: ") + e.what() + ")";
        } catch (...) {
            verdict = "FAIL (unknown exception)";
        }
        if (verdict.rfind("PASS", 0) != 0) ++failedTests;
        std::printf("  %-7s %s\n           %s\n", t.id, verdict.c_str(), t.doc);
    }
    std::printf("\n%d/%zu tests passed, %d/%d checks passed\n",
                (int)registry().size() - failedTests, registry().size(),
                g_checks - g_failed_checks, g_checks);
    return failedTests == 0 ? 0 : 1;
}
