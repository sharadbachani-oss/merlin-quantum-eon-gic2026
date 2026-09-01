# RECEIPTS — mapped to the four official outcomes

## Outcome 1 — hard instances, differing variable counts

| Claim | Artifact |
|---|---|
| 6 / 10 / 14 / 20 / 26 binaries; HiGHS 0.28 s → 1801 s | `results/eon_ladder.json` |
| TIMEOUT 28% gap (20 bin), 34% gap (26 bin) | same → `eon57_util` / `eon57_deep` |

## Outcome 2 — quantum algorithm, NISQ-runnable

| Claim | Job ID | Artifact |
|---|---|---|
| 20q field on ibm_kingston: certified ΔL +0.113 (best), beats MILP +0.045; no-build −0.025 | `daa0dq6rbfbs73ci56bg` | `eon_field_result.json` + frozen pending |
| 20q field cross-device replication (fixed layout, equal structure): deg-2 arm +0.127 vs frozen +0.124; visibility 0.93–0.98 | `daa9do6rbfbs73cifa80` (ibm_marrakesh) | `eon_field_v2_result_20260831_004726.json` |
| eon57_util hard-rung benchmark: Dirac plan 22,078 vs MILP-incumbent referee grade 24,652 (−10.4%, seconds vs 901 s timeout) | `6a943a6408442f441bbb6ad1`, `6a943a7408442f441bbb6ad2` | `eon57_dirac_result.json`, `eon57_fit.json` |
| Storage sizing under measured fluctuation class: true 16.18 p.u.h; white −24% shortfall; AR 12× over-build | spectrum job `daa9pn4e74ec73akj9i0` (ibm_fez) | `eon_storage_sizing.json`, `vw_jam_relaxation_spectrum_v2.json` |
| Each certified closure raises ΔL vs MILP | — | same |
| QAOA exact optimum, ibm_marrakesh | `d9sqks1dsedc73ai3o30` | `results/eon_qaoa_result.json` → `hw` |
| QAOA-circuit MPS tie at χ ≥ 2 (control) | — | same → `mps` |
| Dirac-3 native deg-5, gap 0.000 (annex) | `6a79a72508442f441bbb5e56` | `results/eon_dirac_result.json` → `native` |
| Dirac-3 deg-2, +9.1% (annex) | `6a79a74e08442f441bbb5e57` | same → `surrogate_deg2` |

## Outcome 3 — optimal lines, cost, congestion

| Claim | Artifact |
|---|---|
| Seven named lines (bus pairs, x, rating, capex) | `results/eon_rubric_mps.json` → `eon14_hard.lines` |
| Capex 11.42; 77.125 → 1.440 (−98.1%); 227 → 7; 423 → 137 | same → `eon14_hard` |
| Two-build split (do not use 77.1→2.50 as the certified plan) | `results/eon_v4_advantage.json` → `two_build` |

## Outcome 4 — MPS simulation, poor objective

| Claim | Artifact |
|---|---|
| TT-SVD χ-sweep on true cost, n=10: χ<16 wrong plan, +1.9%…+9.1% | `results/eon_rubric_mps.json` → `eon14_hard.mps_chi_sweep` |
| χ=4 plan = degree-2 QUBO plan | same vs `eon_dirac_result.json` → `surrogate_deg2.solution` |
| n=6: χ=1 is +75.8%, χ≥2 exact | same → `eon14_easy.mps_chi_sweep` |
| Schmidt 8/8 and 32/32; deg-2 shadow rank 5 / 7 | `results/eon_v4_advantage.json` → `schmidt_scaling` |

## Supporting

| Claim | Artifact |
|---|---|
| Held-out −40.5% vs MILP, 12 seeds | `eon_v4_advantage.json` → `held_out` |
| Hidden voltage, 8 DC-up / v-down plans | same → `hidden_congestion` |
| 100q card frozen, not flown | same → `utility_qaoa_100q` |

```
python verify.py
python eon_rubric_mps.py
```
