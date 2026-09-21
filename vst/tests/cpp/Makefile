# Core conformance suite. Deliberately JUCE-free and CMake-free so the model port can be
# tested on any machine with a C++17 compiler, including CI containers without an audio stack.
#
#   make            build the suite against the stub (expect every test to FAIL: red state)
#   make run        build and run
#   make IMPL=../../src/soc_core.cpp run     build and run against the real implementation
#
# The plugin-level suite (tests/cpp/test_plugin.cpp) needs JUCE and is built by the CMake
# target instead; see plan/PLAN.md S-009.

CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O3 -Wall -Wextra -Wno-unused-parameter
IMPL     ?= ../../src/soc_core_stub.cpp
BIN      := test_core
FIXTURES ?= ../fixtures

$(BIN): test_core.cpp $(IMPL) ../../src/soc_core.h ../../third_party/json.hpp
	$(CXX) $(CXXFLAGS) -o $(BIN) test_core.cpp $(IMPL)

.PHONY: run clean red
run: $(BIN)
	SOC_FIXTURES=$(FIXTURES) ./$(BIN)

# Phase 2.3 red verification: against the stub the suite must fail, and must fail because
# functions are unimplemented -- not because of a compile error or a missing fixture.
red: $(BIN)
	@SOC_FIXTURES=$(FIXTURES) ./$(BIN) > red_output.txt 2>&1; \
	 status=$$?; \
	 cat red_output.txt; \
	 if [ $$status -eq 0 ]; then echo "RED VERIFY FAILED: suite passed against the stub"; exit 1; fi; \
	 if grep -q "cannot open fixture" red_output.txt; then echo "RED VERIFY FAILED: missing fixtures"; exit 1; fi; \
	 if ! grep -q "not implemented" red_output.txt; then echo "RED VERIFY FAILED: no not-implemented failures"; exit 1; fi; \
	 if ! grep -q "T_000   PASS" red_output.txt; then echo "RED VERIFY FAILED: fixture-integrity test T-000 did not pass"; exit 1; fi; \
	 echo "RED VERIFY OK: suite compiles, loads fixtures, and fails only on unimplemented functions"

clean:
	rm -f $(BIN) red_output.txt
