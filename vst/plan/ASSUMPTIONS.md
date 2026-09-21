# ASSUMPTIONS

Every item was put to the human in the Phase 0.3 intake batch. The human replied: *"I agree to
all default values except add MPE as well as VSTi."* So A-001 carries the human's explicit
amendment; A-002 … A-010 are adopted defaults.

| ID | Assumption | Origin | Consequence if wrong |
|---|---|---|---|
| A-001 | The plugin is a VST3 **instrument** with a built-in additive synth **and** also emits MPE MIDI out. | Human, explicit amendment | If MPE out is unused the work in S-012 is wasted but nothing breaks. |
| A-002 | **One** switch selects both the units of the start parameter and the candidate set: Note ⇒ 12-TET candidates, Frequency ⇒ free 1-cent grid. | Default adopted | If the user wants free-mode candidates while typing a note name, a second switch must be added; parameter list changes break saved sets (R-004). |
| A-003 | The start value seeds the **next** stream start. Changing it mid-stream does nothing until Restart or transport start. | Default adopted | If live re-anchoring was wanted, automation of Start Note appears inert and will read as a bug. |
| A-004 | Ranges: Start Note = MIDI 0–127 with A4 = 440 Hz; Start Frequency = 20–5000 Hz exponential; Consonance = −0.7 … 3.1 linear. | Default adopted | Targets outside the fitted range produce saturated, uninteresting streams. |
| A-005 | Lookahead depth is 2 notes; the consonance target is latched when generation of a note begins. | Default adopted | Automation appears to lag by two notes. Deeper = safer, shallower = riskier. |
| A-006 | Note timing is tempo-synced, default ¼ note, with a sliding window of 4 sounding notes. | Default adopted | At very fast divisions the generator cannot keep up in free mode (R-002). |
| A-007 | `seed` is saved with the preset but **not** automatable; the generator is clocked off the host playhead so bounces repeat. | Default adopted | Without this, no two bounces match and SC-4 is unmeetable. |
| A-008 | Windows x64 only, VST3 + Standalone, JUCE toolchain matching the user's existing microtonal-guitar project. | Default adopted | macOS/AU users are unserved; adding them later is additive, not a rewrite. |
| A-009 | `sigma` is also exposed as an automatable parameter. | Proposed by planner, not objected to | If unwanted it is one parameter too many; harmless. |
| A-010 | Distribution is personal/source-only, so JUCE's AGPLv3 option is acceptable. | Default adopted | Closed-source binary distribution would require a JUCE commercial licence — see R-007. |
