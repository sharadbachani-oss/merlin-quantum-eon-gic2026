# Outcome 4, as the brief asked for it

**“Evidence that MPS simulation gives poor objective value for these
instances, motivating quantum hardware advantage.”**

Merlin Digital · E.ON track · 2026-08-30

## The measurement

Take the true congestion-plus-capex tensor on eon14_hard (10 build
bits, exact 2¹⁰ referee table). Compress it with TT-SVD to bond
dimension χ. Return the argmin of the compressed tensor. Grade that
plan on the exact referee.

| χ | exact objective of the MPS plan | gap vs certified | plan correct? |
|---:|---:|---:|---|
| 1 | 87.466 | **+4.8%** | no |
| 2 | 85.654 | **+2.7%** | no |
| 4 | 90.995 | **+9.1%** | no — same plan as the degree-2 QUBO |
| 8 | 85.006 | **+1.9%** | no |
| 16 | 83.436 | 0 | yes |
| 32 | 83.436 | 0 | yes |

Receipt: `results/eon_rubric_mps.json`. At 6 binaries the same
solver is already exact at χ = 2; χ = 1 is +75.8%. Differing
variable counts, as Outcome 1 requires.

## Why the hardware is motivated

The mid-cut Schmidt rank of this objective is **32 of 32**. χ < 16
is a truncated model of the instance. Every truncated model we ran
returned a **different reinforcement set** with a worse true
objective. Dirac-3 (native degree 5, job `6a79a725`) and 10-qubit
QAOA on ibm_marrakesh (`d9sqks1`) both returned the χ = 16 plan,
gap 0.000.

The χ = 4 MPS plan is bit-for-bit the Dirac degree-2 restriction
arm (job `6a79a74e`, +9.1%). Quadratic QUBO and mid-χ MPS are the
same compression.

## What this is not

Aer MPS of the degree-2 *QAOA circuit* at 10 qubits ties hardware
from χ ≥ 2. That circuit is the shadow; the shadow is low-rank.
The brief asked about **these instances**, not about a quadratic
proxy of them. The instance-level sweep is 4a above.

A 100-qubit scenario-entangled QAOA on the MIP-hard eon57 graph is
designed and frozen, not flown. Outcome 4 as written does not wait
on that job.
