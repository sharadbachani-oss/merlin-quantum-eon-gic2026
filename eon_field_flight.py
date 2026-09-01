"""
E.ON congestion-field flight — new Heron job, not a recaption of A1.

Human go: 2026-08-30. Open plan only. Frozen ΔL ranking before shots.

Circuits (10):
  no_build / milp / deg2 / certified  ×  k = 0, 1     ranking
  certified null (no quench) k = 0                    must sit on C*
  certified detuned dt = 0.36 k = 1                   must move

PASS: hardware ΔL order is certified > deg2 > milp > no_build
      after one fitted damping envelope.
TIE / LOSS: publish the device order. Line set still has the QAOA receipt.

Stages: derive | fly | grade
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

import eon_nisq_field as F

WORK = Path(r"C:\quantum ai 2026\eon")
OPEN_CRN = __import__("os").environ.get("IBM_QUANTUM_CRN", "")
OPEN_BACKENDS = ["ibm_fez", "ibm_kingston", "ibm_marrakesh"]
SHOTS = 8192
DT_CTRL = 0.36
STATE = WORK / "eon_field_state.json"
C_STAR = F.C_STAR
EXISTING = F.EXISTING

CORE = {
    "no_build": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "milp": [1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    "deg2_hw": [1, 0, 1, 1, 0, 0, 0, 1, 1, 1],
    "certified": [1, 0, 1, 1, 0, 1, 0, 1, 1, 1],
}


def leftover_from_counts(counts, rungs):
    tot = 0
    acc = np.zeros(len(EXISTING))
    for bits, c in counts.items():
        sb = bits.replace(" ", "")[::-1]
        tot += c
        for j, ri in enumerate(EXISTING):
            a, b = rungs[ri]
            if a >= len(sb) or b >= len(sb):
                continue
            zz = 1 - 2 * (int(sb[a]) ^ int(sb[b]))
            acc[j] += c * (C_STAR - zz)
    if tot == 0:
        return 1.0
    d = acc / tot
    return float(np.sqrt(np.mean(np.square(d))))


def stage_derive():
    src = json.loads((WORK / "eon_nisq_field.json").read_text())
    by = {r["name"]: r for r in src["rows"]}
    frozen = {
        name: dict(dL01=by[name]["dL01"],
                   L0=by[name]["leftover_k"][0],
                   L1=by[name]["leftover_k"][1],
                   congestion=by[name]["congestion"],
                   plan=CORE[name])
        for name in CORE
    }
    order = ["certified", "deg2_hw", "milp", "no_build"]
    tag = time.strftime("%Y%m%d_%H%M%S")
    pend = dict(
        card="EON FIELD PENDING (frozen before shots)",
        tag=tag,
        shots=SHOTS,
        dt=F.DT,
        dt_ctrl=DT_CTRL,
        mu=F.MU,
        theta_star=F.THETA_STAR,
        c_star=C_STAR,
        existing=list(EXISTING),
        quench_rung=F.QUENCH_RUNG,
        nq=20,
        n_bonds=src["n_bonds"],
        frozen_dL=frozen,
        frozen_order=order,
        model_gate=True,
        prereg=dict(
            P1="ΔL hardware order is certified > deg2_hw > milp > no_build "
               "(same as referee and SV gate)",
            P2="certified L(0) ≈ L(1) of the other arms is forbidden: "
               "certified must absorb (ΔL > 0) and more than milp",
            P3="null (no quench) leftover on slack star is below quench k=0 "
               "by ≥ 0.15 — prep sits near C*, quench is real",
            P4="detuned dt=0.36 certified k=1 moves vs main k=1 "
               "(|ΔL_ctrl − ΔL_main| > 0.02)",
        ),
        dual=dict(
            PASS="hardware ΔL ranking matches frozen order after one "
                 "damping envelope. Headline: NISQ congestion field "
                 "names the certified lines.",
            LOSS="publish the device order. QAOA receipt still holds "
                 "the bitstring. No caption swap.",
        ),
        arms=["no_build_k0", "no_build_k1", "milp_k0", "milp_k1",
              "deg2_hw_k0", "deg2_hw_k1", "certified_k0", "certified_k1",
              "certified_null_k0", "certified_ctrl_k1"],
    )
    dest = WORK / f"eon_field_pending_{tag}.json"
    dest.write_text(json.dumps(pend, indent=2))
    STATE.write_text(json.dumps(dict(pending=str(dest)), indent=2))
    print(f"frozen {order}  pending -> {dest}")
    return 0


def connect(named=None):
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(instance=OPEN_CRN)
    if named:
        if named not in OPEN_BACKENDS:
            print("REFUSED: not an open-plan backend")
            sys.exit(3)
        return svc, svc.backend(named)
    pend = {}
    for b in OPEN_BACKENDS:
        try:
            pend[b] = svc.backend(b).status().pending_jobs
        except Exception:
            pend[b] = 10 ** 6
    best = min(pend, key=pend.get)
    print(f"  queue: {pend} -> {best}")
    return svc, svc.backend(best)


def make_circuits(nq):
    geo = F.geometry()
    circs, names = [], []
    for name, x in CORE.items():
        for k in (0, 1):
            circs.append(F.qiskit_circuit(geo, x, k, nq, quench=True, dt=F.DT))
            names.append(f"{name}_k{k}")
    circs.append(F.qiskit_circuit(geo, CORE["certified"], 0, nq,
                                  quench=False, dt=F.DT))
    names.append("certified_null_k0")
    circs.append(F.qiskit_circuit(geo, CORE["certified"], 1, nq,
                                  quench=True, dt=DT_CTRL))
    names.append("certified_ctrl_k1")
    return circs, names, geo


def stage_fly():
    if not STATE.exists():
        stage_derive()
    st = json.loads(STATE.read_text())
    pend = json.loads(Path(st["pending"]).read_text())
    print("FROZEN ORDER", pend["frozen_order"])
    print("P1 dL hardware order matches referee / SV gate")
    svc, backend = connect()
    nq = backend.target.num_qubits
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    circs, names, geo = make_circuits(nq)
    qcs = transpile(circs, backend, optimization_level=1)
    depths = [qc.depth() for qc in qcs]
    twos = [qc.num_nonlocal_gates() for qc in qcs]
    print("transpiled:")
    for nm, d, t in zip(names, depths, twos):
        print(f"  {nm:22s}  depth {d:4d}  2q {t:4d}")
    if max(twos) > 370:
        print(f"REFUSED: max 2q {max(twos)} exceeds ~370 CX wall")
        return 2
    s = SamplerV2(mode=backend)
    s.options.dynamical_decoupling.enable = True
    s.options.dynamical_decoupling.sequence_type = "XpXm"
    job = s.run(qcs, shots=SHOTS)
    st.update(backend=backend.name, main_job=job.job_id(),
              main_names=names, depths=depths, twos=twos,
              nq=nq, submitted=time.strftime("%Y-%m-%dT%H:%M:%S"))
    STATE.write_text(json.dumps(st, indent=2))
    print(f"EON FIELD MAIN submitted: {job.job_id()}  "
          f"{len(qcs)} x {SHOTS} on {backend.name}")
    return 0


def stage_grade():
    st = json.loads(STATE.read_text())
    pend = json.loads(Path(st["pending"]).read_text())
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(instance=OPEN_CRN)
    job = svc.job(st["main_job"])
    status = job.status()
    print(f"job {st['main_job']} status {status}")
    if str(status) not in ("DONE", "JobStatus.DONE"):
        try:
            done = status.name == "DONE"
        except Exception:
            done = False
        if not done:
            print("not done")
            return 1
    res = job.result()
    geo = F.geometry()
    scored = {}
    for i, nm in enumerate(st["main_names"]):
        counts = res[i].data.c.get_counts()
        L = leftover_from_counts(counts, geo["rungs"])
        scored[nm] = L
        print(f"  {nm:22s}  L={L:.4f}")
    dL = {}
    for name in CORE:
        dL[name] = scored[f"{name}_k0"] - scored[f"{name}_k1"]
        print(f"  dL {name:12s}  {dL[name]:+.4f}  "
              f"frozen {pend['frozen_dL'][name]['dL01']:+.4f}")
    hw_order = [n for n, _ in sorted(dL.items(), key=lambda kv: -kv[1])]
    frozen = pend["frozen_order"]
    p1 = hw_order == frozen
    p2 = dL["certified"] > 0 and dL["certified"] > dL["milp"]
    p3 = scored["certified_null_k0"] < scored["certified_k0"] - 0.15
    p4 = abs((scored["certified_k0"] - scored["certified_ctrl_k1"])
             - dL["certified"]) > 0.02
    out = dict(job=st["main_job"], backend=st["backend"],
               leftover=scored, dL=dL, hw_order=hw_order,
               frozen_order=frozen, P1=p1, P2=p2, P3=p3, P4=p4,
               verdict="PASS" if (p1 and p2 and p3) else "LOSS")
    dest = WORK / "eon_field_result.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"hw order {hw_order}  frozen {frozen}  {out['verdict']}")
    print(f"-> {dest}")
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "fly"
    raise SystemExit({"derive": stage_derive, "fly": stage_fly,
                      "grade": stage_grade}[stage]())
