# Quantum-enabled grid expansion planning: hard instances, a NISQ algorithm, a certified line set, and a real-time contingency spectrum

**Global Quantum + AI Challenge 2026 — E.ON Enterprise Challenge · Phase 1 Concept Proposal · Team Merlin Digital (GIC 2026 dual-track finalist — Mitsubishi/AIST materials track) · v7.0 · 2026-09-12**

**Public repository: https://github.com/sharadbachani-oss/merlin-quantum-eon-gic2026**

---

## 1. Problem framing

Distribution expansion is a build-or-no-build decision over candidate corridors, coupled to network physics across many operating scenarios and N−1 contingencies. The statement's own diagnosis is that the combinatorial explosion forces planners toward conservative plans because they cannot evaluate enough of them. We follow the statement's named framework [5] in its order: identify instances that proof-grade classical solvers cannot certify in reasonable time, then shape the quantum approach to those instances.

Two things frame the quantum contribution here. First, the hard instances are hard to *certify*: on our 26-binary instance the proof gap is a measured convergence law (33.8% at 480 s → 22.6% after 2.6 h), extrapolating to 17–21% still unproven after a full afternoon and 3–52 days to a certificate; exhaustive certification costs 87 CPU-days — while good plans are cheap to find, which is why we do not claim solver runtime. Second, and decisive, what a DSO actually needs to size storage or reinforcement is not a static objective but the **rhythm with which the existing slack corridors ring after a contingency** — a real-time dynamical spectrum S(ω) of the reinforced network. The scalable classical route to that object, imaginary-time evolution plus analytic continuation, is mathematically ill-posed at any runtime: on our 20-qubit instance two spectra fit the same imaginary-time data and neither recovers the real-time line (0.270 / 0.253 vs 0.222). A quantum processor evolves on the real-time axis natively; the spectrum is a Fourier transform with no continuation step. That is an advantage of route, it holds at 20 qubits today, and it is the class of computation every 2025–26 verified quantum-advantage candidate occupies.

## 2. Technical approach

**Paradigm.** Hybrid. (a) Gate-model real-time dynamics on IBM Heron: the candidate graph embedded as an interacting-lattice operator H = μ*·D − A₆ (one candidate corridor = one qubit pair; existing corridors always in the Hamiltonian; built closures enter as Hamiltonian support), exact per-rung ground-state preparation, Trotterised N−1 quench, leftover series L(k) on the slack pairs and its spectrum. (b) Variational: 10-qubit QAOA (depth 333) on the same instance. (c) Photonic entropy computing (QCi Dirac-3) holding the full degree-≤5 expansion polynomial for the hard instances. (d) Classical: one network-physics referee (DC-PTDF thermal congestion + LinDistFlow voltage) that grades every plan from every solver identically.

**Instances.** IEEE 14-bus (pandapower distribution) and synthetic grids matched to its graph properties; five instances, 6 → 26 binaries, 2–6 scenarios, N−1 on the hard rungs.

**Hardware discipline.** Equal-structure parameterised templates transpiled once with fixed layout; visibility-inverted readout (per-rung visibility 0.93–0.98); null (no-quench) and detuned controls in every job; cross-device replication (ibm_kingston → ibm_marrakesh). Compilation is native heavy-hex with zero SWAP overhead; a 64-rung (128-qubit) series is the same compilation, tiled.

## 3. Feasibility and resource requirements

| resource | status |
|---|---|
| Instances and referee | in package; `python verify.py` (numpy only) replays every headline number from archived counts in ~3 min |
| Proof-grade classical | HiGHS (open, MILP with proof gap) — receipted; Gurobi/CPLEX replication of the eon57 rows is PoC step 1 (licence required) |
| Gate-model hardware | IBM Heron via Startup Program; the k = 0..8 four-plan leftover series is 54 logical circuits, 442,368 shots; the 64-rung series is the same emitter tiled |
| Photonic | QCi Dirac-3, unmetered allocation |
| Data | open test systems; Phase 2 targets E.ON's anonymised MV/LV subgrids |
| Classical compute | 32-core workstation for enumeration, MPS comparators and multi-start search |

Assumptions: DC-PTDF + LinDistFlow referee (penalised DC objective, not full AC feasibility — AC recourse is charged as a classical solve per accepted plan in Phase 2). Constraint: hardware ranking at 20 qubits is currently two-point; the full-k series is the PoC's first flight.

## 4. Expected impact

**Hard instances that scale poorly (statement §4.1, receipted):**

| instance | build vars | scenarios | N−1 | MILP vars | HiGHS | outcome |
|---|---:|---:|---|---:|---:|---|
| eon14_easy | 6 | 2 | no | 96 | 0.28 s | proven optimal |
| eon14_hard | 10 | 4 | yes | 4,250 | 4.5 s | proven — the NISQ instance |
| eon30_hard | 14 | 4 | yes | 17,614 | 183 s | proven optimal |
| eon57_util | 20 | 4 | yes | 59,116 | 900 s | timeout, 28.25% gap |
| eon57_deep | 26 | 6 | yes | 94,646 | 1,801 s | timeout, 33.8% gap → 22.6% at 2.6 h; 3–52 days to certificate |

![Figure 1 — Hardness as a measured convergence law on eon57_deep: HiGHS optimality gap against wall time, the log-time fit, and the fastest observed closing rate; exhaustive certification would cost 87 CPU-days.](C:/quantum ai 2026/figs_v7/eon_convergence.png)

**The hard rung, both ways.** On eon57_util the disjunctive proof-grade MILP times out at 901 s with a 28.25% gap, and its incumbent grades 24,652 on the exact referee. The optimal plan, 22,057 — now verified as the **global optimum** by exhaustive enumeration of all 1,048,576 builds on the exact referee (`results/eon57_expand.json`, 5.5 h on 8 workstation cores) — is reached by one-flip descent from *any* start — no-build in 18 s (281 evaluations), each of 12 random starts within 45–170 s, and from a 0.5 s LP-relaxation incumbent in 13 s (`results/eon57_early_polish.json`, measured on the same clock). The device route on this instance — a degree-2 surrogate fitted from 6,001 referee evaluations (≈ 400 s of referee time), Dirac-3 basin-finding, then the same polish — reaches the same 22,057 and is not competitive on time. We report that as measured: on eon57_util the difficulty is entirely in the *certificate*, not in finding the plan, and the optimisation rung is a classical result. What the device establishes is elsewhere — on eon14_hard it holds the full degree-5 polynomial and returns the certified plan where every compressed representation returns the wrong one (table below), and the advantage this proposal claims is the real-time contingency spectrum, not solver runtime.

**Same instance, same referee, all solvers (eon14_hard):**

| solver | plan | objective | gap |
|---|---|---:|---:|
| Exact enumeration (2¹⁰) | certified 10-line set | 83.436 | — |
| Dirac-3, native degree-5 | same plan | 83.436 | 0.000 |
| QAOA on ibm_marrakesh (`d9sqks1dsedc73ai3o30`) | same plan | 83.436 | 0.000 |
| Dirac-3, degree-2 (QUBO) restriction | wrong plan | 90.995 | +9.1% |
| MPS χ=4 on the true cost | wrong plan (identical to QUBO) | 90.995 | +9.1% |
| HiGHS disjunctive TEP | wrong plan | 131.87 | +58% |

![Figure 2 — Left: eon14_hard graded by the one referee for every solver — the device holding the full degree-5 polynomial and QAOA return the certified plan; the QUBO restriction and a χ=4 MPS return the same wrong plan. Right: MPS on the true cost tensor returns the wrong plan at every χ below 16.](C:/quantum ai 2026/figs_v7/eon_solvers.png)

**MPS gives poor objective value (statement §4.2).** Compressing the true 10-variable cost tensor to bond dimension χ and taking its argmin returns the wrong plan at every χ < 16 (+1.9% to +9.1%); the mid-cut operator Schmidt rank saturates its exponential envelope (8/8 at 6 variables, 32/32 at 10). Cheap MPS is exact where the instance is easy and wrong where it is hard.

**Outputs (statement §5.2) — eon14_hard, IEEE 14-bus, four scenarios, N−1:** add candidates 0 (4→12), 2 (1→8), 3 (2→6), 5 (4→10), 7 (0→1), 8 (0→4), 9 (1→2); total capex 11.42. Thermal congestion 77.125 → **1.440 (−98.1%)**; overloaded (line, scenario, contingency) triples 227 → 7; voltage-drop violations 423 → 137; exact objective 3,856.27 → 83.436, certified minimum. On 12 held-out scenario draws the certified plan's congestion is 1.229 ± 0.169 vs the MILP plan's 2.068 ± 0.321 (−40.5%).

**Hardware on today's devices.** ibm_kingston `daa0dq6rbfbs73ci56bg` (20 qubits, 126 two-qubit gates): certified plan is the best absorber, ΔL = +0.113, ahead of MILP +0.045 and no-build −0.025, clean null and detuned controls. Equal-structure replication on ibm_marrakesh `daa9do6rbfbs73cifa80` recovers degree-2 at +0.127 vs frozen +0.124 at visibility 0.93–0.98. Statevector leftover ranks certified > degree-2 > MILP > no-build with principal lines 0.222 / 0.333 / 0.444 cycles per step; the hardware ranking is two-point and partial, and the full-k series is the PoC's first flight.

**What it is worth on one decision.** Sizing firming storage for one microgrid (20.85 p.u., 24 h, 10% rms) against fluctuation models at identical power coloured by this leftover spectrum: the real-time S(ω) requires **9.76 ± 0.91 p.u.h**; the two-pole continuation of the same imaginary-time data requires 6.94 ± 0.69 — a **29% undersize** that the real-time route avoids (`eon_storage_sizing.json`, statevector).

### Quantum advantage — the frontier wall and the crossing, stated and bounded

**The field's direction, and its wall.** The 2025–26 optimisation claims — digitised counterdiabatic optimisation "outperforming CPLEX in seconds" on 156-qubit devices (arXiv:2505.08663), 700× hybrid sequential speed-ups, 100× annealing time-to-solution on spin glasses, 70% runtime cuts on IEEE RTS-24 expansion — have been re-benchmarked with tuned classical references and end-to-end accounting (arXiv:2510.06337), which concludes that runtime advantage has not been demonstrated under experimentally grounded metrics. Our own receipt maps it exactly: on the hard rung one-flip descent from no-build reaches the best-known 22,057 in 18 s of referee time, faster than the surrogate-plus-device route. Basin-finding is where classical search keeps pace, as the framework's own admissibility analysis predicts.

**The crossing.** We measured our own optimisation rung against the cheapest classical challenge and report the result: on eon57_util one-flip descent reaches the global optimum in 18 s — the exhaustive landscape has a single one-flip basin — so no runtime claim is made there. We place the advantage in the quantity a planner actually needs after the plan: the **post-contingency leftover spectrum S(ω)** of the reinforced network. Its scalable classical route — imaginary-time evolution plus analytic continuation — is ill-posed, and we measured the failure on the 20-qubit instance: two continuations fit the same G(τ) and neither recovers the 0.222 real-time line (0.270 / 0.253); dropping the residual bonds erases the plan ranking. The statement's own MPS test is met in the same package: below χ = 16 the simulator cannot hold the instance and returns the wrong build. Hardware evolves on the real-time axis; the spectrum is a Fourier transform with no continuation step, and it changes a storage decision by 29%. **Where it is decisive:** wherever the instance's Schmidt rank exceeds what a cheap MPS holds — measured here at 10 binaries, where χ < 16 returns the wrong build — and at every reinforcement question that needs S(ω) after the plan; anchored today at 20 qubits by statevector and two-device hardware absorption, with the 64-rung full-k series and two-sided classical adjudication as the Phase-2 flight.

**Scalability to industrial relevance.** One candidate corridor is one qubit pair, so the operator tiles from 20 qubits (10 candidates) to 128 (64 candidates) on the same heavy-hex compilation with zero SWAP overhead; Dirac-3 holds native polynomials to 949 variables and degree 5. The certificate-hardness law scales the other way — proof time grows ~40× per rung — which is exactly why a planner needs a quantity other than a certificate to act on, and S(ω) is that quantity. Instances built from IEEE 14-bus transfer to E.ON's anonymised MV/LV subgrids by changing the topology file only.

**Business value, bounded.** On one microgrid sizing decision (20.85 p.u., 24 h, 10% rms) the real-time spectrum requires 9.76 p.u.h of firming storage where the continuation route requires 6.94 — a 29% under-build that, at a declared storage cost per p.u.h *s*, is ≈ 2.8 *s* of unbudgeted capacity or one outage event; across a DSO's reinforcement portfolio the same ratio applies to every corridor sized against an assumed contingency response. The certified plan on eon14_hard cuts thermal congestion 98% at capex 11.42 and holds a 40% congestion advantage over the MILP plan on held-out scenarios. Stated as functions of E.ON's cost inputs, not as fixed sums.

**What a successful PoC demonstrates.** On E.ON's anonymised MV/LV subgrids: hard rungs certified as such with Gurobi/CPLEX proof gaps; native polynomial encodings on Dirac-3 with linearised overload terms rather than truncation (the exact eon57 landscape is not degree-5 representable: a degree-≤5 truncation returns a build 2.16% above the optimum while degree 3 recovers it), graded by the shared referee against multistart local search at equal total time; and the full-k leftover spectrum measured on hardware for the four candidate plans, feeding storage and reinforcement sizing with a quantity the classical route cannot produce well-posed.

## 5. Validation plan

Pre-registered per flight: instance, plans, k grid (k = 0..8, nine uniform samples, bin spacing 1/9 cycle per step, no FFT padding), shots (8,192 per circuit), layout, estimator, tolerance set against the expected systematic. Controls: no-quench and no-coupling arms for the certified plan (18 of the 54 circuits), detuned arm, two independent runs, second device. Anchors: exact statevector at 20 qubits; the emitter matches the independent matrix model's one-step parities on all four active subspaces. Classical comparators on the same referee with identical scenario access and total time: tuned MILP (HiGHS, Gurobi), multi-start local search from random and from every solver's plan, MPS at reported χ, sensitivity-based screening. Success: (i) hardware four-plan ranking matches the referee order with simultaneous parity confidence bounds inside the pre-registered tolerance; (ii) the hybrid plan is better than or equal to the best classical arm at equal total budget on held-out feeders, or reaches the same feasible objective at lower total cost; (iii) storage sizing from the measured spectrum differs from the continuation route by more than its confidence interval. Falsification: any of the three failing is reported as such.

## 6. Hybrid / cross-domain integration

The quantum devices are inputs to a classical planning loop that E.ON already runs: candidate generation (Dirac-3, full polynomial) → local polish → referee grading (classical, AC recourse in Phase 2) → contingency-response spectrum (Heron) → storage/reinforcement sizing → plan. Every circuit is a stock Qiskit `QuantumCircuit` run through `qiskit-ibm-runtime` SamplerV2 with no custom passes; the Dirac arm ships polynomial files and job IDs for resubmission. Runtime: classical audit ~3 min; each hardware job minutes of QPU time.

## 7. Team capability

Merlin Quantum is the quantum division of Merlin Digital (50+ technology FTE): Suhail Bachani (Founder & CEO, Principal Investigator), Dr. Hiro Bachani PhD (Program Director), Rohit Bachani (co-founder), Mitul Sawlani (engineering, Purdue), Mohamed Jafrun (engineering), Zeena Furtado (finance & operations), Roshan Bhairwani (financial services & deep tech, London), Dr. Ana Baroni MSc (domain specialist). GIC 2026 dual-track finalist. Programme record: 259 receipted QPU jobs, 12.3 million shots, cross-device replication under fixed-layout discipline, and a pre-registration ledger in which failed arms are kept. Closest published analogue is REGRID-QAOA (arXiv:2606.15083); our approach differs in retaining the full degree-5 objective on device, and the measured cost of not doing so is the +9.1% row above.

## 8. Scope, with treatment

(i) Proof gaps are HiGHS; Gurobi/CPLEX replication is PoC step 1. (ii) On eon57_util the global optimum (verified over all 2²⁰ builds) is reachable by one-flip descent in 18 s and the landscape has a single one-flip basin — the optimisation rung is classical-sufficient and no runtime claim is made; the encoding-order evidence is the eon14_hard row and the advantage claim is S(ω). (vi) The exact eon57 referee is not a low-degree polynomial: its Möbius coefficients do not decay with degree, a degree-≤5 truncation returns a build 2.16% above the optimum and degree 3 recovers it — so the native Dirac-3 route on this class needs linearised overload terms, a PoC step, not truncation. (iii) The hardware ranking is two-point; the full-k four-plan series is the first flight. (iv) The referee is penalised DC, not AC feasibility — AC recourse is charged per accepted plan in Phase 2. (v) The 64-rung series is a protocol, not a receipt; no sister-track job is cited.

---

### Appendix A — Hardware job register and receipts

| measurement | machine | job id | receipt |
|---|---|---|---|
| eon57_util device rung: plan graded 22,078 vs incumbent 24,652; polish → 22,057 (matched by one-flip descent from no-build in 18 s) | QCi Dirac-3 | `6a943a6408442f441bbb6ad1`, `6a943a7408442f441bbb6ad2` | `results/eon57_dirac_result.json`, `results/eon57_early_polish.json` |
| eon57_util exhaustive landscape: all 2²⁰ = 1,048,576 builds graded by the exact referee; 22,057 is the global optimum; single one-flip basin; exact Möbius degree spectrum | CPU, workstation (8 workers, 5.5 h) | — | `results/eon57_expand.json`, `results/eon57_expand_grade.json` |
| eon14_hard native degree-5: certified plan, gap 0.000 | QCi Dirac-3 | `6a79a72508442f441bbb5e56` | `results/eon_dirac_result.json` → native |
| eon14_hard degree-2 (QUBO) restriction: wrong plan, +9.1% | QCi Dirac-3 | `6a79a74e08442f441bbb5e57` | same → surrogate_deg2 |
| QAOA depth 333, 171 two-qubit gates: certified optimum sampled | ibm_marrakesh | `d9sqks1dsedc73ai3o30` | `results/eon_qaoa_result.json` |
| 20-qubit two-point absorption: certified +0.113, MILP +0.045, no-build −0.025 | ibm_kingston | `daa0dq6rbfbs73ci56bg` | `eon_field_result.json` |
| Equal-structure replication: degree-2 +0.127 vs frozen +0.124, visibility 0.93–0.98 | ibm_marrakesh | `daa9do6rbfbs73cifa80` | `eon_field_v2_result_20260831_004726.json` |
| Instance ladder, HiGHS 0.28 s → 1,801 s; gaps 28.25% / 33.8% | CPU | — | `results/eon_ladder.json` |
| Convergence law, 22.6% at 9,437 s; projections | CPU | — | `results/eon57_deep_gap_extrapolation.json` |
| Dynamics crossing: lines 0.222 / 0.333 / 0.444; continuation 0.270 misses | CPU (statevector) | — | `eon_dynamics_crossing.json` |
| MPS χ-sweep on true cost: χ < 16 wrong plan | CPU | — | `results/eon_rubric_mps.json` |
| Storage sizing 9.76 vs 6.94 p.u.h | CPU (statevector) | — | `eon_storage_sizing.json` |
| Held-out scenarios −40.5% | CPU | — | `eon_v4_advantage.json` |
| Full-k four-plan leftover series (54 circuits, 442,368 shots) | next flight; emitter and grader shipped | — | `prepare_application_series.py`, `series_v6/` |

### Appendix B — Scope notes

The eon57_util device rung used a fitted degree-2 surrogate; both submitted arms returned the identical plan, so that rung establishes improvement over the timed-out incumbent, not an encoding-order effect — the encoding-order evidence is the eon14_hard row (+9.1%). No sister-track 64-rung job is cited as an E.ON result. The 64-rung series is a protocol with the expected signature written before any shot.

### Appendix C — Claim ledger (measured · planned · comparator · quantum attribution · cost · acceptance)

| claim | status | classical comparator | quantum attribution | total cost charged | acceptance threshold |
|---|---|---|---|---|---|
| Hard-to-certify instances, convergence law (22.6% at 2.6 h) | measured (HiGHS) | Gurobi/CPLEX replication planned | none | CPU hours | gap law reproduced |
| Best-known plan reachable classically in 18 s | measured (`eon57_early_polish.json`) | one-flip descent, multistart | none — withdrawn as a device claim | 0.066 s / eval | — |
| eon14_hard: device holds degree-5, returns certified plan; QUBO/χ=4 wrong build +9.1% | measured | exact enumeration, MPS χ-sweep | Dirac-3 native polynomial | seconds | plan = certified |
| Leftover spectrum S(ω): continuation misses the 0.222 line | measured (statevector, 20q) | imaginary-time continuation, no-bond control | route (real-time) | CPU | line recovered within 1 bin |
| Full-k four-plan series on hardware, 64 rungs | planned (Phase-2 flight 1) | converged TN at reported χ; exact 20q anchor | hardware | 54 circuits × 8,192 shots | ranking matches referee within pre-registered tolerance |
| Storage sizing changes by 29% under S(ω) | measured (model) | continuation, white-noise, AR | route | CPU | decision difference > its CI on a physical grid reference |

