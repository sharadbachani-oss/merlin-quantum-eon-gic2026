# E.ON v5 internal plan — Mitsubishi-class dynamics crossing

**2026-09-08.** Close the 8.0 → sendable gap without inventing jobs.

## The crossing (what we add)

Mitsubishi v4’s advantage is **of route**: real-time \(A(\omega)\) versus
ill-posed imaginary-time + analytic continuation. E.ON v4 only had a
**representation** wall (MPS of the cost tensor, \(\chi<16\) wrong plan).

v5 adds the same route class on the E.ON operator:

> After an N−1 quench, the slack-star leftover series \(L(k)\) is a
> real-time dynamical correlator of \(H=\mu^\star D-A_6\). Its spectrum
> \(S(\omega)\) is the congestion-field absorption — the quantity that
> ranks builds and sizes firming storage. The scalable classical route
> is imaginary-time leftover \(G(\tau)\) plus Padé/Prony continuation.
> That continuation is ill-posed: two spectra fit \(G(\tau)\) and
> disagree on the principal line. Cheap MPS dynamics (mid-cut \(\chi\)
> truncation of the evolving 20q state) returns the wrong \(\Delta L\)
> ranking. Real-time evolution has no continuation step.

That is a dynamics crossing a classical imag-time / MPS / AR route
cannot cheaply fake. It is **not** supremacy at 10 binaries.

## Evidence required (honest split)

| Claim | Status | Artifact |
|---|---|---|
| Real-time \(S(\omega)\) of \(L(k)\) on the 20q grid operator | **computed now** (statevector, same circuits as Outcome 2) | `eon_dynamics_crossing.json` |
| Imag-time \(G(\tau)\) + two-spectrum ill-posedness | **computed now** | same |
| Mid-cut MPS dynamics: cheap \(\chi\) wrong \(\Delta L\) order | **computed now** | same |
| Factorized (no \(A_6\) bonds) ranking fails | **computed now** | same |
| Storage sized from **this** 20q leftover spectrum | **computed now** — replaces VW job | same + `eon_storage_sizing.json` |
| Hardware two-point \(\Delta L\) (kingston / marrakesh) | **already flown** — ranking **partial** | existing field JSONs |
| Hardware full-\(k\) leftover \(\to S(\omega)\) | **NOT FLOWN** — protocol + expected signature only | protocol card in the JSON |
| 64-rung VW spectrum `daa9pn4e74ec73akj9i0` | **drop from E.ON claims** | leave file, do not cite as ours |
| Aquila exact rung map | **protocol** (fable 1e-9 map); no Aquila job | protocol card |

## Files that change

- `eon_dynamics_crossing.py` — crossing + storage + protocol (new)
- `eon_full_k_leftover.py` — retrieve-first leftover → S(ω) one-command
- `results/eon_full_k_leftover.json` — protocol + CRN search (NOT_FLOWN)
- `results/eon_dynamics_crossing.json` — generated
- `eon_storage_sizing.json` / `results/eon_storage_sizing.json` — E.ON-native
- `EON_REPORT_v4.md`, `EON_SUBMISSION_BODY.md`, `README.md`, `RECEIPTS.md`
- `QUANTUM_ADVANTAGE_EXHIBIT.md`, `EON_FRONTIER_CARD.md`, `verify.py`

Working copies under `C:\quantum ai 2026\eon` stay in sync for the
script and the report. No VW / Cleveland / HSBC / Airbus edits.

## Claim that will match the evidence

**Advantage of route, bounded.** Real-time leftover spectrum versus
ill-posed continuation and cheap MPS dynamics, on today’s 20q operator.
Hardware ranks certified \(>\) MILP \(>\) no-build on kingston; degree-2
is device-dependent and is stated as such. Full-chip \(S(\omega)\) and
Aquila analog are the next flights, not this package’s jobs.

Sendable to the E.ON brief: **yes, stronger**. Mitsubishi-v4 sendable:
**not until a full-\(k\) leftover series is flown.** Do not pretend
otherwise.

## Full-\(k\) leftover one-command (2026-09-08)

Searched local receipts and the IBM CRN. No E.ON leftover-series job
exists. Two-point \(\Delta L\) jobs stay P1 LOSS and cannot host the
0.222 bin. VW `daa9pn4e74ec73akj9i0` is refused.

One-command (default retrieve, no paid submit):

```
python eon_full_k_leftover.py
```

Exact next flight that would close the Mitsubishi gap: 29 circuits
(certified / MILP / no-build × \(k=0..8\) + null + detuned), 8192 shots,
open Heron, fixed CHAIN layout. Human go:

```
EON_FULL_K_SUBMIT=1 python eon_full_k_leftover.py --submit --k-grid dense
```

## Closed (2026-09-08)

All five crossing gates PASS (`eon_dynamics_crossing.json`, 270 s):

- Real-time leftover lines: certified 0.222 / deg-2 0.333 / MILP 0.444
- Two imag-time spectra, err 0.057 / 0.058, decays 1.696 vs 1.592
- Continuation 0.270 misses 0.222
- \(A_6\)-off: every plan \(\Delta L=+0.514\)
- Storage from this spectrum: Q 9.76 ± 0.91; continuation 6.94 (−29%)
- Hardware ranking left partial; VW job dropped; Aquila / full-\(k\) marked NOT_FLOWN
- Full-\(k\) leftover is now one-command (`eon_full_k_leftover.py`); CRN retrieve found no series; still NOT_FLOWN

Mid-cut MPS \(\chi=1,2,4\) still ranks \(\Delta L\) (control). Product-rung
preserves \(\Delta L\) order but moves the deg-2 line 0.333 → 0.444.
