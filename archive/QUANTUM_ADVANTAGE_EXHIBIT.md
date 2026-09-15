# Advantage of route — leftover \(S(\omega)\) vs continuation

**Merlin Digital · E.ON track · Report v5.0 · 2026-09-08**

Mitsubishi v4’s advantage was of route: real-time \(A(\omega)\) versus
ill-posed imaginary-time + analytic continuation. This exhibit is the
same class on the E.ON operator. It is **not** a supremacy claim.

## The industrial object

After an N−1 quench on a slack corridor, the leftover series

\[
L(k)=\mathrm{rms}_{i\in\{7,8,9\}}(C^\star-\langle ZZ\rangle_i(k))
\]

is a real-time correlator of \(H=\mu^\star D-A_6\). Its spectrum
\(S(\omega)=|\mathrm{DFT}[L-\mathrm{mean}]|^2\) is the congestion-field
absorption: it ranks builds and sizes firming storage.

| plan | \(\Delta L\) | principal line (cyc/step) | referee congestion |
|---|---:|---:|---:|
| certified | +0.140 | **0.222** | 1.440 |
| degree-2 | +0.124 | 0.333 | 1.625 |
| MILP | +0.042 | 0.444 | 2.495 |
| no-build | −0.042 | 0.444 | 77.125 |

Receipt: `results/eon_nisq_field.json`, `results/eon_dynamics_crossing.json`.

## The classical routes that fail

**1. Imaginary-time + continuation (ill-posed).** Two two-pole models
fit the certified arm’s \(G(\tau)\) to max residual 0.057 and 0.058
and disagree on the principal decay (1.696 vs 1.592). Mapped to
cycles/step they land at 0.270 / 0.253. The real-time line is 0.222.
Distinct spectra reproduce the same imaginary-time data; neither is
the leftover spectrum.

**2. Drop residual \(A_6\) bonds.** Every named plan returns
\(\Delta L=+0.514\). Without the derived kinetic term the field cannot
rank a certified closure against do-nothing.

**3. Product-rung projection.** Rebuild a product of per-rung 2-qubit
states after every step. \(\Delta L\) order can survive; the degree-2
principal line does not (0.333 → 0.444).

A mid-cut MPS of the 20q state (\(\chi=1,2,4\)) still ranks \(\Delta L\).
That cut is kind — the slack star sits on one side — and is shipped as
the control, not the cheap attack.

## What hardware has actually measured

Two-point \(\Delta L\) on IBM Heron, raw counts:

- ibm_kingston `daa0dq6rbfbs73ci56bg`: certified +0.113, MILP +0.045,
  no-build −0.025, degree-2 **−0.006**. Certified beats MILP and
  do-nothing. Frozen order is not recovered. P1 LOSS.
- ibm_marrakesh `daa9do6rbfbs73cifa80`: degree-2 +0.127 (frozen +0.124),
  certified +0.120, visibility 0.93–0.98. Device order is deg-2 >
  certified. P1 LOSS.

Full-\(k\) leftover \(\to S(\omega)\) on a device: **NOT FLOWN**.
One-command (retrieve only): `python eon_full_k_leftover.py`.
The flight that would close the Mitsubishi gap is 29 circuits,
\(k=0..8\), 8192 shots, open Heron — gated by `EON_FULL_K_SUBMIT=1`.
No job ID.

## Storage, from this spectrum only

Colored by the 20q certified leftover spectrum (statevector, no cloud
job): **9.76 ± 0.91 p.u.h**. Colored by continuation of the same
\(G(\tau)\): **6.94 ± 0.69 p.u.h (−29%)**. White 10.67 ± 2.40; AR
9.57 ± 2.12. At this resolution white/AR sit near the real-time
number; the decision-changing error is the continuation.

A previous draft used Volkswagen’s 64-rung series
(`daa9pn4e74ec73akj9i0`). That job is **not an E.ON result**.

## What this is not

Not absolute-energy supremacy at 10 binaries. Not a 100-qubit
hardware-vs-MPS result. Not a claim that the two-point Heron ranking
recovers the frozen four-plan order. The advantage is of route, and
it is bounded to the leftover spectrum of this operator on this
instance.
