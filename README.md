# Merlin Quantum — GIC 2026 · E.ON — Grid Expansion Planning

Phase-1 concept proposal, 2026 Global Quantum + AI Challenge.

| | |
|---|---|
| **Submitted proposal** | [`EON_PROPOSAL_v7.md`](EON_PROPOSAL_v7.md) — rendered as `report.pdf` |
| **Team** | Merlin Quantum, the quantum applications division of Merlin Digital (Dubai) |
| **Independent validation** | GIC 2026 **dual-track finalist** — Mitsubishi/AIST materials and QCi tracks; same framework, same instrument |
| **Repository** | https://github.com/sharadbachani-oss/merlin-quantum-eon-gic2026 |
| **Superseded material** | `archive/` — earlier drafts and planning notes, kept for provenance; not part of the submission |

## Claim → receipt

Every measurement the proposal reports, with the file in this repository that backs it. Each entry resolves inside this repo.

| # | Measurement | Receipt |
|---:|---|---|
| 1 | The hard rung. On eon57_util the proof-grade MILP times out with an incumbent grading 24,652, while exhaustive enumeration of all 1,048,576 builds on the exact referee | [`eon57_expand.json`](results/eon57_expand.json) · [`eon57_early_polish.json`](results/eon57_early_polish.json) |
| 2 | On the variational rung it holds: depth-1 to depth-3 QAOA on eon57_util's 20 binaries samples within 0.03% of the optimum at χ = 4 and reaches it at χ = 64 | [`eon57_qaoa_mps.json`](results/eon57_qaoa_mps.json) |
| 3 | All four arms are computed exactly by statevector | [`eon_storage_sizing.json`](eon_storage_sizing.json) |
| 4 | eon57_util device rung: 22,078 vs incumbent 24,652; polish → 22,057 (matched classically in 18 s) | [`eon57_dirac_result.json`](results/eon57_dirac_result.json) |
| 5 | eon57_util exhaustive landscape: all 2²⁰ = 1,048,576 builds graded by the exact referee; 22,057 is the global optimum; single one-flip basin; exact Möbius degree spectrum | [`eon57_expand_grade.json`](results/eon57_expand_grade.json) |
| 6 | eon14_hard native degree-5: certified plan, gap 0.000 | [`eon_dirac_result.json`](results/eon_dirac_result.json) |
| 7 | QAOA depth 333, 171 two-qubit gates: certified optimum sampled | [`eon_qaoa_result.json`](results/eon_qaoa_result.json) |
| 8 | 20-qubit two-point absorption: certified +0.113, MILP +0.045, degree-2 −0.006, no-build −0.025; middle pair swaps vs frozen order, P1 false, logged LOSS | [`eon_field_result.json`](results/eon_field_result.json) |
| 9 | Equal-structure replication, visibility 0.93–0.98: degree-2 +0.126, certified +0.120, MILP +0.073, no-build +0.029; P1/P3 false, logged LOSS | [`eon_field_v2_result_20260831_004726.json`](results/eon_field_v2_result_20260831_004726.json) |
| 10 | Instance ladder, HiGHS 0.28 s → 1,801 s; gaps 28.25% / 33.8% | [`eon_ladder.json`](results/eon_ladder.json) |
| 11 | Convergence law, 22.6% at 9,437 s; projections | [`eon57_deep_gap_extrapolation.json`](results/eon57_deep_gap_extrapolation.json) |
| 12 | Dynamics crossing: lines 0.222 / 0.333 / 0.444; continuation 0.270 misses | [`eon_dynamics_crossing.json`](results/eon_dynamics_crossing.json) |
| 13 | MPS χ-sweep on true cost: χ < 16 wrong plan | [`eon_rubric_mps.json`](results/eon_rubric_mps.json) |
| 14 | Held-out scenarios −40.5% | [`eon_v4_advantage.json`](results/eon_v4_advantage.json) |
| 15 | Full-k four-plan leftover series (54 circuits, 442,368 shots) | [`prepare_application_series.py`](prepare_application_series.py) |

## Verifying

```
python verify.py
```

Replays the headline numbers from archived counts — no credentials, no network, numpy only.
