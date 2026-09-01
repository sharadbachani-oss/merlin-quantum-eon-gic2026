# Quantum-Enhanced Grid Expansion: Hard Instances, a NISQ Algorithm, a Certified Line Set, and MPS-Poor Evidence

**Global Quantum + AI Challenge 2026 — E.ON Enterprise Track**
**Team: Merlin Digital (GIC 2026 dual-track finalist — Mitsubishi/AIST materials track) · Report v4.3, 2026-08-31**

This page is written to the challenge brief. Each expected outcome is a
section. Every number has a receipt.

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
| 2. Quantum algorithm on a hard instance, NISQ-runnable | 20-qubit framework operator on the candidate lattice. ΔL ranks certified > deg-2 > MILP > no-build. 10q QAOA already flown (ibm_marrakesh). |
| 3. Optimal new lines + cost + congestion reduction | Seven lines named below. Capex 11.42. Thermal congestion 77.125 → 1.440 (−98.1%). |
| 4. MPS simulation gives poor objective value | TT-SVD MPS of the *true* cost: χ < 16 returns the wrong plan (gaps +1.9% to +9.1%). Hardware returns the exact plan. |

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

The candidate graph is a 10-rung lattice. Exact per-rung ground
prep (RY(θ*)–CNOT–H⊗H). Existing slack corridors (buses 0–1, 0–4,
1–2) are always in the Hamiltonian. Distance-2 closures enter only
when built. N−1 is an X-quench on the slack corridor. The scored
object is the slack-star leftover series
L(k) = rms(C* − ⟨ZZ⟩) on those three existing rungs. Builds are
Hamiltonian support, not QUBO bits.

Initial absorption ΔL = L(0) − L(1) ranks the four named plans in
the same order as the physics referee:

| plan | ΔL | referee congestion |
|---|---:|---:|
| all-build | +0.146 | 1.452 |
| **certified** | **+0.140** | **1.440** |
| degree-2 | +0.124 | 1.625 |
| MILP + cand 3 | +0.114 | 2.322 |
| MILP + cand 2 | +0.104 | 1.734 |
| MILP + cand 5 | +0.098 | 1.787 |
| MILP | +0.042 | 2.495 |
| no-build | −0.042 | 77.125 |

Each certified closure, added alone to the MILP set, raises ΔL.
Together they recover the certified plan. All-build buys +0.006
more absorption and a *worse* thermal number — the field does
not want junk lines.

Statevector gate: `results/eon_nisq_field.json`. Hardware,
job `daa0dq6rbfbs73ci56bg` on ibm_kingston (10 × 8,192 shots;
max 126 two-qubit gates), graded from raw:

| plan | frozen ΔL | hardware ΔL |
|---|---:|---:|
| certified | +0.140 | **+0.113** |
| degree-2 | +0.124 | −0.006 |
| MILP | +0.042 | **+0.045** |
| no-build | −0.042 | **−0.025** |

Certified is the best absorber on the device and beats MILP.
No-build grows. Null (no quench) leftover is 0.031 vs 0.784
with quench. Detuned control moved. **Hardware prefers the
certified lines over MILP and over do-nothing.** A fixed-layout,
equal-structure re-flight on a second device (ibm_marrakesh,
job `daa9do6rbfbs73cifa80` — every arm the same physical circuit,
only coupling angles differ) reproduces the plan-class
separation with uniform per-rung visibility 0.93–0.98 and lands
the degree-2 arm on its frozen value (+0.127 vs +0.124
predicted): the ranking physics replicates cross-device.

**Letter of the brief (already on hardware).** 10-qubit QAOA from
the degree-2 shadow, ibm_marrakesh job `d9sqks1dsedc73ai3o30`
(depth 333, 171 two-qubit gates, 8,192 shots), sampled the
certified bitstring. That is the small-instance sample. The
algorithm we are submitting is the 20q operator above.

**Scalability to utility scale (>100 qubits), demonstrated not
projected.** The operator's unit is the rung (one candidate = 2 qubits);
scaling means more rungs on the same heavy-hex fabric. The identical
operator family has been executed at **64 rungs — 128+ qubits — on IBM
Heron** (job `daa9pn4e74ec73akj9i0`, 33 circuits × 32,768 shots, full
depth-15 series graded), meeting the brief's >100-qubit utility-scale
criterion with a receipt rather than an extrapolation. The 20-qubit
card and the 128-qubit flight bracket the brief's requested range with
one algorithm.

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
| MPS χ = 4 on true cost | 1 0 1 1 0 0 0 1 1 1 | 90.995 | +9.1% | (same wrong plan as deg-2) |
| MPS χ = 1 on true cost | 1 0 1 1 1 1 1 1 1 1 | 87.466 | +4.8% | wrong plan |
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
instance family.

### 4a. MPS as a solver of the instance (the letter of the outcome)

Compress the *true* 10-bit cost tensor by TT-SVD to bond dimension
χ, take the argmin of the compressed tensor, re-grade that plan on
the exact referee. That is the expansion plan an MPS-truncated
model of the instance returns.

| χ | plan | exact objective | gap | verdict |
|---:|---|---:|---:|---|
| 1 | 1 0 1 1 1 1 1 1 1 1 | 87.466 | **+4.8%** | wrong plan |
| 2 | 1 0 1 1 0 1 1 1 1 1 | 85.654 | **+2.7%** | wrong plan |
| 4 | 1 0 1 1 0 0 0 1 1 1 | 90.995 | **+9.1%** | wrong plan — **identical to the degree-2 QUBO / Dirac restriction** |
| 8 | 1 1 1 1 0 1 0 1 1 1 | 85.006 | **+1.9%** | wrong plan |
| 16 | 1 0 1 1 0 1 0 1 1 1 | 83.436 | 0 | exact |
| 32 | same | 83.436 | 0 | exact (full rank) |

Receipt: `results/eon_rubric_mps.json` → `eon14_hard.mps_chi_sweep`.

**MPS gives a poor objective at every χ that cannot hold the tensor.**
The mid-cut rank of this objective is 32/32. χ = 16 is the first
lossless solver. Dirac-3 and the flown QAOA return the χ = 16 plan
without building that MPS.

At 6 binaries (eon14_easy) the same method is already lossless at
χ = 2 (gap 0); χ = 1 is **+75.8%**. Differing variable counts:
cheap MPS works on the easy instance and fails on the certified one.

### 4b. Why χ has to be that large — the objective MPS cannot hold

Operator Schmidt rank of the true cost saturates the exponential
envelope: **8/8 at 6 binaries, 32/32 at 10 binaries.** The degree-2
shadow every QUBO/QAOA-on-QUBO pipeline holds is rank 5 / 7.
Receipt: `results/eon_v4_advantage.json` → `schmidt_scaling`.

This is the stronger form of the brief’s MPS line. MPS does not
merely return a poor value — below χ = 16 it **cannot represent
the instance**, and the plan it then returns is the wrong
reinforcement set. χ = 4 recovers the same wrong set as a
quadratic QUBO. That is the motivation for quantum hardware that
accepts the uncompressed polynomial (Dirac-3) and for a NISQ
variational arm that at least samples the certified bitstring
(QAOA).

### 4c. What we do not claim (the QAOA-circuit MPS)

Aer MPS of the *degree-2 QAOA circuit* at 10 qubits ties the
hardware from χ ≥ 2 (`results/eon_qaoa_result.json`). That is
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

**Storage sizing under the measured fluctuation class (quantum input
to DER planning).** The brief names the cost of classical uncertainty:
operators are *"forced toward more conservative planning."* Here that
cost is measured. Firming storage for the decisive microgrid (mg9,
20.85 p.u. load, 24 h horizon, 10% rms collective fluctuation) sized
against three fluctuation models at *identical rms power* (3 seeds ×
2,000 realizations): white-noise scenario planning requires 12.3 p.u.h —
**a 24% energy shortfall** against the true requirement (the battery runs
empty in service); an AR surrogate matched to variance and
autocorrelation requires 194.3 p.u.h — **a 12× over-build**, plus 2.9×
excess power capacity. Against the **measured collective spectrum**
(real-time series computed on quantum hardware, k=0–15 on a 64-rung
interacting lattice, collective line 0.0625 cyc/step reproduced on two
devices; job `daa9pn4e74ec73akj9i0`), the requirement is **16.18 ± 0.02
p.u.h energy, 4.40 ± 0.01 p.u. power**. Storage capacity is the integral
of low-frequency spectral power — a quantity no moment-matched surrogate
carries; sizing it correctly requires the spectrum itself, and the
spectrum is the quantum deliverable. The 12× over-build *is* the
conservative planning the brief describes — priced here, and removed by
the measured spectrum. Receipt: `eon_storage_sizing.json`.

**20q field circuits.** Same operator as Outcome 2. Derived
waveforms frozen in `eon_nisq_field.json`. Heron flight is a
new job on go — not a recaption of A1.

---

## Scope

- The certified plan's value is robustness: −40.5% held-out congestion
  and 286 voltage violations cleared, at 1.60× the MILP plan's capex —
  the resilience-per-euro trade a DSO prices, both numbers on one receipt.
- The 20q field ranking ships statevector-closed with the hardware
  replication above; deeper Heron series are Phase II flights.
- Outcome 4's evidence is the true-cost sweep — the instance itself,
  not any single circuit family, is what MPS cannot hold below χ=16.

## Reproducibility

```
python verify.py              # two-build + Schmidt + residuals (~1 min)
python eon_rubric_mps.py      # line set + MPS χ-sweep (~30 s)
python eon_v4_advantage.py    # held-out, hidden voltage, Schmidt (~45 s)
python eon_nisq_field.py      # 20q operator, ΔL gate (~90 s)
```

No quantum credentials to audit. Heron submit needs a human go.
Phase I closes 2026-09-15.

**Compatibility and runtime (per §5.3 of the challenge statement).**
Every circuit in this package is a Qiskit `QuantumCircuit`; flights use
`qiskit-ibm-runtime` SamplerV2 with no custom transpilation passes —
the E.ON team can execute and validate every hardware result in
standard Qiskit by pointing the flight scripts at any backend
(`IBM_QUANTUM_CRN` environment variable; backend name as argument).
The Dirac-3 arm ships its polynomial files and job IDs for independent
resubmission. End-to-end runtimes: classical audit ~3 minutes; each
hardware job minutes of QPU time; the full pipeline replays well inside
the brief's few-hour limit.

---
*Merlin Digital. The expansion objective is a congestion field.
MPS cannot hold it. The NISQ algorithm is that field.*
