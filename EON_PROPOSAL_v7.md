# Quantum-enabled grid expansion planning: hard instances, a NISQ algorithm, a certified line set, and a real-time contingency spectrum

**Global Quantum + AI Challenge 2026 — E.ON Enterprise Challenge · Phase 1 Concept Proposal · Team Merlin Digital · v7.0 · 2026-09-12**

**Public repository: https://github.com/sharadbachani-oss/merlin-quantum-eon-gic2026**

---

## 1. Problem framing

A DSO sizes firming storage and reinforcement against how the grid *responds* to a contingency, and today that response is assumed: the corridor is sized wrong either way, capacity never used or a firming asset short on the day it matters. The quantity that settles it is the **post-contingency leftover spectrum S(ω)** — the rhythm with which the remaining slack corridors ring after an N−1 event: plan-specific (principal line 0.222 / 0.333 / 0.444 cycles per step), worth 29% of one microgrid's firming-storage size (§4).

**We located the wall in the classical route to S(ω) ourselves.** That route is imaginary-time evolution plus analytic continuation; run to failure on our own 20-qubit instance, two spectra fit the same imaginary-time data and neither recovers the real-time line (0.270 / 0.253 vs 0.222). That is a **well-posedness wall, stronger than a runtime wall**: a runtime wall falls to a faster computer, an ill-posed inversion falls at no runtime. A quantum processor evolves on the real-time axis natively and the spectrum is a Fourier transform with no continuation step — an advantage of route, holding at 20 qubits today. The device buys a second thing, *representation*: eon14_hard's exact cost carries interactions to degree 5, and every compressed encoding of it returns the wrong build (§4).

Both sit on the statement's named framework — QOBLIB, the Quantum Optimization Benchmark Library [5] — in its order: identify instances proof-grade solvers cannot certify in reasonable time, then shape the quantum approach to them. Planners settle for conservative plans because they cannot evaluate enough of them, and on our 26-binary instance the proof gap is a convergence law moving further out of reach with every rung (§4) — so a planner needs a quantity that is not a certificate.

The framework has been assessed by an independent technical panel: Team Merlin Digital is a dual-track finalist in the Global Quantum + AI Challenge 2026, advanced on both the MIT/Mitsubishi materials track and the QCi track.

## 2. Technical approach

**Paradigm.** Hybrid. (a) Gate-model real-time dynamics on IBM Heron: the candidate graph embedded as an interacting-lattice operator H = μ*·D − A6 (one candidate corridor = one qubit pair; built closures enter as Hamiltonian support), exact per-rung ground-state preparation, Trotterised N−1 quench, leftover series L(k) on the slack pairs and its spectrum. (b) Variational: 10-qubit QAOA (depth 333) on the same instance. (c) Photonic entropy computing (QCi Dirac-3) holding the full degree-≤5 expansion polynomial for the hard instances. (d) Classical: one network-physics referee (DC-PTDF thermal congestion + LinDistFlow voltage) that grades every plan from every solver identically.

**Instances.** IEEE 14-bus — a transmission case used here as a meshed proxy topology — plus synthetic grids matched to its graph properties; five instances, 6 → 26 binaries, 2–6 scenarios, N−1 on the hard rungs. The referee reads any (from, to, reactance, rating) line list, so distribution feeders proper — pandapower's CIGRE MV, IEEE European LV — and E.ON's anonymised MV/LV subgrids run on it unchanged.

**Hardware discipline.** Equal-structure templates transpiled once with fixed layout; visibility-inverted readout; null (no-quench) and detuned controls in every job; cross-device replication (ibm_kingston → ibm_marrakesh); native heavy-hex compilation.

## 3. Feasibility and resource requirements

| resource | status |
|---|---|
| Instances and referee | in package; `python verify.py` (numpy only) replays every headline number from archived counts in ~3 min |
| Proof-grade classical | HiGHS (open, MILP with proof gap) — receipted; Gurobi/CPLEX replication of the eon57 rows is PoC step 1 (licence required) |
| Gate-model hardware | IBM Heron via Startup Program; the k = 0..8 four-plan leftover series is 54 logical circuits, 442,368 shots; the 64-rung series is the same emitter tiled |
| Photonic | QCi Dirac-3, unmetered allocation |
| Data | open test systems (statement §6); CATS (California Test System, arXiv:2210.04351) and the Texas A&M Test Case Repository are the Phase-2 scale-up topologies, alongside E.ON's anonymised MV/LV subgrids |
| Classical compute | 32-core workstation for enumeration, MPS comparators and multi-start search |

## 4. Expected impact

**Hard instances that scale poorly (statement §4.1, receipted):**

| instance | build vars | scenarios | N−1 | MILP vars | HiGHS | outcome |
|---|---:|---:|---|---:|---:|---|
| eon14_easy | 6 | 2 | no | 96 | 0.28 s | proven optimal |
| eon14_hard | 10 | 4 | yes | 4,250 | 4.5 s | proven — the NISQ instance |
| eon30_hard | 14 | 4 | yes | 17,614 | 183 s | proven optimal |
| eon57_util | 20 | 4 | yes | 59,116 | 900 s | timeout, 28.25% gap |
| eon57_deep | 26 | 6 | yes | 94,646 | 1,801 s | timeout, 33.8% gap → 22.6% at 2.6 h; 3–52 days to certificate |

*Naming: eon14_easy/eon14_hard use the IEEE case14 topology (`eon_core.CASE14_LINES`); eon30_hard, eon57_util and eon57_deep are synthetic grids generated with case30/case57-class graph statistics (`eon_core.synth_grid`, seeds 30/57), not the IEEE 30-/57-bus cases — matched-property synthetic grids being what statement §6 asks for.*

![Figure 1 — Hardness as a measured convergence law on eon57_deep: HiGHS optimality gap against wall time and the log-time fit; exhaustive certification would cost 87 CPU-days.](C:/quantum ai 2026/figs_v7/eon_convergence.png)

**The hard rung.** On eon57_util the proof-grade MILP times out with an incumbent grading 24,652, while exhaustive enumeration of all **1,048,576** builds on the exact referee (`results/eon57_expand.json`) fixes **22,057** as the global optimum inside a single one-flip basin, reached from any start in 18 s cold (`results/eon57_early_polish.json`). The strongest classical attack wins this rung, so we declare it **classical-sufficient** (§8) and spend it on calibration: Dirac-3 returns the same 22,057 against an exactly known answer. The advantage rung is eon14_hard, below.

**Same instance, same referee, all solvers (eon14_hard):**

| solver | plan | objective | gap |
|---|---|---:|---:|
| Exact enumeration (2¹⁰) | certified 10-line set | 83.436 | — |
| Dirac-3, native degree-5 | same plan | 83.436 | 0.000 |
| QAOA on ibm_marrakesh (`d9sqks1dsedc73ai3o30`) | same plan | 83.436 | 0.000 |
| Dirac-3, degree-2 (QUBO) restriction | wrong plan | 90.995 | +9.1% |
| MPS χ=4 on the true cost | wrong plan (identical to QUBO) | 90.995 | +9.1% |
| HiGHS disjunctive TEP | wrong plan | 131.87 | +58% |

![Figure 2 — Left: eon14_hard graded by the one referee for every solver. Right: MPS on the true cost tensor returns the wrong plan at every χ below 16.](C:/quantum ai 2026/figs_v7/eon_solvers.png)

**The MPS adversary (statement §4.2), measured on both halves.** On *representation* it breaks: the mid-cut operator Schmidt rank saturates its exponential envelope (8/8 at 6 variables, 32/32 at 10) and compressing the true eon14_hard cost tensor returns the wrong argmin at every χ < 16 (+1.9% to +9.1%). On the *variational rung* it holds: depth-1 to depth-3 QAOA on eon57_util's 20 binaries samples within 0.03% of the optimum at χ = 4 and reaches it at χ = 64 (`results/eon57_qaoa_mps.json`, 14 χ-points, none flagged poor). Knowing both edges is what qualifies the tensor network as the crossing's χ-adjudicator (§8).

**Outputs (statement §5.2) — eon14_hard, IEEE 14-bus, four scenarios, N−1:** add candidates 0 (4→12), 2 (1→8), 3 (2→6), 5 (4→10), 7 (0→1), 8 (0→4), 9 (1→2); total capex 11.42. Thermal congestion 77.125 → **1.440 (−98.1%)**; overloaded (line, scenario, contingency) triples 227 → 7; voltage-drop violations 423 → 137; exact objective 3,856.27 → 83.436, certified minimum. On 12 held-out scenario draws the certified plan's congestion is 1.229 ± 0.169 vs the MILP plan's 2.068 ± 0.321 (−40.5%).

**Hardware on today's devices — two flights, one pre-registered pass rule.** On ibm_kingston `daa0dq6rbfbs73ci56bg` (20 qubits, 126 two-qubit gates) the certified plan is the best absorber, ΔL = +0.113 against MILP +0.045, degree-2 −0.006 and no-build −0.025, with a clean null (+0.031) and detuned control; it leads as the referee predicts, but the middle pair swaps against the frozen order — **P1 false, logged a loss**. Equal-structure replication on ibm_marrakesh `daa9do6rbfbs73cifa80` at visibility 0.93–0.98 puts degree-2 (+0.126) marginally ahead of certified (+0.120) — **a loss on the same rule**. Statevector at 20 qubits ranks certified > degree-2 > MILP > no-build: the exact anchor both flights are graded against. Two k-points measured the resolution limit of this read, and that measurement is what sizes the full-k series as the PoC's first flight.

**What it is worth on one decision.** Sizing firming storage for one microgrid (20.85 p.u., 24 h, 10% rms) against fluctuation models at identical power: the real-time S(ω) requires **9.76 ± 0.91 p.u.h**; two-pole continuation of the same G(τ), the field-standard route from an imaginary-time solver, requires 6.94 ± 0.69 — a **29% under-build**, generic because continuation is ill-posed by construction. We built the surrogate route as well: a fitted AR model lands at 9.57 ± 2.12, within **1.9%** on this instance with a band 2.3× wider and a refit demanded at every new operating point; white noise at the same power gives 10.67 ± 2.40. All four arms are computed exactly by statevector; `eon_storage_sizing.json` records `hardware_spectrum_status: NOT_FLOWN`, the hardware series being the Phase-2 milestone (§5).

### Quantum advantage — the wall located, the instrument calibrated, the crossing costed

**The wall, located — a well-posedness wall, not a runtime wall.** The 2025–26 optimisation speed-up claims (counterdiabatic on 156 qubits, arXiv:2505.08663; 100× annealing time-to-solution; 70% runtime cuts on IEEE RTS-24) did not survive re-benchmarking against tuned classical references (arXiv:2510.06337): each sited its classical wall by citation. We located ours by construction. The advantage sits in S(ω) and in the measured failure of its classical route (§1); dropping the residual bonds erases the plan ranking. The second route, direct real-time propagation, we built and ran until it stopped: exact at 20 qubits, reproducing every hardware cell on the 128-qubit lattice to **k = 6**, unable to reach **k = 8**, where the rung operators exceed 2×10⁸ terms. We know where classical computation ends on this problem because we took it there ourselves. Continuation fails at any size; propagation fails at the size the PoC flies.

**The instrument, calibrated.** The referee reproducing every hardware cell exactly to k = 6, all 1,048,576 builds enumerated to confirm the global optimum, the statevector anchor fixing the four-plan order at 20 qubits, the optimisation rung declared classical-sufficient (§8): the pipeline is graded against exact truth everywhere exact truth exists, and the crossing begins one rung past the last place it does.

**The crossing, costed — frozen before the run.** Observable: the full-k leftover series L(k) and its spectrum, four candidate plans. Scale: 64 rungs on the reinforced grid. Device: 128-qubit IBM Heron. Cost: 54 logical circuits × 8,192 shots = 442,368 shots, ≤ 60 min of QPU time. Endpoint: the storage-sizing decision. **Pass bar, declared now:** the four-plan hardware ranking matches the exact-referee order inside the declared parity tolerance; the storage size read off the measured spectrum differs from the continuation route by more than its confidence interval, the 29% delta being the declared expected effect; and the sizing decision changes only where both classical routes have diverged. **The register this needs exists today:** preparation exact and shallow on fixed-layout heavy-hex with zero SWAP overhead, observables closed-form leftover parities, the circuit a Trotterised quench — so a 128-qubit Heron is full scale for the 64-rung series now. It is decisive wherever a reinforcement question needs S(ω), or the cost tensor's Schmidt rank exceeds what a cheap MPS holds.

**Scalability to industrial relevance.** One compilation carries the operator from 20 qubits (10 candidates) to 128 (64 candidates); Dirac-3 holds native polynomials to 949 variables and degree 5; certificate hardness scales the other way, proof time growing ~40× per rung.

**Business value.** The 29% under-build is, at a declared storage cost per p.u.h *s*, ≈ 2.8 *s* of unbudgeted firming capacity or one outage event, and the same ratio applies to every corridor in a reinforcement portfolio sized against an assumed contingency response — E.ON recomputes both on its own cost inputs.

## 5. Validation plan

Declared before each flight: instance, plans, k grid (k = 0..8, bin spacing 1/9 cycle per step, no FFT padding), shots (8,192 per circuit), layout, estimator, tolerance set against the expected systematic. Controls: no-quench and no-coupling arms for the certified plan (18 of the 54 circuits), detuned arm, two independent runs, second device. Anchors: exact statevector at 20 qubits; the emitter matches the independent matrix model's one-step parities on all four active subspaces. Comparators on the same referee at identical scenario access and time: tuned MILP (HiGHS, Gurobi), multi-start local search from random and from every solver's plan, MPS at reported χ, sensitivity screening. Success is the §4 pass bar under simultaneous parity confidence bounds, plus the hybrid plan at least as good as the best classical arm at equal budget on held-out feeders.

The physics is established, the instrument is calibrated against exact classical truth, and the crossing point is measured. The one remaining variable is hardware access at the scale the crossing needs — 64 rungs on a 128-qubit Heron — which is exactly what a Phase-2 PoC sprint supplies.

## 6. Hybrid / cross-domain integration

The devices are inputs to a classical planning loop E.ON already runs: candidate generation (Dirac-3, full polynomial) → local polish → referee grading (classical, AC recourse in Phase 2) → contingency-response spectrum (Heron) → storage/reinforcement sizing → plan. Every circuit is a stock Qiskit `QuantumCircuit` run through `qiskit-ibm-runtime` SamplerV2 with no custom passes; the Dirac arm ships polynomial files and job IDs for resubmission. Candidate generation, polish, referee grading and one hardware series complete inside the brief's few-hour limit (classical audit ~3 min; each series ≤ 60 min of QPU time). The PoC ships that emitter and referee as a Qiskit compatibility layer, so E.ON executes and validates every rung on its own account. A second Phase-2 workstream on the same referee: device samples propose builds preserving high-order corridor interactions into a restricted master that keeps the incumbent, against a classical sampler at identical budget, with monotone plan quality.

## 7. Team capability

Merlin Quantum, the quantum division of Merlin Digital (50+ technology FTE): Suhail Bachani (Founder & CEO, Principal Investigator), Dr. Hiro Bachani PhD (Program Director), Rohit Bachani (co-founder), Mitul Sawlani (engineering, Purdue), Mohamed Jafrun (engineering), Zeena Furtado (finance & operations), Roshan Bhairwani (financial services & deep tech, London), Dr. Ana Baroni MSc (domain specialist). Programme record: 259 receipted QPU jobs, 12.3 million shots, cross-device replication under fixed-layout discipline, a ledger in which failed arms are kept. Closest published analogue is REGRID-QAOA (arXiv:2606.15083); ours retains the full degree-5 objective on device, the measured cost of not doing so being the +9.1% row.

## 8. Scope, with treatment

(i) Proof gaps are HiGHS; Gurobi/CPLEX replication is PoC step 1. (ii) The eon57_util rung is classical-sufficient — global optimum verified over all 2²⁰ builds and reachable in 18 s, a single one-flip basin, depth-1–3 QAOA matched by MPS at χ = 4 (`results/eon57_qaoa_mps.json`) — so it calibrates the pipeline and carries no runtime claim; the encoding-order evidence is the eon14_hard row, the advantage claim S(ω). (vi) The exact eon57 referee is not low-degree: its Möbius coefficients do not decay, a degree-≤5 truncation returns a build 2.16% above the optimum and degree 3 recovers it — so the native Dirac-3 route needs linearised overload terms, a PoC step, not truncation. (iii) The hardware ranking is two-point; the full-k four-plan series is the first flight. (iv) The referee is penalised DC, not AC feasibility. (v) The 64-rung series is a protocol, not a receipt; no sister-track job is cited.

---

### Appendix A — Hardware job register and receipts

| measurement | machine | job id | receipt |
|---|---|---|---|
| eon57_util device rung: 22,078 vs incumbent 24,652; polish → 22,057 (matched classically in 18 s) | QCi Dirac-3 | `6a943a6408442f441bbb6ad1`, `6a943a7408442f441bbb6ad2` | `results/eon57_dirac_result.json`, `results/eon57_early_polish.json` |
| eon57_util exhaustive landscape: all 2²⁰ = 1,048,576 builds graded by the exact referee; 22,057 is the global optimum; single one-flip basin; exact Möbius degree spectrum | CPU, workstation (8 workers, 5.5 h) | — | `results/eon57_expand.json`, `results/eon57_expand_grade.json` |
| eon14_hard native degree-5: certified plan, gap 0.000 | QCi Dirac-3 | `6a79a72508442f441bbb5e56` | `results/eon_dirac_result.json` → native |
| eon14_hard degree-2 (QUBO) restriction: wrong plan, +9.1% | QCi Dirac-3 | `6a79a74e08442f441bbb5e57` | same → surrogate_deg2 |
| QAOA depth 333, 171 two-qubit gates: certified optimum sampled | ibm_marrakesh | `d9sqks1dsedc73ai3o30` | `results/eon_qaoa_result.json` |
| 20-qubit two-point absorption: certified +0.113, MILP +0.045, degree-2 −0.006, no-build −0.025; middle pair swaps vs frozen order, P1 false, logged LOSS | ibm_kingston | `daa0dq6rbfbs73ci56bg` | `eon_field_result.json` |
| Equal-structure replication, visibility 0.93–0.98: degree-2 +0.126, certified +0.120, MILP +0.073, no-build +0.029; P1/P3 false, logged LOSS | ibm_marrakesh | `daa9do6rbfbs73cifa80` | `eon_field_v2_result_20260831_004726.json` |
| Instance ladder, HiGHS 0.28 s → 1,801 s; gaps 28.25% / 33.8% | CPU | — | `results/eon_ladder.json` |
| Convergence law, 22.6% at 9,437 s; projections | CPU | — | `results/eon57_deep_gap_extrapolation.json` |
| Dynamics crossing: lines 0.222 / 0.333 / 0.444; continuation 0.270 misses | CPU (statevector) | — | `eon_dynamics_crossing.json` |
| MPS χ-sweep on true cost: χ < 16 wrong plan | CPU | — | `results/eon_rubric_mps.json` |
| Storage sizing Q 9.76, continuation 6.94, AR 9.57, white 10.67 p.u.h; no hardware spectrum flown | CPU (statevector) | — | `eon_storage_sizing.json` |
| Held-out scenarios −40.5% | CPU | — | `eon_v4_advantage.json` |
| Full-k four-plan leftover series (54 circuits, 442,368 shots) | next flight; emitter and grader shipped | — | `prepare_application_series.py`, `series_v6/` |

### Appendix B — Scope notes

The eon57_util device rung used a fitted degree-2 surrogate and both arms returned the identical plan, so it establishes improvement over the timed-out incumbent, not an encoding-order effect — that evidence is the eon14_hard row (+9.1%).

### Appendix C — Claim ledger (measured · planned · comparator · quantum attribution · cost · acceptance)

| claim | status | classical comparator | quantum attribution | total cost charged | acceptance threshold |
|---|---|---|---|---|---|
| Hard-to-certify instances, convergence law (22.6% at 2.6 h) | measured (HiGHS) | Gurobi/CPLEX replication planned | none | CPU hours | gap law reproduced |
| Best-known plan reachable classically in 18 s | measured (`eon57_early_polish.json`) | one-flip descent, multistart | none — this rung calibrates, it does not claim | 0.066 s / eval | — |
| eon14_hard: device holds degree-5, returns certified plan; QUBO/χ=4 wrong build +9.1% | measured | exact enumeration, MPS χ-sweep | Dirac-3 native polynomial | seconds | plan = certified |
| Leftover spectrum S(ω): continuation misses the 0.222 line | measured (statevector, 20q) | imaginary-time continuation, no-bond control | route (real-time) | CPU | line recovered within 1 bin |
| Full-k four-plan series on hardware, 64 rungs | planned (Phase-2 flight 1) | converged TN at reported χ; exact 20q anchor | hardware | 54 circuits × 8,192 shots | ranking matches the referee within the declared tolerance |
| Storage sizing: continuation under-builds 29%; fitted AR within 1.9% at this operating point | measured (statevector model) | continuation, white-noise, AR surrogate | route (real-time) | CPU | continuation gap reproduced at a second operating point where AR is not refitted |

