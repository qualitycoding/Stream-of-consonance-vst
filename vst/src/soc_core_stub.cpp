// STUB IMPLEMENTATION — every function throws NotImplemented.
//
// Purpose: let the frozen test suite compile and fail *cleanly* (Phase 2.3 red verification),
// proving the tests exercise real behaviour rather than crashing on missing symbols.
// The implementer replaces this file with soc_core.cpp; it is removed from the build at S-006.

#include "soc_core.h"

#include <string>

namespace soc {

const std::vector<double> kJustIntervalsCents = {};

Timbre harmonicTimbre(int, double) { throw NotImplemented("harmonicTimbre"); }

double hutchinsonRoughness(const std::vector<double>&, const Timbre&, double) {
    throw NotImplemented("hutchinsonRoughness");
}

double harmonicityBits(const std::vector<double>&, const Timbre&) {
    throw NotImplemented("harmonicityBits");
}

std::optional<double> familiarityLogP(const std::vector<double>&) {
    throw NotImplemented("familiarityLogP");
}

double neutralLogProb() { throw NotImplemented("neutralLogProb"); }

double compositeScore(const std::vector<double>&, const Timbre&, const Weights&) {
    throw NotImplemented("compositeScore");
}

struct CandidateScorer::Impl {};

CandidateScorer::CandidateScorer(const Timbre&, const std::vector<double>&, double, const Weights&)
    : impl_(nullptr) {
    throw NotImplemented("CandidateScorer::CandidateScorer");
}
CandidateScorer::~CandidateScorer() { delete impl_; }
std::vector<double> CandidateScorer::score(const std::vector<double>&) const {
    throw NotImplemented("CandidateScorer::score");
}
std::size_t CandidateScorer::candidateCount() const { throw NotImplemented("CandidateScorer::candidateCount"); }
const std::vector<double>& CandidateScorer::candidateCentsView() const {
    throw NotImplemented("CandidateScorer::candidateCentsView");
}

std::vector<double> candidateCents(const PitchSetSpec&) { throw NotImplemented("candidateCents"); }

Pcg64 Pcg64::fromNumpySeed(std::uint64_t) { throw NotImplemented("Pcg64::fromNumpySeed"); }
Pcg64 Pcg64::fromState(const std::string&, const std::string&) { throw NotImplemented("Pcg64::fromState"); }
std::uint64_t Pcg64::nextUint64() { throw NotImplemented("Pcg64::nextUint64"); }
double Pcg64::nextDouble() { throw NotImplemented("Pcg64::nextDouble"); }

double sampleNext(const CandidateScorer&, const std::vector<double>&, const StreamConfig&, Pcg64&) {
    throw NotImplemented("sampleNext");
}

std::vector<double> generateStream(const CandidateScorer&, const StreamConfig&, int, Pcg64&) {
    throw NotImplemented("generateStream");
}

MpeNote encodeMpe(double, int, double) { throw NotImplemented("encodeMpe"); }
double decodeMpeHz(const MpeNote&, double) { throw NotImplemented("decodeMpeHz"); }

}  // namespace soc
