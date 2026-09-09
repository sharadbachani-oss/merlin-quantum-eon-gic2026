# RECEIPTS — mapped to the four official outcomes

## Outcome 1 — hard instances, differing variable counts

| Claim | Artifact |
|---|---|
| 6 / 10 / 14 / 20 / 26 binaries; HiGHS 0.28 s → 1801 s | `results/eon_ladder.json` |
| TIMEOUT 28% gap (20 bin), 34% gap (26 bin) | same → `eon57_util` / `eon57_deep` |

## Outcome 2 — quantum algorithm, NISQ-runnable

| Claim | Job ID | Artifact |
|---|---|---|
| Real-time leftover \(S(\omega)\): certified 0.222 / deg-2 0.333 / MILP 0.444 cyc/step; \(\Delta L\) ranks with referee | — (statevector) | `eon_dynamics_crossing.json` + `eon_nisq_field.json` |
| Imag-time \(G(\tau)\): two 2-pole models err 0.057 / 0.058, decays 1.696 vs 1.592; continuation 0.270 misses 0.222 | — | same → `imaginary_time` |
| Drop \(A_6\) bonds: every plan \(\Delta L=+0.514\) (cannot rank) | — | same → `factorized_no_A6_bonds` |
| Product-rung: deg-2 line 0.333 → 0.444 | — | same → `product_rung_dynamics` |
| Mid-cut MPS \(\chi=1,2,4\) still ranks \(\Delta L\) (control: slack star on one side) | — | same → `mps_midcut_control` |
| 20q field on ibm_kingston: certified \(\Delta L\) +0.113 (best vs MILP +0.045 / no-build −0.025); deg-2 collapsed −0.006. P1 LOSS | `daa0dq6rbfbs73ci56bg` | `eon_field_result.json` + frozen pending |
| 20q field cross-device (fixed layout): deg-2 +0.127 vs frozen +0.124; visibility 0.93–0.98; device order deg-2 > certified. P1 LOSS | `daa9do6rbfbs73cifa80` (ibm_marrakesh) | `eon_field_v2_result_20260831_004726.json` |
| Full-\(k\) leftover \(\to S(\omega)\) on hardware | **NOT_FLOWN** — no job ID. One-command: `python eon_full_k_leftover.py` (retrieve only). Paid submit is `EON_FULL_K_SUBMIT=1 python eon_full_k_leftover.py --submit --k-grid dense` | `eon_full_k_leftover.json` + `eon_dynamics_crossing.json` → `hardware.full_k_spectrum` |
| Aquila exact rung map | **NOT_FLOWN** — no job ID | same → `hardware.aquila_rydberg` |
| eon57_util hard-rung benchmark: Dirac plan 22,078 vs MILP-incumbent referee grade 24,652 (−10.4%, seconds vs 901 s timeout) | `6a943a6408442f441bbb6ad1`, `6a943a7408442f441bbb6ad2` | `eon57_dirac_result.json`, `eon57_fit.json` |
| Storage from **this** 20q leftover spectrum: Q 9.76 ± 0.91 p.u.h; continuation 6.94 ± 0.69 (−29%) | none (statevector) | `eon_storage_sizing.json` |
| VW 64-rung spectrum `daa9pn4e74ec73akj9i0` | **NOT_AN_EON_RESULT** | same → `hardware.vw_64rung_spectrum` |
| QAOA exact optimum, ibm_marrakesh | `d9sqks1dsedc73ai3o30` | `results/eon_qaoa_result.json` → `hw` |
| QAOA-circuit MPS tie at \(\chi\ge 2\) (control) | — | same → `mps` |
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
| TT-SVD \(\chi\)-sweep on true cost, n=10: \(\chi<16\) wrong plan, +1.9%…+9.1% | `results/eon_rubric_mps.json` → `eon14_hard.mps_chi_sweep` |
| \(\chi=4\) plan = degree-2 QUBO plan | same vs `eon_dirac_result.json` → `surrogate_deg2.solution` |
| n=6: \(\chi=1\) is +75.8%, \(\chi\ge 2\) exact | same → `eon14_easy.mps_chi_sweep` |
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
python eon_dynamics_crossing.py
python eon_full_k_leftover.py   # retrieve + protocol; no paid submit
```
