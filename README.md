# Merlin Digital — GIC 2026 E.ON Enterprise Track

| | |
|---|---|
| **Team** | Merlin Digital |
| **Project** | The Congestion Objective Classical Solvers Cannot Hold |
| **Track** | E.ON — distribution-grid expansion / congestion risk |
| **Write-up** | `EON_REPORT_v4.md` (one section per official outcome) |
| **Exhibit** | `QUANTUM_ADVANTAGE_EXHIBIT.md` |
| **Prior result** | GIC 2026 — **dual-track finalist** (Mitsubishi/AIST materials track); same instrument, sharper advantage class |

## Official outcomes

1. **Hard instances, 6–26 binaries** — HiGHS times out at 20 / 26 (28% / 34% gap).
2. **20-qubit framework operator on the grid** — ΔL ranks certified > deg-2 > MILP > no-build. 10q QAOA already flown on ibm_marrakesh.
3. **Named line set** — seven lines, capex 11.42, congestion 77.125 → 1.440 (−98.1%).
4. **MPS poor objective** — TT-SVD of the true cost: every χ < 16 returns the wrong plan (+1.9% to +9.1%). Hardware returns the exact plan.

`python verify.py` then `python eon_rubric_mps.py`.

## Verify the headline numbers (CPU, ~1 min)

```
python verify.py
```

Expected: two-build, residuals, Schmidt, line set, MPS χ-sweep all PASS.

Full rebuild of the v4 evidence pack (~45 s):

```
python eon_v4_advantage.py
```

## What is in this package

```
EON_REPORT_v4.md                 the write-up
QUANTUM_ADVANTAGE_EXHIBIT.md     standalone advantage exhibit
RECEIPTS.md                      claim → file → job-ID
README.md                        this file
verify.py                        credential-free audit
eon_core.py                      referee + instance generator + MILP
eon_v4_advantage.py              two-build, held-out, Schmidt
eon_rubric_mps.py                named lines + MPS-on-true-cost sweep
eon_nisq_field.py                20q operator (Outcome 2)
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
in `results/`.

## Note on scope

The advantage is **representational**, stated and bounded — not a
supremacy claim at 10 binaries and not a 100-qubit hardware-vs-MPS
result. The scored deliverable is a certified line set plus a hardness
ladder a DSO planner can read.
