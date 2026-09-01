"""Credential-free audit of the E.ON v4 headline numbers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "eon"))

import eon_core as E
from eon_v4_advantage import (
    exact_table,
    instance_eon14_easy,
    instance_eon14_hard,
    poly_residuals,
    schmidt_profile,
    two_build_ledger,
)

FROZEN = json.loads((ROOT / "results" / "eon_v4_advantage.json").read_text())
tol = 1e-6
fails = []


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  {status}  {name} {detail}")
    if not ok:
        fails.append(name)


def main():
    print("E.ON v4 verify — rebuilding eon14_hard table…")
    lines, n, cands, scens, costs = instance_eon14_hard()
    X, y, cong, ovl, vv = exact_table(
        lines, n, cands, scens, costs, True, True
    )
    two = two_build_ledger(lines, n, cands, scens, costs, X, y, cong, ovl, vv)

    want = {r["name"]: r for r in FROZEN["two_build"]["rows"]}
    print("two-build")
    for r in two["rows"]:
        w = want[r["name"]]
        check(
            r["name"],
            abs(r["congestion"] - w["congestion"]) < 1e-9
            and r["overloads"] == w["overloads"]
            and r["vviol"] == w["vviol"],
            f"cong {r['congestion']:.4f} ovl {r['overloads']} vv {r['vviol']}",
        )
    check("dirac is exact argmin", two["dirac_is_exact_argmin"])

    print("residuals")
    resid = poly_residuals(X, y)
    for k, v in resid.items():
        check(f"deg {k}", abs(v - FROZEN["poly_residuals"][k]) < 1e-6, f"{v:.3f}")

    print("schmidt n=10")
    ranks = schmidt_profile(y, 10)
    check("saturates 32/32", ranks[4] == 32, str(ranks))

    print("schmidt n=6")
    lines6, n6, c6, s6, co6 = instance_eon14_easy()
    X6, y6, *_ = exact_table(lines6, n6, c6, s6, co6, False, False)
    r6 = schmidt_profile(y6, 6)
    check("saturates 8/8", r6[2] == 8, str(r6))

    rubric = json.loads((ROOT / "results" / "eon_rubric_mps.json").read_text())
    print("outcome 3 — line set")
    h = rubric["eon14_hard"]
    check("seven lines", len(h["lines"]) == 7)
    check("capex 11.42", abs(h["capex"] - 11.42) < 1e-9, f"{h['capex']}")
    check("cong 1.440", abs(h["congestion"] - 1.4403113122998072) < 1e-9)
    check("cong reduction 98.1pct",
          abs(h["congestion_reduction"]["thermal_pct"] - 98.132) < 0.01,
          f"{h['congestion_reduction']['thermal_pct']:.2f}")

    print("outcome 4 — MPS true-cost sweep")
    sweep = {r["chi"]: r for r in h["mps_chi_sweep"]}
    check("chi=4 is +9.1% and wrong",
          (not sweep[4]["matches_exact"]) and abs(sweep[4]["gap_pct"] - 9.06) < 0.05)
    check("chi=16 exact", sweep[16]["matches_exact"] and sweep[16]["gap"] == 0.0)
    deg2 = [1, 0, 1, 1, 0, 0, 0, 1, 1, 1]
    check("chi=4 plan = Dirac deg-2 plan", sweep[4]["plan"] == deg2)

    if fails:
        print(f"VERIFY FAIL: {fails}")
        return 1
    print("VERIFY PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
