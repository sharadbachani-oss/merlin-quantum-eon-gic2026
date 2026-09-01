"""
E.ON rubric closer — Outcome 3 (named line set) + Outcome 4
(MPS simulation of the TRUE objective gives poor objective value).

MPS method: TT-SVD compress the exact cost tensor to bond dimension chi,
then take the argmin of the compressed tensor and re-grade it on the
exact referee. That is the plan an MPS-truncated model of the instance
would return — the challenge's "MPS simulation gives poor objective value."

At chi >= mid-rank the compression is lossless (32 at n=10, 8 at n=6);
below that the returned plan is measurably worse. The degree-2 QUBO
shadow is the chi~7 special case every QUBO pipeline is stuck in.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from eon_v4_advantage import exact_table, instance_eon14_easy, instance_eon14_hard

WORK = Path(r"C:\quantum ai 2026\eon")


def tt_svd(y: np.ndarray, n_bits: int, chi: int):
    residual = y.reshape(2, -1)
    r_left = 1
    cores = []
    kept = []
    for _ in range(n_bits - 1):
        residual = residual.reshape(r_left * 2, -1)
        u, s, vt = np.linalg.svd(residual, full_matrices=False)
        r = min(int(chi), int(s.size))
        cores.append(u[:, :r].reshape(r_left, 2, r))
        residual = (s[:r, None] * vt[:r])
        kept.append(float(np.sum(s[:r] ** 2) / np.sum(s ** 2)))
        r_left = r
    cores.append(residual.reshape(r_left, 2, 1))
    return cores, kept


def tt_reconstruct(cores, n_bits: int) -> np.ndarray:
    acc = cores[0].reshape(2, cores[0].shape[-1])
    for k in range(1, n_bits):
        acc = np.tensordot(acc, cores[k], axes=([-1], [0]))
        acc = acc.reshape(-1, cores[k].shape[-1])
    return acc.reshape(-1)


def mps_argmin_sweep(y: np.ndarray, n_bits: int, chis):
    i_star = int(np.argmin(y))
    y_star = float(y[i_star])
    rows = []
    for chi in chis:
        cores, kept = tt_svd(y, n_bits, chi)
        yhat = tt_reconstruct(cores, n_bits)
        i_hat = int(np.argmin(yhat))
        true_of_hat = float(y[i_hat])
        rows.append(dict(
            chi=int(chi),
            recon_rel_energy=float(np.mean((yhat - y) ** 2) / np.mean(y ** 2)),
            last_kept_energy=float(kept[-1]) if kept else 1.0,
            plan=[int(b) for b in np.unravel_index(i_hat, (2,) * n_bits)],
            # unravel_index is MSB-first; our table is itertools product
            # which is also MSB-first for product([0,1], repeat=n). Good.
            true_objective=true_of_hat,
            gap=float(true_of_hat - y_star),
            gap_pct=float(100.0 * (true_of_hat - y_star) / abs(y_star)),
            matches_exact=bool(i_hat == i_star),
        ))
    return rows


def bits_of(i: int, n: int):
    return [int(b) for b in format(i, f"0{n}b")]


def line_set(cands, costs, plan):
    built = []
    for i, bit in enumerate(plan):
        if not bit:
            continue
        a, b, x, r = cands[i]
        built.append(dict(
            candidate=int(i),
            from_bus=int(a),
            to_bus=int(b),
            reactance_pu=float(x),
            rating_pu=float(r),
            capex=float(costs[i]),
        ))
    return built


def main():
    out = dict(card="EON RUBRIC — line set + MPS-on-true-objective")

    # --- n=10 certified instance ---
    lines, n, cands, scens, costs = instance_eon14_hard()
    X, y, cong, ovl, vv = exact_table(lines, n, cands, scens, costs, True, True)
    # exact_table uses itertools.product — index i <-> X[i]
    # TT reconstruct uses unravel_index which matches product order.
    i_star = int(np.argmin(y))
    plan = X[i_star].tolist()
    out["eon14_hard"] = dict(
        exact_min=float(y.min()),
        plan=plan,
        capex=float(np.dot(costs, plan)),
        congestion=float(cong[i_star]),
        overloads=int(ovl[i_star]),
        vviol=int(vv[i_star]),
        lines=line_set(cands, costs, plan),
        no_build=dict(
            congestion=float(cong[0]),
            overloads=int(ovl[0]),
            vviol=int(vv[0]),
        ),
        congestion_reduction=dict(
            thermal=float(cong[0] - cong[i_star]),
            thermal_pct=float(100.0 * (cong[0] - cong[i_star]) / cong[0]),
            overloads=int(ovl[0] - ovl[i_star]),
            vviol=int(vv[0] - vv[i_star]),
        ),
        mps_chi_sweep=mps_argmin_sweep(y, 10, (1, 2, 4, 8, 16, 32)),
    )

    # --- n=6 for the differing-variable-count MPS column ---
    lines6, n6, c6, s6, co6 = instance_eon14_easy()
    X6, y6, *_ = exact_table(lines6, n6, c6, s6, co6, False, False)
    out["eon14_easy"] = dict(
        exact_min=float(y6.min()),
        mps_chi_sweep=mps_argmin_sweep(y6, 6, (1, 2, 4, 8)),
    )

    dest = WORK / "eon_rubric_mps.json"
    dest.write_text(json.dumps(out, indent=2))
    print("eon14_hard certified lines:")
    for L in out["eon14_hard"]["lines"]:
        print(f"  cand {L['candidate']}: bus {L['from_bus']}–{L['to_bus']}  "
              f"x={L['reactance_pu']:.3f}  r={L['rating_pu']:.3f}  "
              f"capex={L['capex']:.3f}")
    print(f"  capex {out['eon14_hard']['capex']:.3f}  "
          f"cong {out['eon14_hard']['no_build']['congestion']:.3f} -> "
          f"{out['eon14_hard']['congestion']:.3f}  "
          f"({out['eon14_hard']['congestion_reduction']['thermal_pct']:.1f}%)")
    print("MPS chi sweep (true objective, n=10):")
    for r in out["eon14_hard"]["mps_chi_sweep"]:
        print(f"  chi={r['chi']:2d}  gap {r['gap']:+8.3f}  "
              f"({r['gap_pct']:+6.2f}%)  match={r['matches_exact']}  "
              f"plan {r['plan']}")
    print("MPS chi sweep (n=6):")
    for r in out["eon14_easy"]["mps_chi_sweep"]:
        print(f"  chi={r['chi']:2d}  gap {r['gap']:+8.3f}  "
              f"({r['gap_pct']:+6.2f}%)  match={r['matches_exact']}")
    print(f"-> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
