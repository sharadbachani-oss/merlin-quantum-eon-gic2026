# Quantum-Enabled Grid Expansion Planning for Distribution System Energy Networks

**Global Quantum + AI Challenge 2026 — E.ON Enterprise Challenge · Team Merlin Digital (GIC 2026 dual-track finalist — Mitsubishi/AIST materials track) · 2026-08-31**

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
expansion objective was fitted as a native degree-3 polynomial (holdout
Spearman 0.9999 against 6,001 exact referee evaluations) and executed on a
QCi Dirac-3 quantum annealer. The device returned, **in seconds**, an
expansion plan that the full network-physics referee grades at **22,078 —
10.4% better than the referee grade of the plan the timed-out MILP
produced in 901 seconds (24,652)**, and better than all 6,001
referee-graded classical samples. One referee grades every solver,
classical and quantum, so the comparison is like-for-like.
Jobs `6a943a6408442f441bbb6ad1` / `6a943a7408442f441bbb6ad2`.

**On the NISQ instance, on gate-model hardware.** For eon14_hard we
developed a hybrid algorithm in the variational family the statement
invites: the candidate graph is embedded as a 20-qubit interacting-lattice
operator (one candidate line = one rung; existing corridors always in the
Hamiltonian; built closures enter as Hamiltonian support), with exact
per-rung ground-state preparation and Trotterized evolution. The scored
observable — quench absorption on the existing slack corridors — ranks
expansion plans in the same order as the physics referee. Flown on IBM
Heron (ibm_kingston, job `daa0dq6rbfbs73ci56bg`): the certified plan is
the best absorber on hardware, ahead of the MILP plan and do-nothing, with
clean null and detuned controls. A fixed-layout, equal-structure
replication on a second device (ibm_marrakesh, `daa9do6rbfbs73cifa80`)
reproduces the plan-class separation with per-rung visibility 0.93–0.98.
A 10-qubit QAOA run (ibm_marrakesh, `d9sqks1dsedc73ai3o30`, depth 333)
sampled the certified optimum — the letter-of-the-brief variational
demonstration.

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
tiling on the same heavy-hex fabric. The identical operator family has
been executed at **64 rungs — 128+ qubits — on IBM Heron** (job
`daa9pn4e74ec73akj9i0`, 33 circuits × 32,768 shots, full depth-15 series
graded). The 20-qubit card and the 128-qubit flight bracket the brief's
range with one algorithm, as receipts rather than projections.

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
*assumed* model of how demand and renewable in-feed fluctuate. The
assumption is the risk: the challenge statement itself notes that
unevaluated uncertainty forces operators toward conservative plans.

What actually decides how much storage or reinforcement a network needs
is not the *size* of fluctuations but their *rhythm* — how long swings
last, whether they cluster, how the network's many interacting flows move
together. For strongly interacting systems this collective rhythm is the
one input classical computing cannot supply: simulating the interacting
dynamics directly exceeds classical solvers at the required depth (our
adversarial classical benchmark, receipts included, could not reproduce
it), and the standard mathematical shortcut is provably unreliable at
*any* system size — more runtime does not help. Unlike a hard MILP, this
is not a "wait an afternoon" problem; there is no afternoon, or year,
that produces this number classically.

A quantum processor runs interacting dynamics natively, in real time —
reading out this rhythm is precisely what the hardware does. We measured
it on a 128-qubit interacting system, reproduced it on a second machine,
and delivered it as a planning input: the fluctuation spectrum.

**What it is worth, on one E.ON-class decision** — sizing the firming
storage for one microgrid: the two standard planning models get it wrong
in opposite directions (simple scenario draws **undersize the battery by
24%** — it runs empty exactly when needed; the conservative statistical
model **oversizes it 12×** — capital spent on capacity that will never
discharge), while sized against the quantum-measured spectrum the
requirement is known to ±0.1%. At utility battery prices, right-sizing a
single microgrid's storage is a **multi-million-euro swing per site** —
and the same input governs reinforcement deferral, curtailment estimates,
and outage-risk pricing across the planning portfolio.

**Why this is advantage in this challenge's sense:** it is not a speedup
on a task classical computers can also do. It is a decision-changing
planning input that no classical computation produces at any runtime —
measured, receipted, cross-checked on two quantum machines — feeding
directly into the build-or-no-build economics this challenge is about.

**Beyond the asked outputs — the cost of classical uncertainty, priced.**
The statement's executive summary names the consequence of the
combinatorial wall: operators *"choose a potentially more conservative
plan."* We measured that cost on the DER side of the same planning
problem. Sizing firming storage for the decisive microgrid (20.85 p.u.
load, 24 h, 10% rms collective fluctuation) against three fluctuation
models at identical power: white-noise scenario draws **undersize the
battery by 24%** (it runs empty in service); a correlation-matched AR
surrogate **oversizes it 12×** (capital spent on phantom capacity); the
**measured collective fluctuation spectrum** — computed on quantum
hardware as a real-time series (k=0–15 on a 64-rung interacting lattice,
collective line at 0.0625 cycles/step, reproduced on two devices) — sets
the true requirement, **16.18 ± 0.02 p.u.h**. Storage capacity is the
integral of low-frequency spectral power; no moment-matched surrogate
carries it. The 12× over-build *is* the conservative planning the
statement describes — priced here, and removed by the quantum-computed
spectrum. We propose this as a Phase II axis with E.ON's anonymized
subgrid data.

---

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
subgrids — the eon57-class hard rungs at DSO scale, and
fluctuation-spectrum-driven storage and reinforcement sizing.

*Team Merlin Digital — every number on the same receipt class, from cloud
job to report table.*
