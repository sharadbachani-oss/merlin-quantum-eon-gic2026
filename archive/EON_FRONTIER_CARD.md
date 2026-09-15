# E.ON submission algorithm — framework operator on the grid

**2026-09-08 (v5).** The algorithm is the derived operator. The
advantage is of route.

---

## The algorithm (Outcome 2)

The candidate graph **is** the 6-qubit-cell lattice of
\(H=\mu^\star D-A_6\).

| piece | what it is |
|---|---|
| 10 candidates | 10 rungs, 20 qubits |
| rungs 7, 8, 9 | existing slack corridors (0–1, 0–4, 1–2). Always in H. |
| rungs 0–6 | distance-2 closures. Enter H only when built. |
| prep | exact ground: RY(\(\theta^\star\))–CNOT–H⊗H, \(\theta^\star=\pi/2-2\chi\) |
| step | RZZ(\(-\mu^\star dt\cdot w\)) / RX(\(-2\,dt\)) / electrical-neighbour RXX |
| N−1 | X-quench on the slack corridor (rung 7) |
| score | leftover \(L(k)\) and its spectrum \(S(\omega)\) |

Builds are Hamiltonian support. They are not cost-layer bits.
QAOA-on-a-degree-2-shadow remains the 10-qubit letter of the
brief (already flown, sampled the certified bitstring). It is
not the algorithm we are submitting as the quantum method.

---

## Advantage of route (closed on CPU, partial on hardware)

Mitsubishi’s advantage was **of route**: real-time \(A(\omega)\) vs
ill-posed continuation. E.ON’s is the same class on this lattice.

Real-time leftover \(S(\omega)\) of the four named plans:

| plan | \(\Delta L\) | line (cyc/step) |
|---|---:|---:|
| certified | **+0.140** | **0.222** |
| degree-2 | +0.124 | 0.333 |
| MILP | +0.042 | 0.444 |
| no-build | −0.042 | 0.444 |

Order matches the referee. Continuation of \(G(\tau)\) misses 0.222
(lands at 0.270). Dropping \(A_6\) bonds makes every plan
\(\Delta L=+0.514\). Receipt: `eon_dynamics_crossing.json`.

---

## Hardware (flown vs protocol)

Flown, two-point \(\Delta L\) only:

- ibm_kingston `daa0dq6rbfbs73ci56bg` — certified +0.113 beats MILP
  and no-build; degree-2 collapsed. P1 LOSS.
- ibm_marrakesh `daa9do6rbfbs73cifa80` — degree-2 recovered (+0.127);
  device order deg-2 > certified. P1 LOSS.

Not flown — protocol + expected signature, no job ID:

- Full-\(k\) leftover \(\to S(\omega)\) on Heron — one-command
  `python eon_full_k_leftover.py` (retrieve only; no job ID)
- Aquila exact rung map (\(V=2\mu^\star E_u\), \(\Delta=\mu^\star E_u\), \(\Omega=2E_u\))

Do **not** recaption VW job `daa9pn4e74ec73akj9i0` or A1 job
`d9rdfb1dsedc73agh5ng`.

---

## What stays (spine, not the claim)

| Outcome | Keep |
|---|---|
| 1 | HiGHS ladder. Death at 20 / 26 binaries. |
| 3 | Seven named lines. 77.125 → 1.440. Two-build ledger. |
| 4 | TT-SVD of the true cost. \(\chi<16\) wrong plan. Supporting wall. |

Headline is the leftover spectrum, not Dirac, not a 100q QAOA card,
not “supreme,” not a recycled sister-track job.
