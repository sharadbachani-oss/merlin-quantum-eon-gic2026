"""
E.ON v4 evidence pack — the stronger-than-Mitsubishi advantage demo.

What this adds (all classical, credential-free, deterministic):
  1. Two-build ledger — splits the conflated 77.1→2.50 (MILP-objective plan)
     from the Dirac-certified plan's own referee (1.44 / 7 / 137).
  2. Hidden-congestion audit — DC-clean plans that still fail voltage-true
     (the QCi $786M template, on this distribution instance).
  3. Held-out robustness — Dirac / MILP / deg-2 / no-build graded on
     scenarios the optimizer never saw.
  4. Schmidt scaling of the TRUE objective at n = 6 and n = 10, plus the
     deg-2 shadow — the representation wall as a measured law, not a point.
  5. Frozen 100-qubit utility-QAOA design card (not flown) — the A1-standard
     next flight, dual-outcome texts written before any shot.

Run: py -3 eon_v4_advantage.py
"""
from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

import numpy as np

import eon_core as E

_HERE = Path(__file__).resolve().parent
WORK = _HERE / "results" if (_HERE / "results").is_dir() else _HERE
LAM = 50.0


def instance_eon14_hard():
    lines, n = E.CASE14_LINES, E.CASE14_N
    p = E.CASE14_P * 1.35
    cands = E.candidates(lines, n, 10, seed=10)
    scens = E.scenarios_set(p, 4, seed=4)
    costs = [1.0 + 0.13 * i for i in range(10)]
    return lines, n, cands, scens, costs


def instance_eon14_easy():
    # Matches eon_ladder.py: k=6, m=2, seed=k / seed=m, no N-1.
    lines, n = E.CASE14_LINES, E.CASE14_N
    p = E.CASE14_P * 1.35
    cands = E.candidates(lines, n, 6, seed=6)
    scens = E.scenarios_set(p, 2, seed=2)
    costs = [1.0 + 0.13 * i for i in range(6)]
    return lines, n, cands, scens, costs


def exact_table(lines, n, cands, scens, costs, nminus1, vcheck):
    nb = len(cands)
    X = np.array(list(itertools.product([0, 1], repeat=nb)), dtype=int)
    y = np.zeros(len(X))
    cong = np.zeros(len(X))
    ovl = np.zeros(len(X), dtype=int)
    vv = np.zeros(len(X), dtype=int)
    for i, x in enumerate(X):
        m = E.referee(lines, cands, x.tolist(), scens, n,
                      nminus1=nminus1, vcheck=vcheck)
        y[i] = float(np.dot(costs, x)) + LAM * m["congestion"]
        cong[i] = m["congestion"]
        ovl[i] = m["overloads"]
        vv[i] = m["vviol"]
    return X, y, cong, ovl, vv


def schmidt_profile(y, n_bits, tol=1e-8):
    ranks = []
    for cut in range(1, n_bits):
        A = y.reshape(2 ** cut, 2 ** (n_bits - cut))
        s = np.linalg.svd(A, compute_uv=False)
        ranks.append(int(np.sum(s > tol)))
    return ranks


def poly_residuals(X, y, max_deg=5):
    out = {}
    for deg in range(2, max_deg + 1):
        cols = [np.ones(len(X))]
        for d in range(1, deg + 1):
            for comb in itertools.combinations(range(X.shape[1]), d):
                cols.append(np.prod(X[:, list(comb)], axis=1).astype(float))
        F = np.array(cols).T
        beta, *_ = np.linalg.lstsq(F, y, rcond=None)
        out[str(deg)] = float(np.max(np.abs(F @ beta - y)))
    return out


def deg2_argmin(X, y):
    cols = [np.ones(len(X))]
    nb = X.shape[1]
    for e in range(nb):
        cols.append(X[:, e].astype(float))
    for e in range(nb):
        for f in range(e + 1, nb):
            cols.append((X[:, e] * X[:, f]).astype(float))
    F = np.array(cols).T
    beta, *_ = np.linalg.lstsq(F, y, rcond=None)
    yhat = F @ beta
    i = int(np.argmin(yhat))
    return X[i].tolist(), float(y[i]), float(yhat[i])


def two_build_ledger(lines, n, cands, scens, costs, X, y, cong, ovl, vv):
    dirac = [1, 0, 1, 1, 0, 1, 0, 1, 1, 1]
    milp = [1, 0, 0, 0, 0, 0, 0, 1, 1, 1]
    deg2_x, deg2_true, deg2_hat = deg2_argmin(X, y)
    nobuild = [0] * 10

    def row(name, x):
        i = int(np.argmax(np.all(X == np.array(x), axis=1)))
        return dict(
            name=name, plan=x,
            objective=float(y[i]),
            congestion=float(cong[i]),
            overloads=int(ovl[i]),
            vviol=int(vv[i]),
            capex=float(np.dot(costs, x)),
        )

    rows = [
        row("no_build", nobuild),
        row("milp_disjunctive", milp),
        row("dirac_certified", dirac),
        row("deg2_surrogate", deg2_x),
    ]
    return dict(
        note=(
            "Two different builds of eon14_hard. The 77.1→2.50 / 227→19 "
            "numbers grade the MILP-objective plan under the physics referee. "
            "The Dirac-certified plan's own referee is congestion 1.44 / "
            "7 overloads / 137 vviol. Both receipts are internally consistent; "
            "they must never be spliced into one sentence."
        ),
        dirac_is_exact_argmin=bool(dirac == X[int(np.argmin(y))].tolist()),
        deg2_true_objective=deg2_true,
        deg2_surrogate_value=deg2_hat,
        rows=rows,
    )


def hidden_congestion(X, y, cong, ovl, vv, costs):
    """Plans that look clean on DC congestion but fail the voltage channel."""
    i_star = int(np.argmin(y))
    cong_star = float(cong[i_star])
    # DC-competitive: congestion within 3× of the certified plan
    dc_ok = cong <= max(3.0 * cong_star, 5.0)
    # voltage-dirty: more vviol than the certified plan
    v_bad = vv > vv[i_star]
    hidden = np.where(dc_ok & v_bad)[0]
    # also: Pareto-front of (congestion, vviol) — plans that improve DC
    # while making voltage worse than no-build
    nobuild = 0  # X[0] is all-zeros
    worse_v_better_dc = np.where((cong < cong[0]) & (vv > vv[0]))[0]
    return dict(
        n_plans=int(len(X)),
        certified_vviol=int(vv[i_star]),
        nobuild_vviol=int(vv[0]),
        n_dc_ok_voltage_dirty=int(len(hidden)),
        n_better_dc_worse_voltage=int(len(worse_v_better_dc)),
        certified_clears_voltage_vs_nobuild=bool(vv[i_star] < vv[0]),
        voltage_reduction_vs_nobuild=int(vv[0] - vv[i_star]),
        # cheapest DC-clean / voltage-dirty plan (the hidden-failure exemplar)
        exemplar=(
            None if len(hidden) == 0 else dict(
                plan=X[int(hidden[np.argmin(cong[hidden])])].tolist(),
                congestion=float(cong[hidden].min()),
                vviol=int(vv[int(hidden[np.argmin(cong[hidden])])]),
                objective=float(y[int(hidden[np.argmin(cong[hidden])])]),
            )
        ),
    )


def held_out(lines, n, cands, costs, plans, n_seeds=12, n_scen=4):
    """Grade named plans on scenario draws the optimizer never saw."""
    names = list(plans)
    acc = {k: dict(cong=[], ovl=[], vv=[]) for k in names}
    t0 = time.time()
    for seed in range(100, 100 + n_seeds):
        scens = E.scenarios_set(E.CASE14_P * 1.35, n_scen, seed=seed)
        for name, x in plans.items():
            m = E.referee(lines, cands, x, scens, n, nminus1=True, vcheck=True)
            acc[name]["cong"].append(m["congestion"])
            acc[name]["ovl"].append(m["overloads"])
            acc[name]["vv"].append(m["vviol"])
    summary = {}
    for name, d in acc.items():
        c = np.array(d["cong"])
        o = np.array(d["ovl"])
        v = np.array(d["vv"])
        summary[name] = dict(
            congestion_mean=float(c.mean()),
            congestion_std=float(c.std(ddof=1)),
            overloads_mean=float(o.mean()),
            vviol_mean=float(v.mean()),
            n_seeds=n_seeds,
        )
    d_c = summary["dirac_certified"]["congestion_mean"]
    m_c = summary["milp_disjunctive"]["congestion_mean"]
    g_c = summary["deg2_surrogate"]["congestion_mean"]
    n_c = summary["no_build"]["congestion_mean"]
    return dict(
        wall_s=float(time.time() - t0),
        seeds=list(range(100, 100 + n_seeds)),
        summary=summary,
        dirac_vs_milp_pct=float(100.0 * (m_c - d_c) / m_c) if m_c else 0.0,
        dirac_vs_deg2_pct=float(100.0 * (g_c - d_c) / g_c) if g_c else 0.0,
        dirac_vs_nobuild_pct=float(100.0 * (n_c - d_c) / n_c) if n_c else 0.0,
    )


def schmidt_scaling():
    """Representation wall at two certified sizes."""
    out = {}
    for name, inst, n1 in (
        ("eon14_easy_n6", instance_eon14_easy(), False),
        ("eon14_hard_n10", instance_eon14_hard(), True),
    ):
        lines, n, cands, scens, costs = inst
        nb = len(cands)
        X, y, *_ = exact_table(lines, n, cands, scens, costs, n1, False)
        ranks = schmidt_profile(y, nb)
        # deg-2 shadow
        cols = [np.ones(len(X))]
        for e in range(nb):
            cols.append(X[:, e].astype(float))
        for e in range(nb):
            for f in range(e + 1, nb):
                cols.append((X[:, e] * X[:, f]).astype(float))
        y2 = (np.array(cols).T @ np.linalg.lstsq(
            np.array(cols).T, y, rcond=None)[0])
        ranks2 = schmidt_profile(y2, nb)
        out[name] = dict(
            n_bits=nb,
            exact_ranks=ranks,
            exact_mid_rank=ranks[nb // 2 - 1],
            exact_mid_max=2 ** (nb // 2) if nb % 2 == 0 else 2 ** (nb // 2),
            deg2_ranks=ranks2,
            deg2_mid_rank=ranks2[nb // 2 - 1],
            saturates=bool(ranks[nb // 2 - 1] >= (2 ** (nb // 2) - 1)),
        )
    return out


def utility_design_card():
    """Frozen next-flight card: 100-qubit scenario-entangled QAOA.
    Dual-outcome texts written now, before any shot — A1 / QCi protocol.
    """
    # 20 candidates × 5 held-out scenario copies = 100 decision qubits.
    # Interaction graph = 5 replicas of the eon57_util candidate graph
    # plus all-to-all scenario-coupling on each candidate (the N-1
    # contingency makes every replica interact). Treewidth lower bound
    # = replica count = 5; chi >= 2^5 = 32 just from the copies, and
    # the meshed candidate graph pushes the per-replica tw higher.
    lines, p = E.synth_grid(57, seed=57)
    n = 57
    cands = E.candidates(lines, n, 20, seed=20)
    # candidate adjacency: two candidates share a vertex
    adj = {i: set() for i in range(20)}
    for i, (a, b, _, _) in enumerate(cands):
        for j, (c, d, _, _) in enumerate(cands):
            if i < j and len({a, b} & {c, d}) > 0:
                adj[i].add(j)
                adj[j].add(i)
    degrees = [len(adj[i]) for i in range(20)]
    n_scen = 5
    n_qubits = 20 * n_scen
    # crude tw lower bound: max degree of the scenario-entangled graph
    # each vertex connects to its replica-neighbours (deg) plus n_scen-1
    # copies of itself.
    max_deg = max(degrees) + (n_scen - 1)
    return dict(
        card="EON_UTILITY_QAOA_100Q — FROZEN DESIGN, NOT FLOWN",
        n_qubits=n_qubits,
        n_candidates=20,
        n_scenario_replicas=n_scen,
        candidate_max_degree=int(max(degrees)),
        entangled_max_degree=int(max_deg),
        chi_lower_bound_replicas=int(2 ** n_scen),
        statevector_dim=2 ** n_qubits,
        statevector_impossible=True,
        prereg_pass=(
            "If hardware sampled-best (physics referee) is strictly below "
            "every affordable-chi MPS sampled-best of the SAME circuit, "
            "the rubric's advantage evidence is adjudicated."
        ),
        prereg_tie=(
            "If any chi ties, that chi is the published classical price. "
            "No advantage headline. The representation column (degree-5 "
            "Dirac, Schmidt wall) still stands independently."
        ),
        status="design frozen 2026-08-30; hardware not submitted",
    )


def main():
    t0 = time.time()
    lines, n, cands, scens, costs = instance_eon14_hard()
    print("rebuilding eon14_hard exact table (vcheck on)…", flush=True)
    X, y, cong, ovl, vv = exact_table(
        lines, n, cands, scens, costs, True, True
    )
    i_star = int(np.argmin(y))
    print(f"  min {y.min():.6f} at {X[i_star].tolist()}  "
          f"cong {cong[i_star]:.4f} ovl {ovl[i_star]} vv {vv[i_star]}",
          flush=True)

    two = two_build_ledger(lines, n, cands, scens, costs, X, y, cong, ovl, vv)
    print("two-build ledger:", flush=True)
    for r in two["rows"]:
        print(f"  {r['name']:20s} obj {r['objective']:8.3f}  "
              f"cong {r['congestion']:7.3f}  ovl {r['overloads']:4d}  "
              f"vv {r['vviol']:4d}  capex {r['capex']:.3f}", flush=True)

    hidden = hidden_congestion(X, y, cong, ovl, vv, costs)
    print(f"hidden congestion: {hidden['n_better_dc_worse_voltage']} plans "
          f"improve DC while worsening voltage; certified clears "
          f"{hidden['voltage_reduction_vs_nobuild']} vviol vs no-build",
          flush=True)

    plans = {r["name"]: r["plan"] for r in two["rows"]}
    print("held-out robustness (12 unseen scenario seeds)…", flush=True)
    ho = held_out(lines, n, cands, costs, plans)
    for name, s in ho["summary"].items():
        print(f"  {name:20s} cong {s['congestion_mean']:.3f}±"
              f"{s['congestion_std']:.3f}  ovl {s['overloads_mean']:.1f}  "
              f"vv {s['vviol_mean']:.1f}", flush=True)
    print(f"  Dirac vs MILP {ho['dirac_vs_milp_pct']:+.1f}%  "
          f"vs deg-2 {ho['dirac_vs_deg2_pct']:+.1f}%  "
          f"vs no-build {ho['dirac_vs_nobuild_pct']:+.1f}%", flush=True)

    print("Schmidt scaling…", flush=True)
    sch = schmidt_scaling()
    for name, d in sch.items():
        print(f"  {name}: exact mid {d['exact_mid_rank']}/{d['exact_mid_max']} "
              f"deg2 mid {d['deg2_mid_rank']} saturates={d['saturates']}",
              flush=True)

    util = utility_design_card()
    resid = poly_residuals(X, y)

    out = dict(
        card="EON v4 ADVANTAGE EVIDENCE",
        generated="2026-08-30",
        wall_s=float(time.time() - t0),
        two_build=two,
        hidden_congestion=hidden,
        held_out=ho,
        schmidt_scaling=sch,
        poly_residuals=resid,
        utility_qaoa_100q=util,
        hardware_receipts=dict(
            dirac_native="6a79a72508442f441bbb5e56",
            dirac_deg2="6a79a74e08442f441bbb5e57",
            qaoa_marrakesh="d9sqks1dsedc73ai3o30",
        ),
        claim_class=(
            "representation-advantage + certified-optimum + three-rung "
            "trust ladder. NOT a 100q hardware-vs-MPS flight (that card "
            "is frozen, not flown). NOT an n=10 speed claim."
        ),
    )
    dest = WORK / "eon_v4_advantage.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2))
    print(f"-> {dest}  ({time.time() - t0:.1f}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
