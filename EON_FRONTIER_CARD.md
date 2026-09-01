# E.ON submission algorithm — framework operator on the grid

**2026-08-30.**

## The algorithm (Outcome 2)

The candidate graph **is** the 6-qubit-cell lattice.

| piece | what it is |
|---|---|
| 10 candidates | 10 rungs, 20 qubits |
| rungs 7, 8, 9 | existing slack corridors (0–1, 0–4, 1–2). Always in H. |
| rungs 0–6 | distance-2 closures. Enter H only when built. |
| prep | exact ground: RY(θ*)–CNOT–H⊗H, θ* = π/2 − 2χ |
| step | RZZ(−μ* dt · w) / RX(−2 dt) / electrical-neighbour RXX |
| N−1 | X-quench on the slack corridor (rung 7) |
| score | slack-star leftover L(k) = rms_{i∈{7,8,9}} (C* − ⟨ZZ⟩_i) |

Builds are Hamiltonian support. They are not cost-layer bits.
QAOA-on-a-degree-2-shadow remains the 10-qubit letter of the
brief (already flown, sampled the certified bitstring). It is
not the algorithm we are submitting as the quantum method.

---

## What “better than Mitsubishi” means here

Mitsubishi’s advantage was **of route**: real-time A(ω) vs
ill-posed continuation. Bounded, receipt-backed, no fake
energy supremacy.

E.ON’s advantage is **of representation, measured as dynamics**:
the true expansion objective is fifth-order because congestion
is a collective field. MPS of that tensor returns the wrong
lines below χ = 16. The same field is the A1 observable on
this lattice. Hardware holds the series; a bond-dimension
truncation of the operator growth does not.

That is a stronger *kind* than a 10q QAOA that lucked the
argmin. It is the brief’s Outcome 4 on the algorithm, not
only on a tensor we diagonalized classically.

---

## Model gate (closed on the four named plans)

Score is the **initial absorption** ΔL = L(0) − L(1), not a
late-k point. k = 8 is a unitary revival (same lesson as A1).

| plan | ΔL | congestion |
|---|---:|---:|
| certified | **+0.140** | 1.440 |
| degree-2 | +0.124 | 1.625 |
| MILP | +0.042 | 2.495 |
| no-build | −0.042 | 77.125 |

Order matches the referee. Receipt: `eon_nisq_field.json`.

---

## Hardware (new jobs only)

Same circuits as the model gate. Frozen before fly:

- Arms: no-build / MILP / deg-2 / certified × k ∈ {0,4,8,10}
- Control: detuned dt = 0.36 (must move)
- Null: prep, no quench (must sit on C*)
- Backend: open plan, lowest queue among fez / kingston / marrakesh
- Do **not** recaption A1 job `d9rdfb1dsedc73agh5ng`
- Dual outcome, written now:
  - Hardware L(k) matches the derived series on the certified
    arm after one damping envelope; certified remains the
    lowest leftover arm. Headline: NISQ congestion-field
    ranking, same line set as the exact table.
  - If the device series follows a different arm, publish
    that. The line set still has the QAOA receipt. No
    caption swap.

Human go required to submit. Depth stays inside the ~370 CX
wall (20q, sparse, k ≤ 10).

---

## What stays from v4.1 (spine, not the claim)

| Outcome | Keep |
|---|---|
| 1 | HiGHS ladder. Death at 20 / 26 binaries. |
| 3 | Seven named lines. 77.125 → 1.440. Two-build ledger. |
| 4 | TT-SVD of the true cost. χ < 16 wrong plan. |

Drop from the headline: Dirac as the algorithm, the 100q QAOA
card, “supreme,” recycled A1 jobs.

---

## Order

1. Close the model gate on the slack-star series.
2. Freeze pending + circuits.
3. Rewrite `EON_REPORT` with this as Outcome 2.
4. Fly on go.
