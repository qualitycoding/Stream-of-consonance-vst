# Research log — reversible consonance model (gen-20260919T204010Z-consonance-inverse)

Confidence tags: [VERIFIED] retrieved during this run; [UNVERIFIED] from model background knowledge, must be checked in step S0 before any test or code depends on it.

## Sources
R1 [VERIFIED] Harrison & Pearce (2020). Simultaneous consonance in music perception and composition. Psychol Rev 127(2):216-244. https://pmc.ncbi.nlm.nih.gov/articles/PMC7032667/ (DOI 10.1037/rev0000169)
  - Composite model = linear regression on 4 features: Hutchinson-Knopoff interference, H&P harmonicity, corpus-based cultural familiarity, number of notes; r=.88 on Bowling et al. 2018 data; coefficients of similar magnitude; signs: interference -, harmonicity +, familiarity +.
  - Harmonicity: Milne (2013) pitch-class spectral pattern matching; H&P treat cosine-similarity profile as a distribution and use KL divergence from uniform.
  - Familiarity: chord-type counts from Billboard corpus (Burgoyne 2011) -> defined on 12-tone chord types only.
  - Symbolic models generally beat audio-analysis models on their data; other datasets are small (trend-level evidence only).
  - Interference: consonance falls at low registers for the same ratio (pitch-height effect); inharmonic spectra shift consonance minima (Sethares 2005).
  - Software: R package `incon` (+ dycon, har18 sub-packages named in Table 2). License/URL of package NOT retrieved [UNVERIFIED].
R2 [VERIFIED] Harrison & Pearce (2018). An energy-based generative sequence model for testing sensory theories of Western harmony. ISMIR 2018. https://arxiv.org/abs/1807.00790 ; https://www.marcus-pearce.com/assets/papers/HarrisonPearce2018b.pdf
  - Exponential-family energy-based generative model of chord sequences from continuous features (harmonicity; spectral distance; voice-leading distance).
R3 [VERIFIED] Analysis scripts: https://github.com/pmcharrison/inconPaper (R; Essentia 2.1, MIRtoolbox 1.6.1 used).
R4 [VERIFIED] Cousineau, McDermott, Peretz (2012). PNAS 109(48):19858-19863. https://www.pnas.org/doi/10.1073/pnas.1207989109 — amusics show normal beating aversion but no consonance preference => harmonicity matters. (Candidate for user's "2012" memory; unconfirmed.)
R5 [VERIFIED] Milne, Laney, Sharp (2016). Testing a spectral model of tonal affinity with microtonal melodies and inharmonic spectra. Musicae Scientiae. https://journals.sagepub.com/doi/abs/10.1177/1029864915622682 — harmonicity model applied to microtonal/inharmonic stimuli.
R6 [VERIFIED] Erlich, harmonic entropy: http://www.tonalsoft.com/sonic-arts/td/entropy.htm ; https://en.xen.wiki/w/Harmonic_entropy — dyad-level entropy over Farey/mediant probability distribution; a value can be computed per 1-cent interval (see TISMIR 2026 article https://transactions.ismir.net/articles/10.5334/tismir.353).
R7 [UNVERIFIED] Plomp & Levelt (1965), JASA 38:548-560; Sethares (1993, 2005 "Tuning, Timbre, Spectrum, Scale"): pair penalty a_i*a_j*(exp(-b1*s*df)-exp(-b2*s*df)), s=0.24/(0.021*f_min+19), b1=3.5, b2=5.75. Constants recalled from memory — verify (S0).
R8 [UNVERIFIED] Glasberg & Moore (1990) ERB(f)=24.7*(4.37 f/1000 + 1) Hz — used only as a definitional constant inside test_interference.py; verify (S0).
R9 [UNVERIFIED] Hutchinson & Knopoff (1978) via Bigand, Parncutt & Lerdahl (1996) algebraic approximation (cited inside R1, formula not retrieved). Verify (S0).

## Known research gaps (carried into pre-mortem)
G1 Perceptual validity of composite score outside 12-TET Western chords is unstudied in R1.
G2 No published inversion/generation procedure for the composite model was found; the sampler design is this plan's own proposal (energy-based conditioning on a target), not a cited method.
G3 Numerical agreement with the R `incon` implementation is not testable in this environment (no R/CRAN access).

## S0 verification (performed 2026-09-19, during implementation)
Primary source read: MIT-licensed R package `incon` v0.5.0 (https://github.com/pmcharrison/incon, files R/model-dycon.R, R/model-har18.R, R/model-har-2019.R, R/model-corpdiss.R, R/models.R) and `hrep` (R/milne-pc-spectrum.R, R/pc-chord-type.R, R/coded-vec.R).
- R7 VERIFIED: Sethares a=3.5, b=5.75, s=0.24/(0.021*f_lo+19). NOTE: incon's default uses min(a1,a2), not a1*a2 (Sethares 2005/Weisser 2013) — implemented that way.
- R9 VERIFIED (better than recalled): Hutchinson-Knopoff via Mashinter: CBW=1.72*mean_f^0.65, y=|df|/CBW, g=((y/0.25)*exp(1-y/0.25))^2, g=0 for y>1.2, roughness = sum_{i<j} a_i a_j g / sum a^2.
- Vassilakis formula verified (s=0.24/(0.0207 f+18.96)).
- Harmonicity VERIFIED: Milne pc-spectrum, 12 harmonics, weight 1/h^rho, rho=0.75 (composite passes rho=roll_off*0.75), sigma=6.83 cents, 1200 bins, cosine-similarity sweep, KL from uniform in bits: sum p*log2(p*n).
- Composite coefficients VERIFIED (har_19_composite_coef): intercept 0.628434666589357; chord_size 0.422267698605598 (disabled by default in incon); hutch roughness -1.62001025973261; har_18 harmonicity 1.77992362857478; corpus dissonance (-log P) -0.0892234643584134. Defaults num_harmonics=11, roll_off=1.
- Familiarity data VERIFIED: popular_1_pc_chord_type (2048 chord types, McGill Billboard; total count 74,093; add-one smoothing). Encoding: id = 1 + sum 2^(11-j) over non-bass pitch classes j (decode_pc_chord_type).
- R8 (Glasberg-Moore ERB) remains a definitional constant inside test_interference.py only; it did not contradict the Sethares peak (27 Hz at 500 Hz, inside 5%-60% of ERB).
- incon license: MIT (R1 caveat closed). No frozen test was contradicted by S0 findings.
