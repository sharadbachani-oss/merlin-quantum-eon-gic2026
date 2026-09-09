"""
E.ON full-k leftover → S(ω) — one-command retrieve + optional submit.

Default is retrieve + protocol receipt. This script does not submit a
paid job unless EON_FULL_K_SUBMIT=1 is set in the environment.

It invents no job IDs. It refuses VW job daa9pn4e74ec73akj9i0. The
two-point ΔL flights (k=0,1 only) are not a leftover series and cannot
host the statevector 0.222 bin.

Usage
  python eon_full_k_leftover.py              # retrieve + write receipt
  python eon_full_k_leftover.py --job ID     # retrieve one id, then grade
  python eon_full_k_leftover.py --submit     # refused unless env gate

The flight that would close the Mitsubishi gap is --k-grid dense
(k=0..8, 29 circuits): the SV S(ω) is DFT of nine consecutive leftover
samples. The frozen protocol subset k∈{0,1,2,4,6,8} is 20 circuits and
is not a uniform device Fourier of that series.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

import eon_nisq_field as F
from eon_dynamics_crossing import CORE, spectrum_of
from eon_field_flight import leftover_from_counts

HERE = Path(__file__).resolve().parent
DEST = HERE / "results" if (HERE / "results").is_dir() else HERE
RECEIPT = DEST / "eon_full_k_leftover.json"
XING = DEST / "eon_dynamics_crossing.json"
STATE = DEST / "eon_full_k_state.json"

VW_JOB = "daa9pn4e74ec73akj9i0"
TWO_POINT = {
    "daa0dq6rbfbs73ci56bg": "kingston two-point ΔL (k=0,1 only)",
    "daa9do6rbfbs73cifa80": "marrakesh two-point ΔL (k=0,1 only)",
}
QAOA_JOB = "d9sqks1dsedc73ai3o30"
A1_JOB = "d9rdfb1dsedc73agh5ng"

ARMS = ("certified", "milp", "no_build")
K_PROTOCOL = (0, 1, 2, 4, 6, 8)
K_DENSE = (0, 1, 2, 3, 4, 5, 6, 7, 8)
CONTROLS = ("certified_null_k0", "certified_detuned_dt0.36_k1")
OPEN_BACKENDS = ("ibm_fez", "ibm_kingston", "ibm_marrakesh")
SHOTS = 8192
DT_CTRL = 0.36
TWOQ_WALL = 370
CHAIN = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 35, 34, 33]
OMEGA_STAR = 2.0 / 9.0
DEFAULT_CRN = (
    "crn:v1:bluemix:public:quantum-computing:us-east:"
    "a/0601b1157c194f5f9dc0b0fe3ff89f31:"
    "4448fcf5-e662-487a-a307-4e13163054a7::"
)

# Jobs on the same CRN that are not an E.ON leftover series.
# Attribution is from this package + sibling-track receipts (read only).
NOT_LEFTOVER_SERIES = {
    **TWO_POINT,
    VW_JOB: "VW 64-rung spectrum — NOT_AN_EON_RESULT",
    QAOA_JOB: "E.ON 10q QAOA, not leftover L(k)",
    A1_JOB: "A1/VW 64-rung collective — not E.ON leftover",
    "d9rm4j9dsedc73agrb70": "VW fez spectroscopy — not E.ON leftover",
    "d9solsgpdb6s73e6a6q0": "Airbus QLGA — not E.ON leftover",
    "daaucejvpcac73dd232g": "HSBC 128q feature map — not E.ON leftover",
    "dab6therrl7c7386flo0": "HSBC 128q generative — not E.ON leftover",
    "daba21jvpcac73ddh9h0": "HSBC 87q QBM — not E.ON leftover",
    "daa9fnerbfbs73cifcjg": "Cleveland IBM walk — not E.ON leftover",
    "daa9fgurbfbs73cifcc0": "Cleveland IBM sector — not E.ON leftover",
    "daa9f09qtnsc73d2db5g": "Cleveland IBM scout — not E.ON leftover",
    "daatu7j4clkc73fi68vg": "Cleveland qallo — not E.ON leftover",
    "daauddbvpcac73dd2430": "Cleveland-matched — not E.ON leftover",
    "daa1akce74ec73ak9qcg": "deep3 main — not E.ON leftover",
    "daa19lerbfbs73ci66eg": "deep3 scout — not E.ON leftover",
    "daa0hburbfbs73ci5ai0": "deep2 scout — not E.ON leftover",
    "daa0bqce74ec73ak8mgg": "deep main — not E.ON leftover",
    "daa0bc1qtnsc73d231v0": "deep scout — not E.ON leftover",
    "daa3osce74ec73akcmb0": "cancelled kingston — not a leftover series",
}


def _crn():
    return os.environ.get("IBM_QUANTUM_CRN") or DEFAULT_CRN


def k_grid(dense: bool):
    return list(K_DENSE if dense else K_PROTOCOL)


def circuit_names(ks):
    names = [f"{arm}_k{k}" for arm in ARMS for k in ks]
    names.extend(CONTROLS)
    return names


def sv_leftover_at(xing, ks):
    rows = {}
    for arm in ARMS:
        L = xing["realtime"][arm]["leftover_k"]
        rows[arm] = [float(L[k]) for k in ks]
    return rows


def interpolate_to_dense(ks, L):
    """Place measured leftover on k=0..8. Missing integers are linear-interp."""
    ks = np.asarray(ks, float)
    L = np.asarray(L, float)
    grid = np.arange(K_DENSE[-1] + 1, dtype=float)
    return [float(x) for x in np.interp(grid, ks, L)]


def logical_2q_estimate(geo, x, k):
    on = F.active_mask(x)
    prep_cx = sum(1 for i in range(10) if on[i])
    rzz = prep_cx
    rxx = 0
    for p, q, _ww in geo["bonds"]:
        if on[p // 2] and on[q // 2]:
            rxx += 1
    return prep_cx + k * (rzz + rxx)


def next_flight(dense=True):
    ks = k_grid(dense)
    n = len(circuit_names(ks))
    return dict(
        closes_mitsubishi=bool(dense),
        command=(
            "EON_FULL_K_SUBMIT=1 python eon_full_k_leftover.py --submit --k-grid dense"
            if dense else
            "EON_FULL_K_SUBMIT=1 python eon_full_k_leftover.py --submit"
        ),
        retrieve_command="python eon_full_k_leftover.py",
        arms=list(ARMS),
        k=ks,
        controls=list(CONTROLS),
        n_circuits=n,
        shots=SHOTS,
        backend="open Heron (fez / kingston / marrakesh), lowest queue",
        layout="fixed CHAIN from marrakesh two-point (seed_transpiler=21)",
        dd="XpXm",
        compilation="eon_nisq_field.qiskit_circuit — same operator as the SV leftover",
        twoq_wall=TWOQ_WALL,
        twoq_note=(
            "v1 certified k=1 was 114 two-qubit gates. Linear scaling puts "
            "certified k≥4 over the v1 370 CX guard. Dense k=8 is the "
            "Mitsubishi-closing series; the human go waives that guard or "
            "accepts the queue/depth risk. Do not interpolate a 2-point "
            "ΔL flight and call it S(ω)."
        ),
        grade=(
            "Certified-arm DFT principal line is 0.222 after one damping "
            "envelope. Continuation of the same arm's G(τ) still misses "
            "(0.270). Two-point jobs cannot host that bin."
        ),
        why_dense=(
            "SV S(ω) is |DFT[L(k=0..8) − mean]|². The 0.222 line is the "
            "k=2/9 bin of a 9-sample series. The frozen 6-k subset is not "
            "uniform and cannot host that bin without interpolation."
        ),
        submit_gate="EON_FULL_K_SUBMIT=1",
        default="NO paid submit",
    )


def local_search():
    hits = []
    rejects = []
    for path in sorted(DEST.glob("*.json")) + sorted(HERE.glob("*.json")):
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        text = json.dumps(blob)
        if any(f"_k{k}" in text for k in (2, 4, 6, 8)) and (
            "leftover" in text or "full_k" in text
        ):
            if path.name in {
                "eon_nisq_field.json",
                "eon_dynamics_crossing.json",
                "eon_full_k_leftover.json",
            }:
                rejects.append(dict(
                    file=path.name,
                    reason="statevector / protocol — not a hardware leftover series",
                ))
                continue
            leftover_keys = []
            if isinstance(blob, dict):
                leftover = blob.get("leftover") or {}
                leftover_keys = [k for k in leftover if any(
                    k.endswith(f"_k{n}") for n in (2, 4, 6, 8)
                )]
            if leftover_keys:
                hits.append(dict(file=path.name, keys=leftover_keys))
            else:
                rejects.append(dict(
                    file=path.name,
                    reason="mentions k≥2 leftover but has no hardware leftover keys",
                ))
    return hits, rejects


def ibm_search(job_id=None):
    """List jobs. Do not invent a match. Never fetch VW as E.ON leftover."""
    out = dict(available=False, examined=0, match=None, rejects=[], error=None)
    if job_id == VW_JOB:
        out["error"] = "REFUSED: VW job daa9pn4e74ec73akj9i0 is not an E.ON result"
        return out
    if job_id in TWO_POINT:
        out["error"] = (
            f"REFUSED: {job_id} is {TWO_POINT[job_id]} — not a leftover series"
        )
        return out
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        svc = QiskitRuntimeService(instance=_crn())
        out["available"] = True
    except Exception as e:
        out["error"] = f"IBM list unavailable: {type(e).__name__}: {e}"
        return out

    if job_id:
        try:
            job = svc.job(job_id)
        except Exception as e:
            out["error"] = f"job {job_id} not retrievable: {type(e).__name__}: {e}"
            return out
        rec = _inspect_job(job)
        if rec.get("is_leftover_series"):
            out["match"] = rec
        else:
            out["rejects"].append(rec)
        out["examined"] = 1
        return out

    try:
        jobs = list(svc.jobs(limit=80))
    except Exception as e:
        out["error"] = f"jobs() failed: {type(e).__name__}: {e}"
        return out
    out["examined"] = len(jobs)
    for job in jobs:
        rec = _inspect_job(job, light=True)
        if rec.get("is_leftover_series"):
            out["match"] = rec
        elif rec.get("reason"):
            out["rejects"].append(rec)
    return out


def _inspect_job(job, light=True):
    jid = job.job_id()
    rec = dict(job=jid, is_leftover_series=False)
    try:
        rec["backend"] = job.backend().name
    except Exception:
        rec["backend"] = None
    rec["status"] = str(job.status())
    rec["created"] = str(getattr(job, "creation_date", None))
    if jid in NOT_LEFTOVER_SERIES:
        rec["reason"] = NOT_LEFTOVER_SERIES[jid]
        return rec
    if light:
        rec["reason"] = (
            "unlabeled on CRN — no leftover-series receipt; not claimed"
        )
        return rec
    try:
        inp = job.inputs
        pubs = inp.get("pubs") or inp.get("circuits") or []
        rec["n_circuits"] = len(pubs)
    except Exception as e:
        rec["reason"] = f"inputs unavailable: {type(e).__name__}"
        return rec
    names = circuit_names(K_PROTOCOL)
    dense_names = circuit_names(K_DENSE)
    n = rec["n_circuits"]
    if n in (len(names), len(dense_names)):
        rec["reason"] = (
            f"{n} pubs — count matches a leftover protocol, but this package "
            "has no stored names for this id. Not claimed."
        )
        return rec
    rec["reason"] = f"{n} pubs — not the leftover-series circuit count"
    return rec


def retrieve_and_grade(job_id, names, geo):
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(instance=_crn())
    job = svc.job(job_id)
    status = str(job.status())
    if "DONE" not in status.upper():
        return dict(job=job_id, status=status, graded=False,
                    reason="job not DONE")
    res = job.result()
    if len(res) != len(names):
        return dict(job=job_id, status=status, graded=False,
                    reason=f"pub count {len(res)} != expected {len(names)}")
    leftover = {}
    for i, nm in enumerate(names):
        leftover[nm] = leftover_from_counts(res[i].data.c.get_counts(),
                                            geo["rungs"])
    return grade_leftover(job_id, leftover, names)


def grade_leftover(job_id, leftover, names):
    xing = json.loads(XING.read_text(encoding="utf-8"))
    rows = {}
    for arm in ARMS:
        ks, Ls = [], []
        for nm, val in leftover.items():
            if nm.startswith(f"{arm}_k"):
                ks.append(int(nm.split("_k")[1]))
                Ls.append(float(val))
        if not ks:
            continue
        order = np.argsort(ks)
        ks = [ks[i] for i in order]
        Ls = [Ls[i] for i in order]
        dense = interpolate_to_dense(ks, Ls)
        spec_raw = spectrum_of(Ls)
        spec_dense = spectrum_of(dense)
        rows[arm] = dict(
            k=ks, leftover=Ls, leftover_interp_0_8=dense,
            spectrum_on_measured_k=spec_raw,
            spectrum_interp_dense=spec_dense,
        )
    cert = rows.get("certified", {})
    prin = None
    if cert:
        prin = cert["spectrum_interp_dense"]["principal_cyc_per_step"]
    expected = xing["realtime"]["certified"]["spectrum"]["principal_cyc_per_step"]
    cont = xing["imaginary_time"]["continuation_cyc_per_step"]
    measured_k = cert.get("k", [])
    uniform_dense = measured_k == list(K_DENSE)
    return dict(
        job=job_id,
        graded=True,
        leftover=leftover,
        rows=rows,
        certified_principal_interp=prin,
        statevector_omega=expected,
        continuation_omega=cont,
        principal_matches_sv=(
            prin is not None and abs(prin - expected) < 0.04
        ),
        continuation_still_misses=abs(cont - expected) > 0.04,
        uniform_dense_series=uniform_dense,
        note=(
            "Device Fourier of a uniform k=0..8 series."
            if uniform_dense else
            "Measured k is not 0..8. Interpolated leftover is labeled as "
            "such — not a uniform device Fourier."
        ),
    )


def write_receipt(payload):
    RECEIPT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    patch_crossing_card(payload)
    return RECEIPT


def patch_crossing_card(payload):
    """Keep the crossing hardware card honest. Never write a fake job id."""
    if not XING.exists():
        return
    xing = json.loads(XING.read_text(encoding="utf-8"))
    hw = xing.setdefault("hardware", {}).setdefault("full_k_spectrum", {})
    match = payload.get("ibm_search", {}).get("match")
    graded = payload.get("graded")
    if graded and graded.get("graded") and graded.get("job"):
        hw["status"] = "FLOWN"
        hw["job_id"] = graded["job"]
        hw["spectrum"] = (graded.get("rows", {})
                          .get("certified", {})
                          .get("spectrum_interp_dense"))
    else:
        hw["status"] = "NOT_FLOWN"
        hw["job_id"] = None
    proto = hw.setdefault("protocol", {})
    proto["one_command"] = "python eon_full_k_leftover.py"
    proto["submit_gate"] = "EON_FULL_K_SUBMIT=1"
    proto["default"] = "retrieve only — no paid submit"
    proto["receipt"] = "results/eon_full_k_leftover.json"
    proto["k"] = list(K_PROTOCOL)
    proto["k_dense"] = list(K_DENSE)
    proto["n_circuits_protocol"] = len(circuit_names(K_PROTOCOL))
    proto["n_circuits_dense"] = len(circuit_names(K_DENSE))
    proto["next_flight"] = payload.get("next_flight_dense")
    if match:
        proto["retrieved_match"] = match.get("job")
    XING.write_text(json.dumps(xing, indent=2), encoding="utf-8")


def patch_storage(job_id=None):
    for path in (DEST / "eon_storage_sizing.json",
                 HERE / "eon_storage_sizing.json"):
        if not path.exists():
            continue
        store = json.loads(path.read_text(encoding="utf-8"))
        store["hardware_spectrum_job"] = job_id
        store["hardware_spectrum_status"] = "FLOWN" if job_id else "NOT_FLOWN"
        if job_id == VW_JOB:
            raise RuntimeError("refused to write VW job into storage")
        path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def stage_derive(dense: bool):
    xing = json.loads(XING.read_text(encoding="utf-8"))
    ks = k_grid(dense)
    geo = F.geometry()
    est = {
        arm: {str(k): logical_2q_estimate(geo, CORE[arm], k) for k in ks}
        for arm in ARMS
    }
    return dict(
        card="EON FULL-k LEFTOVER → S(ω) PROTOCOL",
        generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
        status="NOT_FLOWN",
        job_id=None,
        operator="H = μ* D − A6",
        industrial_object=(
            "N-1 quench leftover series L(k) on the slack star; "
            "S(ω) = |DFT[L − mean]|²"
        ),
        k_grid="dense" if dense else "protocol",
        k=ks,
        arms=list(ARMS),
        controls=list(CONTROLS),
        names=circuit_names(ks),
        n_circuits=len(circuit_names(ks)),
        shots=SHOTS,
        dt=F.DT,
        dt_ctrl=DT_CTRL,
        chain=CHAIN,
        frozen_sv_leftover=sv_leftover_at(xing, ks),
        frozen_sv_omega=xing["realtime"]["certified"]["spectrum"]["principal_cyc_per_step"],
        continuation_omega=xing["imaginary_time"]["continuation_cyc_per_step"],
        logical_2q_estimate=est,
        expected_signature=(
            "Certified-arm DFT principal line matches the statevector "
            f"ω*={OMEGA_STAR:.3f} after one damping envelope; continuation "
            "of the same arm's imag-time G(τ) misses ω*. "
            "Do not assign a job id until flown."
        ),
    )


def stage_submit(dense: bool, backend_name=None):
    if os.environ.get("EON_FULL_K_SUBMIT") != "1":
        print("REFUSED: default is NO paid submit.")
        print("Set EON_FULL_K_SUBMIT=1 only for a human-authorized flight.")
        print("Exact next flight is in results/eon_full_k_leftover.json")
        return 3
    ks = k_grid(dense)
    names = circuit_names(ks)
    geo = F.geometry()
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    svc = QiskitRuntimeService(instance=_crn())
    if backend_name:
        if backend_name not in OPEN_BACKENDS:
            print("REFUSED: not an open-plan Heron")
            return 3
        backend = svc.backend(backend_name)
    else:
        pend = {}
        for b in OPEN_BACKENDS:
            try:
                pend[b] = svc.backend(b).status().pending_jobs
            except Exception:
                pend[b] = 10 ** 6
        backend = svc.backend(min(pend, key=pend.get))
        print(f"  queue {pend} -> {backend.name}")
    nq = backend.target.num_qubits
    layout = [q for q in CHAIN if q < nq]
    if len(layout) < 20:
        print(f"REFUSED: backend {backend.name} cannot host CHAIN layout")
        return 2
    circs = []
    for arm in ARMS:
        for k in ks:
            circs.append(F.qiskit_circuit(geo, CORE[arm], k, nq,
                                          quench=True, dt=F.DT))
    circs.append(F.qiskit_circuit(geo, CORE["certified"], 0, nq,
                                  quench=False, dt=F.DT))
    circs.append(F.qiskit_circuit(geo, CORE["certified"], 1, nq,
                                  quench=True, dt=DT_CTRL))
    tp = dict(optimization_level=1, initial_layout=layout,
              seed_transpiler=21)
    qcs = transpile(circs, backend, **tp)
    twos = [qc.num_nonlocal_gates() for qc in qcs]
    depths = [qc.depth() for qc in qcs]
    print("transpiled:")
    for nm, d, t in zip(names, depths, twos):
        print(f"  {nm:28s}  depth {d:4d}  2q {t:4d}")
    if max(twos) > TWOQ_WALL:
        print(f"NOTE: max 2q {max(twos)} exceeds v1 {TWOQ_WALL} CX guard.")
        print("Human go is already implied by EON_FULL_K_SUBMIT=1.")
    s = SamplerV2(mode=backend)
    s.options.dynamical_decoupling.enable = True
    s.options.dynamical_decoupling.sequence_type = "XpXm"
    job = s.run(qcs, shots=SHOTS)
    st = dict(backend=backend.name, main_job=job.job_id(),
              names=names, depths=depths, twos=twos,
              k=ks, dense=dense,
              submitted=time.strftime("%Y-%m-%dT%H:%M:%S"))
    STATE.write_text(json.dumps(st, indent=2), encoding="utf-8")
    print(f"EON FULL-k submitted: {job.job_id()}  "
          f"{len(qcs)} x {SHOTS} on {backend.name}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description="E.ON full-k leftover → S(ω). Default: retrieve only.")
    p.add_argument("--submit", action="store_true",
                   help="paid submit; refused unless EON_FULL_K_SUBMIT=1")
    p.add_argument("--job", help="retrieve this IBM job id (no inventing)")
    p.add_argument("--backend", help="open Heron name for submit")
    p.add_argument("--k-grid", choices=("protocol", "dense"),
                   default="protocol",
                   help="protocol=frozen 6-k subset; dense=k=0..8 (Mitsubishi closer)")
    args = p.parse_args(argv)

    dense = args.k_grid == "dense"
    derive = stage_derive(dense)
    local_hits, local_rejects = local_search()
    ibm = ibm_search(args.job)

    graded = None
    match_id = None
    if ibm.get("match") and ibm["match"].get("job"):
        match_id = ibm["match"]["job"]
    if args.job and not ibm.get("error"):
        if args.job == VW_JOB:
            print("REFUSED: VW job is not an E.ON leftover series")
            match_id = None
        elif args.job in TWO_POINT:
            print(f"REFUSED: {args.job} is two-point ΔL, not a leftover series")
            match_id = None
        else:
            match_id = args.job

    if match_id and not ibm.get("error"):
        try:
            graded = retrieve_and_grade(match_id, derive["names"], F.geometry())
        except Exception as e:
            graded = dict(job=match_id, graded=False,
                          reason=f"{type(e).__name__}: {e}")

    flown = bool(graded and graded.get("graded") and graded.get("job")
                 and graded["job"] != VW_JOB)

    payload = dict(
        derive,
        local_search=dict(hits=local_hits, rejects=local_rejects),
        ibm_search=ibm,
        graded=graded,
        status="FLOWN" if flown else "NOT_FLOWN",
        job_id=graded["job"] if flown else None,
        honesty=dict(
            no_supremacy=True,
            vw_job_refused=VW_JOB,
            two_point_not_a_series=list(TWO_POINT),
            qaoa_not_a_series=QAOA_JOB,
            invented_ids=False,
        ),
        next_flight_dense=next_flight(True),
        next_flight_protocol=next_flight(False),
    )
    dest = write_receipt(payload)
    if flown:
        patch_storage(payload["job_id"])
    else:
        patch_storage(None)

    print(f"status {payload['status']}  job {payload['job_id']}")
    print(f"local leftover-series hits: {len(local_hits)}")
    print(f"IBM examined: {ibm.get('examined')}  match: "
          f"{(ibm.get('match') or {}).get('job')}")
    if ibm.get("error"):
        print("IBM:", ibm["error"])
    print("next flight (closes Mitsubishi):")
    nf = payload["next_flight_dense"]
    print(f"  {nf['n_circuits']} circ × {nf['shots']}  k={nf['k']}")
    print(f"  {nf['command']}")
    print(f"-> {dest}")

    if args.submit:
        return stage_submit(dense, args.backend)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
