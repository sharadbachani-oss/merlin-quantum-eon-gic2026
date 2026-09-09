# Merlin Digital — GIC 2026 E.ON Enterprise Track

| | |
|---|---|
| **Team** | Merlin Digital |
| **Project** | The leftover spectrum classical continuation cannot hold |
| **Track** | E.ON — distribution-grid expansion / congestion risk |
| **Write-up** | `EON_REPORT_v4.md` (v5.0 — one section per official outcome) |
| **Exhibit** | `QUANTUM_ADVANTAGE_EXHIBIT.md` |
| **Prior result** | GIC 2026 — **dual-track finalist** (Mitsubishi/AIST materials track); same instrument, same advantage *class* (of route) |

## Official outcomes

1. **Hard instances, 6–26 binaries** — HiGHS times out at 20 / 26 (28% / 34% gap).
2. **20-qubit framework operator on the grid** — real-time leftover \(S(\omega)\) ranks certified > deg-2 > MILP > no-build. Imaginary-time continuation misses the certified line (0.270 vs 0.222). Dropping \(A_6\) bonds makes every plan \(\Delta L=+0.514\). 10q QAOA already flown on ibm_marrakesh.
3. **Named line set** — seven lines, capex 11.42, congestion 77.125 → 1.440 (−98.1%).
4. **MPS poor objective** — TT-SVD of the true cost: every \(\chi<16\) returns the wrong plan (+1.9% to +9.1%). Hardware / Dirac return the exact plan.

`python verify.py` then `python eon_rubric_mps.py`.

## Verify the headline numbers (CPU, ~1 min)

```
python verify.py
```

Expected: two-build, residuals, Schmidt, line set, MPS \(\chi\)-sweep, dynamics-crossing gates all PASS.

Full rebuild of the v4 evidence pack (~45 s):

```
python eon_v4_advantage.py
```

Dynamics crossing (~5 min, no credentials):

```
python eon_dynamics_crossing.py
```

Full-\(k\) leftover \(\to S(\omega)\) on hardware is **not flown**. One-command (retrieve only; no paid submit):

```
python eon_full_k_leftover.py
```

## What is in this package

```
EON_REPORT_v4.md                 the write-up (v5.0)
QUANTUM_ADVANTAGE_EXHIBIT.md     standalone advantage-of-route exhibit
RECEIPTS.md                      claim → file → job-ID (or NOT_FLOWN)
EON_V5_PLAN.md                   internal upgrade plan
README.md                        this file
verify.py                        credential-free audit
eon_core.py                      referee + instance generator + MILP
eon_v4_advantage.py              two-build, held-out, Schmidt
eon_rubric_mps.py                named lines + MPS-on-true-cost sweep
eon_nisq_field.py                20q operator (Outcome 2)
eon_dynamics_crossing.py         leftover S(ω) vs continuation / A6-off
eon_full_k_leftover.py           full-k leftover → S(ω): retrieve + optional submit
EON_FRONTIER_CARD.md             algorithm card
results/                         frozen JSONs behind every headline number
```

## Compatibility (challenge §5.3)

All circuits are Qiskit `QuantumCircuit`; hardware runs use
`qiskit-ibm-runtime` SamplerV2. E.ON can re-execute any flight by setting
`IBM_QUANTUM_CRN` and pointing the script at a backend. Dirac-3 polynomial
files ship for independent resubmission. Full replay fits inside the
brief's few-hour runtime limit.

## Discipline

Frozen pre-registration before hardware. One physics referee for every
solver — classical and quantum alike — so every comparison in the
write-up shares one grader, from the MILP timeout on eon57_util to the
Dirac plan that beats it. Every number regenerates from the frozen JSONs
in `results/`. Jobs that were not run are marked `NOT_FLOWN` with a
protocol and expected signature — never a fake job ID.

## Note on scope

The advantage is **of route**, stated and bounded: real-time leftover
\(S(\omega)\) versus ill-posed imaginary-time continuation and
\(A_6\)-off dynamics, on today's 20-qubit operator. Hardware two-point
\(\Delta L\) ranking is **partial** (degree-2 is device-dependent).
A full-\(k\) leftover series on a device, and the Aquila analog map,
are protocols in this package — not receipts. This is not a supremacy
claim at 10 binaries and not a 100-qubit hardware-vs-MPS result.
