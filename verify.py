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

    print("v5 dynamics crossing")
    xing_path = ROOT / "results" / "eon_dynamics_crossing.json"
    check("crossing receipt present", xing_path.exists())
    if xing_path.exists():
        xing = json.loads(xing_path.read_text())
        g = xing["crossing"]["gates"]
        check("realtime ranks with referee", g["realtime_ranks_with_referee"])
        check("two imag-time spectra disagree", g["imag_time_two_spectra_disagree"])
        check("continuation misses realtime line", g["continuation_misses_realtime_line"])
        check("factorized A6-off ranking fails", g["factorized_wrong_dL_order"])
        check("cheap local ranking fails", g["cheap_local_wrong_dL_order"])
        it = xing["imaginary_time"]
        check("certified leftover line is 0.222",
              abs(it["realtime_cyc_per_step"] - 2.0 / 9.0) < 1e-9)
        check("continuation not the realtime line",
              abs(it["continuation_cyc_per_step"] - it["realtime_cyc_per_step"]) > 0.04)
        fac = xing["factorized_no_A6_bonds"]
        check("A6-off cannot rank builds", fac["ranking_fails"])
        hw = xing["hardware"]
        fk = hw["full_k_spectrum"]
        check("full-k leftover spectrum not flown",
              fk["status"] == "NOT_FLOWN" and fk["job_id"] is None)
        check("full-k one-command is retrieve-first",
              fk["protocol"].get("one_command") == "python eon_full_k_leftover.py"
              and fk["protocol"].get("default", "").startswith("retrieve only"))
        check("VW 64-rung spectrum not claimed",
              hw["vw_64rung_spectrum"]["status"] == "NOT_AN_EON_RESULT")
        check("Aquila map is protocol only",
              hw["aquila_rydberg"]["status"] == "NOT_FLOWN"
              and hw["aquila_rydberg"]["job_id"] is None)
        check("kingston job unchanged",
              hw["two_point_flown"]["kingston"]["job"] == "daa0dq6rbfbs73ci56bg")
        check("marrakesh job unchanged",
              hw["two_point_flown"]["marrakesh"]["job"] == "daa9do6rbfbs73cifa80")

    print("v5 E.ON-native storage")
    store = json.loads((ROOT / "results" / "eon_storage_sizing.json").read_text())
    check("storage is leftover spectrum, not a hardware job",
          store.get("hardware_spectrum_job") is None
          and store.get("hardware_spectrum_status") == "NOT_FLOWN")
    check("VW job dropped from storage",
          store.get("dropped_vw_job") == "daa9pn4e74ec73akj9i0")
    leftover_cmd = ROOT / "eon_full_k_leftover.py"
    leftover_rcpt = ROOT / "results" / "eon_full_k_leftover.json"
    check("full-k one-command present", leftover_cmd.exists())
    check("full-k leftover receipt present", leftover_rcpt.exists())
    if leftover_rcpt.exists():
        lk = json.loads(leftover_rcpt.read_text())
        check("leftover receipt is protocol-only",
              lk.get("status") == "NOT_FLOWN" and lk.get("job_id") is None)
        check("leftover receipt refuses VW job",
              lk.get("honesty", {}).get("vw_job_refused") == "daa9pn4e74ec73akj9i0")
        check("two-point jobs are not a leftover series",
              "daa0dq6rbfbs73ci56bg" in lk.get("honesty", {}).get("two_point_not_a_series", [])
              and "daa9do6rbfbs73cifa80" in lk.get("honesty", {}).get("two_point_not_a_series", []))
        nf = lk.get("next_flight_dense", {})
        check("Mitsubishi closer is dense k=0..8, 29 circuits",
              nf.get("k") == [0, 1, 2, 3, 4, 5, 6, 7, 8]
              and nf.get("n_circuits") == 29
              and nf.get("closes_mitsubishi") is True)
        check("no invented leftover job id",
              lk.get("honesty", {}).get("invented_ids") is False)
    qE = store["results"]["Q"][0]
    cE = store["results"]["C"][0]
    check("continuation undersizes vs realtime spectrum",
          cE < qE and abs(store["continuation_rel_err"] - (qE - cE) / qE) < 1e-9,
          f"Q={qE:.2f} C={cE:.2f}")

    if fails:
        print(f"VERIFY FAIL: {fails}")
        return 1
    print("VERIFY PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
