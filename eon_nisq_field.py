"""
E.ON NISQ algorithm — the framework operator on the grid.

Lattice
  10 candidates = 10 rungs = 20 qubits.
  Rungs 7,8,9 are parallel re-rates of existing slack corridors
  (0–1, 0–4, 1–2). They are always in H — the grid is already there.
  Rungs 0–6 are distance-2 closures. They enter H only when built.

Operator (exact compilation, same as A1)
  Prep: RY(θ*)–CNOT–H⊗H on every active rung. θ* = π/2 − 2χ, χ = atan(δ/2).
  Step: RZZ(−μ* dt · w) on active rungs, RX(−2 dt) on their qubits,
        RXX on electrically neighbouring active pairs (residual A6).
  N−1: X-quench on the slack corridor (rung 7, bus 0–1).

Score
  Slack-star leftover at each k:
      L(k) = rms_{i in {7,8,9}} (C* − ⟨ZZ⟩_i)
  The congestion field is that series. A better build absorbs the
  quench off the existing slack star.

Not a QUBO. Builds are Hamiltonian support, not cost-layer bits.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

import eon_core as E
from eon_v4_advantage import instance_eon14_hard

WORK = Path(r"C:\quantum ai 2026\eon")
MU = 3.0 / (3.0 - math.sqrt(5.0))
DT = 0.30
K_MAX = 8
CHI = math.atan((math.sqrt((MU / 2) ** 2 + 4) - MU / 2) / 2)
THETA_STAR = math.pi / 2 - 2 * CHI
C_STAR = 0.7005699377
EXISTING = (7, 8, 9)           # already-on-the-grid re-rate corridors
QUENCH_RUNG = 7
CLOSURES = tuple(range(7))


def bus_dist(n, lines):
    adj = {i: set() for i in range(n)}
    for a, b, _, _ in lines:
        adj[a].add(b)
        adj[b].add(a)
    dist = np.full((n, n), 99, int)
    for s in range(n):
        dist[s, s] = 0
        q = [s]
        for u in q:
            for v in adj[u]:
                if dist[s, v] > dist[s, u] + 1:
                    dist[s, v] = dist[s, u] + 1
                    q.append(v)
    return dist


def geometry():
    lines, n, cands, scens, costs = instance_eon14_hard()
    rungs = [(2 * i, 2 * i + 1) for i in range(len(cands))]
    d = bus_dist(n, lines)
    bonds = []
    for i, (a, b, x, _) in enumerate(cands):
        for j in range(i + 1, len(cands)):
            c, e, x2, _ = cands[j]
            dmin = int(min(d[a, c], d[a, e], d[b, c], d[b, e]))
            if dmin <= 2:
                bonds.append((rungs[i][0], rungs[j][0],
                              (0.5 * (1.0 / x + 1.0 / x2)) / (1 + dmin)))
    w_rung = np.array([1.0 / c[2] for c in cands])
    w_rung = w_rung / w_rung.mean()
    return dict(lines=lines, n=n, cands=cands, scens=scens, costs=costs,
                rungs=rungs, bonds=bonds, w_rung=w_rung, nq=2 * len(cands))


def apply_1q(psi, nq, q, u2):
    psi = psi.reshape((2,) * nq)
    psi = np.moveaxis(psi, q, 0).reshape(2, -1)
    psi = u2 @ psi
    return np.moveaxis(psi.reshape((2,) + (2,) * (nq - 1)), 0, q).ravel()


def apply_2q(psi, nq, a, b, u4):
    psi = psi.reshape((2,) * nq)
    psi = np.moveaxis(psi, (a, b), (0, 1)).reshape(4, -1)
    psi = u4 @ psi
    return np.moveaxis(psi.reshape((2, 2) + (2,) * (nq - 2)), (0, 1), (a, b)).ravel()


def rx(th):
    c, s = math.cos(th / 2), math.sin(th / 2)
    return np.array([[c, -1j * s], [-1j * s, c]], complex)


def rzz(th):
    e = np.exp(-1j * th / 2)
    return np.diag([e, e.conjugate(), e.conjugate(), e]).astype(complex)


def rxx(th):
    h = np.array([[1, 1], [1, -1]], complex) / math.sqrt(2)
    hh = np.kron(h, h)
    return hh @ rzz(th) @ hh


def ry(th):
    c, s = math.cos(th / 2), math.sin(th / 2)
    return np.array([[c, -s], [s, c]], complex)


def hgate():
    return np.array([[1, 1], [1, -1]], complex) / math.sqrt(2)


def cnot():
    return np.array([[1, 0, 0, 0], [0, 1, 0, 0],
                     [0, 0, 0, 1], [0, 0, 1, 0]], complex)


def active_mask(x):
    on = [False] * len(x)
    for i in EXISTING:
        on[i] = True
    for i in CLOSURES:
        on[i] = bool(x[i])
    return on


def prepare(nq, rungs, on):
    psi = np.zeros(1 << nq, complex)
    psi[0] = 1.0
    u_ry, u_h, u_cx = ry(THETA_STAR), hgate(), cnot()
    for i, (a, b) in enumerate(rungs):
        if not on[i]:
            continue
        psi = apply_1q(psi, nq, a, u_ry)
        psi = apply_2q(psi, nq, a, b, u_cx)
        psi = apply_1q(psi, nq, a, u_h)
        psi = apply_1q(psi, nq, b, u_h)
    return psi


def evolve_series(psi, nq, rungs, bonds, w_rung, on, k_max, dt=DT):
    u_rx = rx(-2.0 * dt)
    u_rzz = {}
    for i, (a, b) in enumerate(rungs):
        if on[i]:
            u_rzz[i] = (a, b, rzz(-MU * dt * float(w_rung[i])))
    u_rxx = []
    for p, q, w in bonds:
        ri, rj = p // 2, q // 2
        if on[ri] and on[rj]:
            u_rxx.append((p, q, rxx(2.0 * dt * w / 4.0)))
    series = [rung_zz(psi, nq, rungs)]
    for _ in range(k_max):
        for a, b, u in u_rzz.values():
            psi = apply_2q(psi, nq, a, b, u)
        for i, (a, b) in enumerate(rungs):
            if on[i]:
                psi = apply_1q(psi, nq, a, u_rx)
                psi = apply_1q(psi, nq, b, u_rx)
        for p, q, u in u_rxx:
            psi = apply_2q(psi, nq, p, q, u)
        series.append(rung_zz(psi, nq, rungs))
    return series


def quench(psi, nq, q):
    return apply_1q(psi, nq, q, np.array([[0, 1], [1, 0]], complex))


def zz_expect(psi, nq, a, b):
    p = (psi.conj() * psi).real
    idx = np.arange(p.size)
    za = 1 - 2 * ((idx >> (nq - 1 - a)) & 1)
    zb = 1 - 2 * ((idx >> (nq - 1 - b)) & 1)
    return float(np.dot(p, za * zb))


def rung_zz(psi, nq, rungs):
    return [zz_expect(psi, nq, a, b) for a, b in rungs]


def leftover_star(zzs):
    d = [C_STAR - zzs[i] for i in EXISTING]
    return float(np.sqrt(np.mean(np.square(d))))


def run_plan(geo, x, k_max=K_MAX):
    nq, rungs = geo["nq"], geo["rungs"]
    on = active_mask(x)
    psi = prepare(nq, rungs, on)
    psi = quench(psi, nq, rungs[QUENCH_RUNG][0])
    series = evolve_series(psi, nq, rungs, geo["bonds"], geo["w_rung"], on, k_max)
    L = [leftover_star(z) for z in series]
    return dict(leftover_k=L, leftover=L[k_max], rung_zz=series[k_max], on=on)


def referee_cong(geo, x):
    m = E.referee(geo["lines"], geo["cands"], x, geo["scens"], geo["n"],
                  nminus1=True, vcheck=False)
    return float(m["congestion"])


def qiskit_circuit(geo, x, k, nq_chip, quench=True, dt=DT):
    """Same operator, for Heron. Exact prep + optional quench + k Trotter steps."""
    from qiskit import QuantumCircuit
    rungs, bonds, w = geo["rungs"], geo["bonds"], geo["w_rung"]
    on = active_mask(x)
    qc = QuantumCircuit(nq_chip, nq_chip)
    for i, (a, b) in enumerate(rungs):
        if not on[i]:
            continue
        qc.ry(THETA_STAR, a)
        qc.cx(a, b)
        qc.h(a)
        qc.h(b)
    if quench:
        qc.x(rungs[QUENCH_RUNG][0])
    for _ in range(k):
        for i, (a, b) in enumerate(rungs):
            if on[i]:
                qc.rzz(-MU * dt * float(w[i]), a, b)
        for i, (a, b) in enumerate(rungs):
            if on[i]:
                qc.rx(-2.0 * dt, a)
                qc.rx(-2.0 * dt, b)
        for p, q, ww in bonds:
            if on[p // 2] and on[q // 2]:
                qc.rxx(2.0 * dt * ww / 4.0, p, q)
    for i, (a, b) in enumerate(rungs):
        if on[i]:
            qc.measure(a, a)
            qc.measure(b, b)
    return qc


def main():
    t0 = time.time()
    geo = geometry()
    named = {
        "no_build": [0] * 10,
        "milp": [1, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        "milp+2": [1, 0, 1, 0, 0, 0, 0, 1, 1, 1],
        "milp+3": [1, 0, 0, 1, 0, 0, 0, 1, 1, 1],
        "milp+5": [1, 0, 0, 0, 0, 1, 0, 1, 1, 1],
        "deg2_hw": [1, 0, 1, 1, 0, 0, 0, 1, 1, 1],
        "certified": [1, 0, 1, 1, 0, 1, 0, 1, 1, 1],
        "all_build": [1] * 10,
    }
    rows = []
    print(f"lattice {geo['nq']}q  {len(geo['bonds'])} electrical bonds  "
          f"k=0..{K_MAX}  existing rungs {EXISTING}", flush=True)
    print("named plans (k-resolved slack-star leftover)…", flush=True)
    for name, x in named.items():
        out = run_plan(geo, x)
        cg = referee_cong(geo, x)
        dL = out["leftover_k"][0] - out["leftover_k"][1]
        rows.append(dict(name=name, plan=x, congestion=cg,
                         dL01=dL, **out))
        series = " ".join(f"{v:.3f}" for v in out["leftover_k"])
        print(f"  {name:12s}  dL={dL:+.3f}  L[k]={series}  "
              f"cong {cg:.3f}", flush=True)

    for r in rows:
        r["leftover_int"] = float(np.mean(r["leftover_k"][1:]))
    order_dL = [r["name"] for r in sorted(rows, key=lambda r: -r["dL01"])]
    order_L8 = [r["name"] for r in sorted(rows, key=lambda r: r["leftover"])]
    core = [r for r in rows if r["name"] in
            ("no_build", "milp", "deg2_hw", "certified")]
    core_dL = [r["name"] for r in sorted(core, key=lambda r: -r["dL01"])]
    core_cong = [r["name"] for r in sorted(core, key=lambda r: r["congestion"])]
    gate = core_dL == core_cong

    dest = WORK / "eon_nisq_field.json"
    payload = dict(
        card="EON NISQ FIELD v2 — existing slack star + gated closures",
        nq=geo["nq"],
        n_bonds=len(geo["bonds"]),
        mu=MU, dt=DT, k_max=K_MAX,
        theta_star=THETA_STAR, c_star=C_STAR,
        existing=list(EXISTING), quench_rung=QUENCH_RUNG,
        score="dL = L(0)-L(1)  initial slack-star absorption",
        named_order_dL=order_dL,
        named_order_L8=order_L8,
        core_order_dL=core_dL,
        core_order_cong=core_cong,
        model_gate_core_dL_matches_referee=gate,
        rows=rows,
        wall_s=float(time.time() - t0),
        algorithm=(
            "Exact prep on active rungs; existing slack corridors always "
            "on; closures enter H only when built; electrical-distance XX; "
            "N-1 X-quench on bus 0-1; score = slack-star leftover series."
        ),
    )
    dest.write_text(json.dumps(payload, indent=2))
    print(f"order by dL (high=better): {order_dL}")
    print(f"core dL vs referee: {core_dL} vs {core_cong}  "
          f"{'GATE PASS' if gate else 'GATE FAIL'}")
    print(f"-> {dest}  ({time.time()-t0:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
