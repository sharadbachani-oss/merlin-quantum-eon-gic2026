# Quantum-Enabled Grid Expansion Planning for Distribution System Energy Networks

**Global Quantum + AI Challenge 2026 — E.ON Enterprise Challenge · Team Merlin Digital (GIC 2026 dual-track finalist — Mitsubishi/AIST materials track) · Report v5.0 · 2026-09-08**

This submission answers the challenge statement section by section, in its
own terms. Every number carries a receipt in the accompanying package
(claim → file → cloud job ID), replayable by the E.ON team in standard
Qiskit.

---

## Response to §4.1 — Primary objective

*"First identifying hard problem instances of a (potentially simplified)
problem formulation and then using these benchmark instances and resulting
problem formulation to shape the quantum algorithmic approach"* — we follow
the challenge's named framework [5] exactly, in that order.

### Hard problem instances that scale poorly with classical solvers

Our formulation is the binary build-or-no-build decision problem of [1]/[4]
class: candidate line additions on a distribution grid, objective =
investment cost + λ × network congestion, graded under multiple operating
scenarios with N−1 contingencies, voltage limits, and thermal ratings.
Instances are built from the open IEEE 14-bus case and synthetic grids
generated to match its graph properties.

| instance | build variables | scenarios | N−1 | MILP variables | proof-grade solver (HiGHS) | outcome |
|---|---:|---:|---|---:|---:|---|
| eon14_easy | 6 | 2 | no | 96 | 0.28 s | proven optimal |
| eon14_hard | 10 | 4 | yes | 4,250 | 4.5 s | proven optimal — **NISQ instance** |
| eon30_hard | 14 | 4 | yes | 17,614 | 183 s | proven optimal |
| **eon57_util** | **20** | 4 | yes | 59,116 | **900 s** | **TIMEOUT — 28.25% optimality gap** |
| **eon57_deep** | **26** | 6 | yes | 94,646 | **1,801 s** | **TIMEOUT — 33.8% optimality gap** |

Runtime grows ~40× per rung — the high-degree scaling the statement
describes. And the wall is not a timeout artifact: on eon57_deep the
proof gap closes as a measured convergence law (33.8% at 480 s → 33.8%
at 1,801 s → **22.6% after 2.6 hours**), which extrapolates to **17–21%
still unproven after a full afternoon (6 h)** and **3–52 days to a
certificate** at the fastest observed closing rate — while certifying by
exhaustive evaluation costs 87 CPU-days
(`results/eon57_deep_gap_extrapolation.json`). At 26 build decisions, no
classical route — solver or enumeration — proves optimality in a
reasonable runtime. This is precisely the wall that *"forces operators
toward more conservative planning."*

### The quantum algorithm, benchmarked on a hard instance

**On the hard rung.** For eon57_util (the 20-variable instance above), the
expansion objective was fitted as a polynomial surrogate over 6,001 exact
referee evaluations (**degree 2 as emitted to the device**; holdout
Spearman **0.9993**, holdout mean relative error 0.025) and executed on a
QCi Dirac-3 quantum annealer. The device returned, **in seconds**, an
expansion plan that the full network-physics referee grades at **22,078 —
10.44% better than the referee grade of the plan the timed-out MILP
produced in 901 seconds (24,652)**, and better than all 6,001
referee-graded classical samples. One referee grades every solver,
classical and quantum, so the comparison is like-for-like.

*Scope of this rung, stated precisely.* Both submitted arms on this
instance returned the **identical** plan and objective, and the receipt
records `native_degree: 2` with
`P2_native_beats_deg2: false`
(`results/eon57_dirac_result.json`). This rung therefore establishes an
**improvement over the timed-out proof-grade incumbent** — it does *not*
establish a degree-3-over-degree-2 encoding gain. The evidence for the
encoding-order effect is the separate eon14_hard receipt below (native
degree-5 recovers the certified optimum; the degree-2 restriction on the
same device returns the wrong plan at +9.1%), where the two arms return
genuinely different plans.
Jobs `6a943a6408442f441bbb6ad1` / `6a943a7408442f441bbb6ad2`.

**On the NISQ instance, on gate-model hardware.** For eon14_hard we
developed a hybrid algorithm in the variational family the statement
invites: the candidate graph is embedded as a 20-qubit interacting-lattice
operator \(H=\mu^\star D-A_6\) (one candidate line = one rung; existing
corridors always in the Hamiltonian; built closures enter as Hamiltonian
support), with exact per-rung ground-state preparation and Trotterized
evolution. The scored observable is the leftover series after an N−1
quench, and its spectrum \(S(\omega)\). Statevector leftover ranks
certified > degree-2 > MILP > no-build, matching the physics referee,
with principal lines 0.222 / 0.333 / 0.444 cycles per step. Imaginary-time
continuation of the same leftover misses the certified line (0.270 vs
0.222); dropping the residual \(A_6\) bonds makes every plan
\(\Delta L=+0.514\). That is an advantage of route, not a supremacy
claim (`eon_dynamics_crossing.json`). Flown on IBM Heron
(ibm_kingston, job `daa0dq6rbfbs73ci56bg`): the certified plan is the
best absorber on hardware (\(\Delta L=+0.113\)), ahead of MILP (+0.045)
and do-nothing (−0.025), with clean null and detuned controls. Degree-2
collapsed (−0.006). A fixed-layout, equal-structure replication on a
second device (ibm_marrakesh, `daa9do6rbfbs73cifa80`) recovers degree-2
(+0.127 vs frozen +0.124) at visibility 0.93–0.98; the device order is
deg-2 > certified. Hardware ranking is therefore **partial**. A
full-\(k\) leftover series (the device Fourier of \(S(\omega)\)) is
not flown — one-command `python eon_full_k_leftover.py` (retrieve
only), no job ID. The next flight is \(k=0..8\) on open Heron. A 10-qubit QAOA run
(ibm_marrakesh, `d9sqks1dsedc73ai3o30`, depth 333) sampled the
certified optimum — the letter-of-the-brief variational demonstration.

**Same instance, same referee, all solvers:**

| solver | plan returned | exact objective | gap |
|---|---|---:|---:|
| Exact enumeration (2¹⁰) | certified 10-line set | 83.436 | — |
| **Dirac-3, native degree-5** | **same plan** | **83.436** | **0.000** |
| QAOA on ibm_marrakesh | same plan | 83.436 | 0.000 |
| Dirac-3, degree-2 (QUBO) restriction | wrong plan | 90.995 | +9.1% |
| MPS χ=4 on the true cost | wrong plan (identical to QUBO) | 90.995 | +9.1% |
| HiGHS disjunctive TEP | wrong plan | 131.87 | +58% |

The quantum device holds the problem's full polynomial; every compressed
representation — the QUBO restriction and the low-χ MPS — returns the same
wrong reinforcement set.

---

## Response to §4.2 — Secondary objectives

**Differing variable counts.** Five instances, 6 → 26 binaries (table
above), spanning proven-optimal to proof-impossible.

**At least one instance on current NISQ hardware.** eon14_hard runs on
today's devices three ways: the 20-qubit operator (126 two-qubit gates),
10-qubit QAOA (171 two-qubit gates), and Dirac-3 native annealing — all
with cloud job receipts.

**MPS simulation gives poor objective value.** Compressing the true
10-variable cost tensor to bond dimension χ and taking its argmin: every
χ < 16 returns the **wrong expansion plan** (objective gaps +1.9% to
+9.1%); χ=4 reproduces exactly the degree-2 QUBO's wrong plan. The
mid-cut operator Schmidt rank of the true cost saturates its exponential
envelope (8/8 at 6 variables, 32/32 at 10) — below χ=16 an MPS *cannot
represent the instance*, and the plan it returns is the wrong build. At 6
variables the same method is lossless at χ=2: cheap MPS works exactly
where the instance is easy and fails where it is hard. This is the
motivation the statement asks for: the objective value from simulators is
poor, and quantum hardware that holds the uncompressed polynomial returns
the certified plan.

**Scalable from low qubit counts to utility scale (>100 qubits).** The
operator's unit is the rung (one candidate = 2 qubits), so scaling is
tiling on the same heavy-hex fabric. A 64-rung (128-qubit) leftover
series is the same compilation. **It is a protocol in this package, not
a receipt.** We do not import a sister-track 64-rung Heron job
(`daa9pn4e74ec73akj9i0`) as an E.ON spectrum. The 20-qubit card is
flown; the >100-qubit leftover series is the next flight, with the
expected signature written before any shot.

---

## Response to §5.2 — Outputs

**The set of new power lines** (eon14_hard, IEEE 14-bus, four scenarios,
N−1; candidates 0/2/3/5 are distance-2 closures, 7/8/9 parallel re-rates):

| add? | candidate | from → to | x (p.u.) | rating (p.u.) | capex |
|---|---:|---|---:|---:|---:|
| yes | 0 | 4 → 12 | 0.105 | 0.873 | 1.000 |
| yes | 2 | 1 → 8 | 0.118 | 0.927 | 1.260 |
| yes | 3 | 2 → 6 | 0.132 | 0.985 | 1.390 |
| yes | 5 | 4 → 10 | 0.128 | 0.803 | 1.650 |
| yes | 7 | 0 → 1 | 0.059 | 1.350 | 1.910 |
| yes | 8 | 0 → 4 | 0.223 | 0.900 | 2.040 |
| yes | 9 | 1 → 2 | 0.198 | 0.900 | 2.170 |
| | | | | **total capex** | **11.42** |

**Cost function values and congestion reduction:**

| metric | no-build | certified plan | reduction |
|---|---:|---:|---:|
| Thermal congestion (line-flow violations, referee) | 77.125 | **1.440** | **−98.1%** |
| Overloaded (line, scenario, contingency) triples | 227 | **7** | −220 |
| Voltage-drop violations | 423 | **137** | −286 |
| Exact objective (capex + 50 × congestion) | 3,856.27 | **83.436** | certified minimum |

On 12 held-out scenario draws the optimizer never saw, the certified
plan's congestion is 1.229 ± 0.169 versus the MILP plan's 2.068 ± 0.321
(**−40.5%**) — robustness under scenarios, the property the energy
transition demands of the network.

### The quantum advantage, in planning terms

Every expansion and storage decision a DSO makes is validated against an
*assumed* model of how a contingency is absorbed. The assumption is the
risk: the challenge statement itself notes that unevaluated uncertainty
forces operators toward conservative plans.

What actually decides how much storage or reinforcement a network needs
is not the *size* of a swing but its *rhythm* — how the leftover on the
existing slack corridors rings after N−1. That leftover spectrum
\(S(\omega)\) is a real-time dynamical object of \(H=\mu^\star D-A_6\).
The scalable classical route is imaginary-time leftover plus analytic
continuation, which is mathematically ill-posed: two spectra fit the
same \(G(\tau)\) on this instance and neither recovers the real-time
line (0.270 / 0.253 vs 0.222). Dropping the residual \(A_6\) bonds
erases the ranking entirely. Unlike a hard MILP, this is not a "wait
an afternoon" problem — more runtime does not well-pose continuation.

A quantum processor evolves on the real-time axis natively. The
spectrum is a Fourier transform with **no continuation step**. That is
an advantage of route, and it holds at this 20-qubit instance today.

**What it is worth, on one E.ON-class decision** — sizing the firming
storage for one microgrid (20.85 p.u., 24 h, 10% rms) against four
fluctuation models at identical power, colored by *this* leftover
spectrum (statevector, no cloud job): real-time \(S(\omega)\) requires
**9.76 ± 0.91 p.u.h**; the two-pole continuation of the same
\(G(\tau)\) requires **6.94 ± 0.69 p.u.h — 29% undersize**. White-noise
and lag-1 AR sit near the real-time number at this 20q resolution
(10.67 / 9.57). The decision-changing error is the continuation, not
the moment-matched surrogates. Receipt: `eon_storage_sizing.json`.

**Why this is advantage in this challenge's sense:** it is not a speedup
on a task classical computers can also do. It is a planning input whose
scalable classical route is ill-posed at any runtime. Hardware has
measured two-point absorption on two Heron chips (partial ranking,
receipts above). A device Fourier of the full leftover series is the
next flight, not a caption on a sister-track job.

**What we do not claim.** A previous draft sized storage against a
64-rung sister-track spectrum (`daa9pn4e74ec73akj9i0`, 16.18 p.u.h,
12× AR over-build). That job is not an E.ON result and is not cited
here. We also do not claim the two-point Heron ranking recovers the
frozen four-plan order, or absolute-energy supremacy at 10 binaries.
We propose the full-\(k\) leftover series, and E.ON's anonymized
medium/low-voltage subgrids, as the Phase II axis.

---

## Related work and positioning

**The state of the field.** Quantum optimisation for power systems is an
active area — optimal power flow, unit commitment, economic dispatch,
and topology/islanding are the recurring targets (PNNL, *A Review of
Quantum Computing Technologies in Power System Optimization*; *Quantum
computing for smart grid*, Nature Reviews Electrical Engineering 2026;
*Quantum Optimization for the Future Energy Grid: Quantum Utility
Prospects*, arXiv:2403.17495). 2026 has brought substantial industrial
engagement: Infleqtion with Eaton on grid contingency analysis under an
AFRL-funded programme, ORNL with IonQ on grid optimisation, and QCi's
own sponsorship of energy infrastructure use cases.

**The gap this submission addresses.** Surveying that work, the
consistent characteristic is *collaborative research and development
rather than documented benchmarks in which quantum definitively beats
classical practice on a stated metric*. Claims are typically
demonstrations of feasibility, or comparisons where the classical
baseline is not held to proof-grade standards.

This package is constructed to close exactly that gap:

- **One referee for every solver.** The full network-physics grader
  (DC-PTDF thermal congestion plus LinDistFlow voltage) scores classical
  and quantum results identically, so no comparison depends on which
  tool reported it.
- **Hardness as a measured convergence law, not a timeout.** On the
  26-variable instance the proof gap is tracked across four runtime
  budgets (33.8% → 22.6% at 2.6 h) and extrapolated, with exhaustive
  certification priced at 87 CPU-days. A single timeout proves nothing;
  a convergence law is falsifiable.
- **Adversarial attack on our own results.** Where a device result could
  plausibly be reproduced classically, we attacked it ourselves with
  local search and multi-start heuristics and report what survived.
- **A stated advantage class.** The optimisation results are benchmark
  comparisons against proof-grade MILP. The leftover spectrum
  \(S(\omega)\) is claimed as an advantage of route — real-time
  evolution versus ill-posed analytic continuation — not as runtime
  supremacy, and not as a 100-qubit hardware-vs-MPS result.

**Closest published formulation.** REGRID-QAOA (arXiv:2606.15083)
applies a resource-efficient hybrid QAOA to physics-constrained power
system islanding — the nearest published analogue to the operator
formulation in Outcome 2. Our approach differs in retaining the full
degree-5 objective on device rather than reducing to a QUBO; the
measured cost of that reduction is reported in Outcome 2 (+9.1% on the
same device, same instance).

## Response to §5.3 — Constraints

**Open-source framework and Qiskit compatibility layer.** Every circuit
in this package is a Qiskit `QuantumCircuit`; hardware runs use stock
`qiskit-ibm-runtime` SamplerV2 with no custom passes. The E.ON team can
re-execute and validate every gate-model result by setting the
`IBM_QUANTUM_CRN` environment variable and pointing the flight scripts at
any backend. The Dirac-3 arm ships its polynomial files and job IDs for
independent resubmission. A credential-free audit (`python verify.py`,
numpy only) replays every headline number from archived counts in ~3
minutes.

**Runtime.** Classical audit ~3 minutes; each hardware job minutes of QPU
time; the full pipeline replays well inside the few-hour limit.

**Open data (§5.4/§6).** IEEE 14-bus (pandapower distribution) plus
synthetic grids generated to match its graph properties. No proprietary
data used.

---

## Toward §5.2's closing invitation

The statement notes E.ON's interest in finalizing results and publishing
jointly. This package is structured for that: one physics referee for
every solver, frozen pre-registrations, cloud receipts for every claim,
and two Phase II axes ready for E.ON's anonymized medium/low-voltage
subgrids — the eon57-class hard rungs at DSO scale, and a full-\(k\)
leftover series on Heron (device Fourier of \(S(\omega)\), one-command
`python eon_full_k_leftover.py`, no job assigned).

*Team Merlin Digital — every number on the same receipt class, from cloud
job to report table.*
