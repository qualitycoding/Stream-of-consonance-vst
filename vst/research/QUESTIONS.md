# QUESTION TREE

Leaves name the decision or test they inform. Pruned questions are listed at the end.

1. **Can the model run inside a plugin at all?**
   1.1 What does one note cost in each pitch mode? → D-002, T-013 — *answered, C-012*
   1.2 Which term dominates? → D-004, S-005 — *answered: harmonicity, ~91%*
   1.3 Is there a cheaper exact formulation? → D-004 — *answered, C-006 (rotation identity)*
   1.4 Can generation run on the audio thread? → D-002, S-010 — *answered: no*
2. **What must the C++ port reproduce, and how is that checked?**
   2.1 Which constants and coefficients are normative? → C-001…C-005, T-001…T-006
   2.2 Where are the silent-failure edges? → T-005 (20-cent boundary), T-007 (invalid input)
   2.3 Can streams be bit-identical across languages? → D-005, T-010, T-011 — *yes, via PCG64*
   2.4 What is the cents reference in each fixture? → **R-001**, T-000 — *was undeclared; fixed*
3. **How do the requested controls map onto VST3?**
   3.1 Can a parameter's units change with a mode switch? → D-007 — *no; both must exist*
   3.2 What does automating a start-of-stream value mean? → A-003
   3.3 How late does consonance automation take effect? → A-005 (2 notes)
   3.4 Can a bounce be reproducible with a random generator inside? → A-007, T-018
4. **What does MPE output require?**
   4.1 What bend range preserves microtonal precision? → D-006, C-011 — *±2 semitones*
   4.2 Does Live accept zone configuration from a plugin's MIDI out? → **C-015, R-006** — *unresolved*
   4.3 How are member channels allocated? → S-012
5. **What is the build environment?**
   5.1 Which JUCE version? → D-001, C-013, C-014
   5.2 What are the known build traps on this user's toolchain? → ENVIRONMENT.md §Gotchas

## Pruned
* "Should the model be re-fitted for microtonal timbres?" — informs no decision in scope; the
  root README already carries the caveat and `docs/LISTENING_PROTOCOL.md` owns it.
* "Which interference model is best?" — the composite fixes Hutchinson; changing it changes the
  oracle. Out of scope by D-003.
