# Quantum-Enhanced Grid Expansion: Hard Instances, a NISQ Algorithm, a Certified Line Set, and a Dynamics Crossing

**Global Quantum + AI Challenge 2026 — E.ON Enterprise Track**
**Team: Merlin Digital (GIC 2026 dual-track finalist — Mitsubishi/AIST materials track) · Report v5.0, 2026-09-08**

This page is written to the challenge brief. Each expected outcome is a
section. Every number has a receipt. Advantage is **of route**, stated
and bounded — not a supremacy claim.

---

## Official brief → this package

**Context.** Expanding medium- and low-voltage networks is a combinatorial
build-or-no-build problem coupled to network physics across operating
scenarios. Classical MIP solvers struggle to prove optimality at scale.

**Objective.** A quantum-enhanced expansion method that optimally reduces
congestion: identify hard instances, develop a quantum algorithm
(variational / hybrid) benchmarked on at least one hard instance, with
at least one instance small enough for current NISQ hardware.

| Expected outcome (verbatim class) | This package |
|---|---|
| 1. Classically hard instances with differing variable counts | 6 / 10 / 14 / 20 / 26 binaries. Proof-grade HiGHS dies at 20 (28% gap) and 26 (34% gap). |
| 2. Quantum algorithm on a hard instance, NISQ-runnable | 20-qubit framework operator \(H=\mu^\star D-A_6\) on the candidate lattice. Real-time leftover spectrum \(S(\omega)\) ranks certified > deg-2 > MILP > no-build. Continuation and \(A_6\)-off dynamics cannot. 10q QAOA already flown (ibm_marrakesh). |
| 3. Optimal new lines + cost + congestion reduction | Seven lines named below. Capex 11.42. Thermal congestion 77.125 → 1.440 (−98.1%). |
| 4. MPS simulation gives poor objective value | TT-SVD MPS of the *true* cost: \(\chi<16\) returns the wrong plan (gaps +1.9% to +9.1%). Hardware / Dirac return the exact plan. |

---

## Outcome 1 — Classically hard instances, differing variable counts

Methodology per the challenge's named framework ([5], QOBLIB): hard
instances of a simplified-but-faithful formulation are identified first,
and the quantum algorithm is shaped to those instances. Instances are
built from the open IEEE 14-bus case and synthetic grids generated to
match its graph properties (degree distribution, meshedness).

One referee (DC-PTDF thermal congestion + LinDistFlow voltage check)
grades every solver. Instances differ only in binary count, scenario
count, and N−1:

| instance | binaries | scenarios | N−1 | MILP vars | HiGHS wall | verdict |
|---|---:|---:|---|---:|---:|---|
| eon14_easy | 6 | 2 | no | 96 | 0.28 s | proven optimal |
| eon14_hard | 10 | 4 | yes | 4,250 | 4.5 s | proven optimal — **NISQ + Dirac target** |
| eon30_hard | 14 | 4 | yes | 17,614 | 183 s | proven optimal |
| **eon57_util** | **20** | 4 | yes | 59,116 | **900 s** | **TIMEOUT, 28% gap — Dirac-3 beats the incumbent by 10.4% in seconds (Outcome 2)** |
| **eon57_deep** | **26** | 6 | yes | 94,646 | **1801 s** | **TIMEOUT, 34% gap** |

Receipt: `results/eon_ladder.json`. ~40× time per rung. The wall is
inside a DSO afternoon loop (20 build decisions). That is the
challenge’s “scale poorly with Gurobi/CPLEX” evidence, executed with
proof-grade HiGHS.

The ladder splits the two roles the brief asks for: eon14_hard is the
NISQ-scale instance whose **true** objective already saturates its
Schmidt envelope (Outcome 4); the hard MIP instances are eon57_*.

**The hard rung, flown.** On **eon57_util** — the 20-binary instance
where proof-grade MILP timed out at 901 s holding a **28.25% proven
gap** — the expansion objective was fitted as a native degree-3
polynomial (holdout Spearman 0.9999 against 6,001 exact referee
evaluations) and annealed on QCi Dirac-3 (jobs
`6a943a6408442f441bbb6ad1`, `6a943a7408442f441bbb6ad2`). The device
returned, **in seconds**, a plan the full-physics referee grades at
**22,078** — **10.4% better than the timed-out MILP incumbent’s referee
grade (24,652)** and better than all 6,001 referee-graded classical
samples (best 22,181). The same referee grades every solver: on the
instance class the brief names as the classical wall, the quantum route
delivers a better plan than the MILP toolchain can find in its budget.
Receipts: `results/eon57_dirac_result.json`, `results/eon57_fit.json`.

---

## Outcome 2 — Quantum algorithm, benchmarked, NISQ-runnable

**Algorithm: the framework operator on the grid, 20 qubits.**

The candidate graph is a 10-rung lattice of the derived operator
\(H=\mu^\star D-A_6\), \(\mu^\star=3/(3-\sqrt{5})\). Exact per-rung
ground prep (RY(\(\theta^\star\))–CNOT–H⊗H, \(\theta^\star=\pi/2-2\chi\)).
Existing slack corridors (buses 0–1, 0–4, 1–2) are always in the
Hamiltonian. Distance-2 closures enter only when built. N−1 is an
X-quench on the slack corridor. Builds are Hamiltonian support, not
QUBO bits.

The scored object is the slack-star leftover series
\(L(k)=\mathrm{rms}(C^\star-\langle ZZ\rangle)\) on those three existing
rungs, and its spectrum \(S(\omega)=|\mathrm{DFT}[L-\mathrm{mean}]|^2\).
A better build absorbs the contingency off the existing star. Initial
absorption \(\Delta L=L(0)-L(1)\) ranks the four named plans in the
same order as the physics referee:

| plan | \(\Delta L\) | leftover \(S(\omega)\) line (cyc/step) | referee congestion |
|---|---:|---:|---:|
| **certified** | **+0.140** | **0.222** | **1.440** |
| degree-2 | +0.124 | 0.333 | 1.625 |
| MILP | +0.042 | 0.444 | 2.495 |
| no-build | −0.042 | 0.444 | 77.125 |

Each certified closure, added alone to the MILP set, raises \(\Delta L\).
All-build buys +0.006 more absorption and a *worse* thermal number — the
field does not want junk lines. Receipt: `results/eon_nisq_field.json`.

### Advantage of route (the Mitsubishi-class crossing)

For a DSO the industrially decisive question after a contingency is not
the static MILP number. It is **how the leftover rings** — the leftover
spectrum \(S(\omega)\). The certified plan, the degree-2 truncation, and
the MILP plan are three different dynamical objects: principal lines
**0.222 / 0.333 / 0.444** cycles per Trotter step.

The scalable classical route to a real-frequency leftover spectrum is
imaginary-time leftover \(G(\tau)\) plus analytic continuation. That
continuation is **ill-posed**. On the certified arm, two two-pole models
fit the same \(G(\tau)\) to 0.057 / 0.058 max residual and disagree on
the principal decay (1.696 vs 1.592). Neither recovers the real-time
line: continuation maps to **0.270** cycles/step against the real-time
**0.222**. Receipt: `results/eon_dynamics_crossing.json`.

Two further cheap classical dynamics fail as ranking engines:

- **Drop the residual \(A_6\) electrical bonds** (factorized rungs).
  Every named plan returns the same \(\Delta L=+0.514\). Without the
  derived kinetic term the field cannot tell a certified closure from
  do-nothing.
- **Product-rung projection** (rebuild a product of per-rung 2-qubit
  states after every step). \(\Delta L\) order can survive; the
  degree-2 principal line does not (0.333 → 0.444).

A mid-cut MPS truncation of the 20q state (\(\chi=1,2,4\) on qubits
0–9 | 10–19) still ranks \(\Delta L\) correctly. That cut is kind: the
slack star sits on one side. It is shipped as a **control**, not as the
cheap attack.

This is an **advantage of route**. Real-time evolution of
\(H=\mu^\star D-A_6\) produces \(S(\omega)\) by Fourier transform with
no continuation step. Imaginary-time + Padé/Prony, \(A_6\)-off
dynamics, and product-rung projection cannot cheaply fake that spectrum
or the ranking it induces. The claim holds at this 20-qubit instance
and does not expire if a faster classical computer arrives tomorrow —
the continuation step stays ill-posed. **What we do not claim:**
absolute-energy supremacy, or a 100-qubit hardware-vs-MPS result.

### Hardware on today's devices (partial ranking, no invented jobs)

Statevector gate: `results/eon_nisq_field.json`. Two-point \(\Delta L\)
hardware, graded from raw:

| plan | frozen \(\Delta L\) | ibm_kingston `daa0dq6rbfbs73ci56bg` | ibm_marrakesh `daa9do6rbfbs73cifa80` |
|---|---:|---:|---:|
| certified | +0.140 | **+0.113** | +0.120 |
| degree-2 | +0.124 | −0.006 | **+0.127** |
| MILP | +0.042 | **+0.045** | +0.073 |
| no-build | −0.042 | **−0.025** | +0.029 |

Kingston: certified is the best absorber and beats MILP; no-build
grows. Null leftover 0.031 vs 0.784 with quench. Detuned control
moved. Degree-2 collapsed — the frozen order is **not** recovered.
Marrakesh (fixed layout, equal structure, inverted readout): degree-2
lands on its frozen value (+0.127 vs +0.124), visibility 0.93–0.98,
but the device order is deg-2 > certified. **Hardware prefers certified
over MILP and over do-nothing. The degree-2 arm is device-dependent.
The ranking is partial; both flights are recorded as P1 LOSS.**

A full-\(k\) leftover series on hardware — the flight that would
Fourier-transform to \(S(\omega)\) on the device — is **not flown**.
One-command (retrieve only, no paid submit):
`python eon_full_k_leftover.py`. The protocol and expected signature
are in `eon_dynamics_crossing.json` → `hardware.full_k_spectrum`
and `results/eon_full_k_leftover.json`. The Mitsubishi-closing flight
is certified / MILP / no-build at \(k=0..8\) (29 circuits, 8192 shots,
open Heron). No job ID is assigned.

**Letter of the brief (already on hardware).** 10-qubit QAOA from
the degree-2 shadow, ibm_marrakesh job `d9sqks1dsedc73ai3o30`
(depth 333, 171 two-qubit gates, 8,192 shots), sampled the
certified bitstring. That is the small-instance sample. The
algorithm we are submitting is the 20q operator above.

**Native maps, today's hardware.** Heavy-hex (IBM Heron): flown, two
devices, two-point leftover. Dirac-3: flown (annex below). Aquila
Rydberg: the rung map is exact (\(V=2\mu^\star E_u\), \(\Delta=\mu^\star E_u\),
\(\Omega=2E_u\), fable 1e-9); FOV+C6 binds at 12 pairs / 24 atoms.
**No Aquila job is in this package.** Protocol only.

**Scalability.** The operator's unit is the rung (one candidate = 2
qubits); scaling is tiling on the same heavy-hex fabric. A 64-rung
(128-qubit) leftover series is the same compilation. It is a
**protocol in this package, not a receipt.** A sister-track Heron
flight of the same operator family exists; we do not import its
spectrum as an E.ON result (dropped job `daa9pn4e74ec73akj9i0`).

**Dirac-3 (annex, not the algorithm).** Native degree-5 anneal
returned the same certified plan (job `6a79a72508442f441bbb5e56`).
The degree-2 restriction on the same device is +9.1%
(`6a79a74e08442f441bbb5e57`). Kept as the same-device truncation
control.

**Benchmark, same instance, same referee.**

| solver | plan | exact objective | gap | congestion / ovl / vviol |
|---|---|---:|---:|---|
| Exact table (2¹⁰) | 1 0 1 1 0 1 0 1 1 1 | 83.436 | — | 1.440 / 7 / 137 |
| **Dirac-3 native deg-5** | **same** | **83.436** | **0.000** | **1.440 / 7 / 137** |
| QAOA on ibm_marrakesh | same | 83.436 | 0.000 | 1.440 / 7 / 137 |
| Dirac-3 degree-2 | 1 0 1 1 0 0 0 1 1 1 | 90.995 | +9.1% | 1.625 / 8 / 133 |
| HiGHS disjunctive TEP | 1 0 0 0 0 0 0 1 1 1 | 131.87 | +58% | 2.495 / 19 / 293 |
| MPS \(\chi=4\) on true cost | 1 0 1 1 0 0 0 1 1 1 | 90.995 | +9.1% | (same wrong plan as deg-2) |
| MPS \(\chi=1\) on true cost | 1 0 1 1 1 1 1 1 1 1 | 87.466 | +4.8% | wrong plan |
| No-build | 0…0 | 3856.27 | — | 77.125 / 227 / 423 |

Jobs: Dirac native `6a79a72508442f441bbb5e56`; Dirac deg-2
`6a79a74e08442f441bbb5e57`; QAOA `d9sqks1dsedc73ai3o30`.

The degree-2 arm is the control the brief’s “quantum vs classical
compression” reading needs: **same device, truncated objective, wrong
build, 9.1% high.** The gap is the objective’s, not the hardware’s.

---

## Outcome 3 — Optimal new lines, cost, congestion reduction

Certified plan on eon14_hard (IEEE 14-bus, four scenarios, N−1).
Buses are 0-indexed case14 nodes. Candidates 0, 2, 3, 5 are
distance-2 closures; 7, 8, 9 are parallel re-rates of existing
corridors.

| add? | candidate | from → to | x (p.u.) | rating (p.u.) | capex |
|---|---:|---|---:|---:|---:|
| yes | 0 | 4 → 12 | 0.105 | 0.873 | 1.000 |
| no | 1 | — | — | — | — |
| yes | 2 | 1 → 8 | 0.118 | 0.927 | 1.260 |
| yes | 3 | 2 → 6 | 0.132 | 0.985 | 1.390 |
| no | 4 | — | — | — | — |
| yes | 5 | 4 → 10 | 0.128 | 0.803 | 1.650 |
| no | 6 | — | — | — | — |
| yes | 7 | 0 → 1 | 0.059 | 1.350 | 1.910 |
| yes | 8 | 0 → 4 | 0.223 | 0.900 | 2.040 |
| yes | 9 | 1 → 2 | 0.198 | 0.900 | 2.170 |
| | | | | **total capex** | **11.42** |

| metric | no-build | certified plan | reduction |
|---|---:|---:|---:|
| Thermal congestion (referee) | 77.125 | **1.440** | **−98.1%** |
| Overloaded (line, scenario, contingency) triples | 227 | **7** | −220 |
| Voltage-drop violations | 423 | **137** | −286 |
| Exact objective (capex + 50 × congestion) | 3856.27 | **83.436** | certified minimum |

Receipt: `results/eon_rubric_mps.json` → `eon14_hard` (lines + metrics)
and `results/eon_dirac_result.json` (hardware certificate).

**Do not splice builds.** A previous draft said “77.1 → 2.50.” That is
the **MILP** plan’s referee (overloads 19, vviol 293, capex 7.12). The
certified plan is 1.440 / 7 / 137. Both are in the ladder receipt.
They are different line sets.

---

## Outcome 4 — MPS simulation gives poor objective value

The brief asks for this in those words. Two measurements, one
instance family. A third, on the *dynamics*, is in Outcome 2.

### 4a. MPS as a solver of the instance (the letter of the outcome)

Compress the *true* 10-bit cost tensor by TT-SVD to bond dimension
\(\chi\), take the argmin of the compressed tensor, re-grade that plan on
the exact referee. That is the expansion plan an MPS-truncated
model of the instance returns.

| \(\chi\) | plan | exact objective | gap | verdict |
|---:|---|---:|---:|---|
| 1 | 1 0 1 1 1 1 1 1 1 1 | 87.466 | **+4.8%** | wrong plan |
| 2 | 1 0 1 1 0 1 1 1 1 1 | 85.654 | **+2.7%** | wrong plan |
| 4 | 1 0 1 1 0 0 0 1 1 1 | 90.995 | **+9.1%** | wrong plan — **identical to the degree-2 QUBO / Dirac restriction** |
| 8 | 1 1 1 1 0 1 0 1 1 1 | 85.006 | **+1.9%** | wrong plan |
| 16 | 1 0 1 1 0 1 0 1 1 1 | 83.436 | 0 | exact |
| 32 | same | 83.436 | 0 | exact (full rank) |

Receipt: `results/eon_rubric_mps.json` → `eon14_hard.mps_chi_sweep`.

**MPS gives a poor objective at every \(\chi\) that cannot hold the tensor.**
The mid-cut rank of this objective is 32/32. \(\chi=16\) is the first
lossless solver. Dirac-3 and the flown QAOA return the \(\chi=16\) plan
without building that MPS.

At 6 binaries (eon14_easy) the same method is already lossless at
\(\chi=2\) (gap 0); \(\chi=1\) is **+75.8%**. Differing variable counts:
cheap MPS works on the easy instance and fails on the certified one.

### 4b. Why \(\chi\) has to be that large — the objective MPS cannot hold

Operator Schmidt rank of the true cost saturates the exponential
envelope: **8/8 at 6 binaries, 32/32 at 10 binaries.** The degree-2
shadow every QUBO/QAOA-on-QUBO pipeline holds is rank 5 / 7.
Receipt: `results/eon_v4_advantage.json` → `schmidt_scaling`.

This is the representation wall. It **motivates** the hardware; it is
not itself the advantage of route. The route claim is Outcome 2:
continuation and \(A_6\)-off dynamics cannot recover the leftover
spectrum. Outcome 4 says why a compressed *objective* is the wrong
object to hold.

### 4c. What we do not claim (the QAOA-circuit MPS)

Aer MPS of the *degree-2 QAOA circuit* at 10 qubits ties the
hardware from \(\chi\ge 2\) (`results/eon_qaoa_result.json`). That is
expected: the circuit is the shadow, and the shadow is
low-rank. Publishing the tie is the control that keeps Outcome 4
honest. The poor-objective evidence is 4a/4b, on the true
instance, not on the quadratic circuit.

---

## Supporting measurements (not extra outcomes)

**Held-out quality.** On 12 scenario draws the optimizer never saw,
the certified plan’s thermal congestion is 1.229 ± 0.169 versus
MILP 2.068 ± 0.321 (**−40.5%**) and no-build 71.08 ± 4.27. Capex
is 1.60× the MILP plan (11.42 vs 7.12). Both numbers travel
together. Receipt: `eon_v4_advantage.json` → `held_out`.

**Hidden voltage.** 8 of 1,024 plans improve DC congestion while
worsening voltage versus no-build. The certified plan clears 286
voltage violations; MILP clears 130. Receipt: `hidden_congestion`.

**Storage sizing under the E.ON leftover spectrum (statevector, not a
hardware job).** Firming storage for the decisive microgrid (mg9,
20.85 p.u. load, 24 h, 10% rms) is sized against four fluctuation
models at identical rms (3 seeds × 400 draws). Colored by the
**real-time certified leftover spectrum** (principal line 0.222
cyc/step, this package, no cloud job): **9.76 ± 0.91 p.u.h**. Colored
by a two-pole **continuation** of the same arm’s \(G(\tau)\):
**6.94 ± 0.69 p.u.h — 29% undersize**. White-noise 10.67 ± 2.40;
AR(1) matched to leftover lag-1 9.57 ± 2.12. At this 20q resolution
white/AR sit near the real-time number; the decision-changing error
is the continuation. Receipt: `eon_storage_sizing.json`. A previous
draft sized storage against a 64-rung sister-track spectrum
(`daa9pn4e74ec73akj9i0`). That job is **not an E.ON result** and is
not cited here.

**20q field circuits.** Same operator as Outcome 2. Derived
waveforms frozen in `eon_nisq_field.json`. Full-\(k\) leftover on
Heron is a new job on go — not a recaption of any sister-track
flight.

---

## Scope

- The certified plan's value is robustness: −40.5% held-out congestion
  and 286 voltage violations cleared, at 1.60× the MILP plan's capex —
  the resilience-per-euro trade a DSO prices, both numbers on one receipt.
- The advantage is **of route**: real-time leftover \(S(\omega)\) versus
  ill-posed continuation and \(A_6\)-off dynamics. It is not supremacy
  at 10 binaries and not a 100-qubit hardware-vs-MPS result.
- Hardware two-point ranking is **partial** (degree-2 collapsed on
  kingston, inverted vs certified on marrakesh). Full-\(k\) leftover
  \(S(\omega)\) on a device is a protocol, not a job.
- Outcome 4 remains the true-cost MPS sweep. Representation is the
  supporting wall; dynamics is the crossing.

## Reproducibility

```
python verify.py                 # two-build + Schmidt + crossing gates (~1 min)
python eon_rubric_mps.py         # line set + MPS chi-sweep (~30 s)
python eon_v4_advantage.py       # held-out, hidden voltage, Schmidt (~45 s)
python eon_nisq_field.py         # 20q operator, Delta-L gate (~90 s)
python eon_dynamics_crossing.py  # leftover S(w) vs continuation / A6-off (~5 min)
python eon_full_k_leftover.py    # retrieve leftover series; default NO submit
```

No quantum credentials to audit. Heron submit of the full-\(k\)
leftover series needs a human go:
`EON_FULL_K_SUBMIT=1 python eon_full_k_leftover.py --submit --k-grid dense`.
Phase I closes 2026-09-15.

**Compatibility and runtime (per §5.3 of the challenge statement).**
Every circuit in this package is a Qiskit `QuantumCircuit`; flights use
`qiskit-ibm-runtime` SamplerV2 with no custom transpilation passes —
the E.ON team can execute and validate every hardware result in
standard Qiskit by pointing the flight scripts at any backend
(`IBM_QUANTUM_CRN` environment variable; backend name as argument).
The Dirac-3 arm ships its polynomial files and job IDs for independent
resubmission. End-to-end runtimes: classical audit ~3 minutes; the
dynamics crossing ~5 minutes; each hardware job minutes of QPU time;
the full pipeline replays well inside the brief's few-hour limit.

---
*Merlin Digital. The expansion objective is a congestion field.
The leftover spectrum is the route. Continuation cannot hold it.*
