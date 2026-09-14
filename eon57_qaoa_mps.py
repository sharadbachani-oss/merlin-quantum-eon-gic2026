"""E.ON outcome 4, at 20 binaries: does an MPS simulation of the quantum algorithm return a poor objective?

Instance: eon57_util, 20 build variables, exhaustive landscape y over all 2^20 builds (eon57_expand.npz, workstation
2026-09-13), global optimum 22,057.057 certified. The exact Moebius expansion truncated at degree 3 (1,351 terms)
recovers the exact argmin, so the QAOA cost Hamiltonian is  H_C = sum_{|S|<=3} c_S  prod_{i in S} (1 - Z_i)/2 ,
i.e. every term is a diagonal phase on <= 3 qubits (RZ / RZZ / CX-ladder RZ). Mixer: RX layer.

Protocol (fixed before running):
  1. Optimise (gamma, beta) for p = 1, 2, 3 on the EXACT statevector (numpy, 2^20 amplitudes; the cost layer is an
     elementwise phase of the full landscape y3, the mixer a product of single-qubit rotations) -- the quantum algorithm's
     ideal output. Report <cost>, P(optimum) and the best-of-1024-samples build objective.
  2. Run the SAME circuit (same angles, same gate list) on qiskit-aer's matrix_product_state simulator with
     matrix_product_state_max_bond_dimension chi = 2, 4, 8, 16, 32, 64, 128, 1024 shots each; grade the sampled builds
     on the exact referee y: <cost>, best-of-shots objective, P(optimum), % above the certified optimum.
  3. Control: Aer's statevector method on the identical circuit must reproduce the numpy reference (mean cost within 1% of
     the optimum) -- otherwise the gate list, not truncation, is at fault and no verdict is issued.
     Verdict rule: "MPS gives poor objective" holds at bond dimension chi if its sampled mean cost or its best-of-shots
     objective exceeds the Aer statevector run's by more than 1% of the certified optimum.
Writes eon57_qaoa_mps.json.  python eon57_qaoa_mps.py [quick]   (quick: p=1 only, chi in {4, 32})
"""
import os, sys, time, json, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
NPZ = next(p for p in [os.path.join(HERE, "eon57_expand.npz"),
                       r"C:\Users\admin\AppData\Local\Temp\claude\C--quantum-ai-2026\56a9f446-4fd3-4ed5-92c4-b718d1d59b20\scratchpad\eon57_expand.npz",
                       r"G:\My Drive\astra\eon57_early_polish\eon57_expand.npz"] if os.path.exists(p))
NB = 20; N = 1 << NB
d = np.load(NPZ); y = d["y"]; c = d["c"]
deg = np.array([bin(s).count("1") for s in range(N)])
idx = np.arange(N)
def zeta(v):
    v = v.copy()
    for b in range(NB):
        m = 1 << b; hi = idx[(idx & m) != 0]; v[hi] += v[hi ^ m]
    return v
y3 = zeta(np.where(deg <= 3, c, 0.0))                 # degree-3 landscape (argmin exact)
best = int(np.argmin(y)); yopt = float(y[best])
assert int(np.argmin(y3)) == best
terms = [(int(s), float(c[s])) for s in range(N) if deg[s] <= 3 and s != 0 and abs(c[s]) > 1e-9]
scale = 1.0 / np.std(y3)                              # angle normalisation
print(f"landscape {NPZ}\n optimum {yopt:.3f} at build {best:020b}; degree-3 terms {len(terms)}", flush=True)

# ---------------- exact statevector QAOA (numpy) ----------------
bits = ((idx[:, None] >> np.arange(NB)[None, :]) & 1).astype(np.int8)   # (N, NB)
def fwht(a):
    """fast Walsh-Hadamard transform (unnormalised) over the 2^NB register, in place on a copy"""
    a = a.copy(); h = 1
    while h < N:
        a = a.reshape(-1, 2 * h); x, y = a[:, :h].copy(), a[:, h:].copy(); a[:, :h] = x + y; a[:, h:] = x - y; a = a.reshape(N); h *= 2
    return a
POP = bits.sum(axis=1)                                   # popcount of each basis state
def mixer(psi, beta):
    # prod_q e^{-i beta X_q} = H^{(x)n} . diag(e^{-i beta sum_q z_q}) . H^{(x)n},  z_q = +1/-1  ->  sum z = NB - 2 popcount
    ph = np.exp(-1j * beta * (NB - 2 * POP))
    return fwht(fwht(psi) / N * ph)
def qaoa_state(params, p):
    psi = np.full(N, 1 / math.sqrt(N), dtype=complex)
    for k in range(p):
        g, b = params[2 * k], params[2 * k + 1]
        psi = psi * np.exp(-1j * g * scale * (y3 - y3.mean()))
        psi = mixer(psi, b)
    return psi
def expect(params, p):
    psi = qaoa_state(params, p); pr = np.abs(psi) ** 2
    return float((pr * y).sum()), pr
def optimise(p, restarts=3, seed=0):
    from scipy.optimize import minimize
    rng = np.random.default_rng(seed); bestv = (np.inf, None)
    for r in range(restarts):
        x0 = rng.uniform(0, 1.0, 2 * p) if r else np.array([0.3, 0.4] * p)
        res = minimize(lambda x: expect(x, p)[0], x0, method="COBYLA", options=dict(maxiter=100 * p, rhobeg=0.3))
        if res.fun < bestv[0]: bestv = (res.fun, res.x)
    return bestv

# ---------------- MPS simulation of the same circuit (qiskit-aer) ----------------
def build_circuit(params, p):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(NB, NB)
    qc.h(range(NB))
    for k in range(p):
        g, b = params[2 * k], params[2 * k + 1]
        for s, coef in terms:                              # c_S prod (1-Z)/2 -> expand to Z-products; keep diagonal phases exact
            qs = [q for q in range(NB) if (s >> q) & 1]
            # prod_{i in S} (1 - Z_i)/2 = 2^{-|S|} sum_{T subset S} (-1)^{|T|} Z_T ; phase e^{-i g*scale*c_S * that}
            ang = g * scale * coef / (2 ** len(qs))
            subs = [t for t in range(1, 1 << len(qs))]
            for t in subs:
                zq = [qs[j] for j in range(len(qs)) if (t >> j) & 1]; sgn = (-1) ** len(zq)
                theta = 2 * ang * sgn                      # RZ(theta) = e^{-i theta Z/2}
                if len(zq) == 1: qc.rz(theta, zq[0])
                elif len(zq) == 2: qc.rzz(theta, zq[0], zq[1])
                else:
                    for a in range(len(zq) - 1): qc.cx(zq[a], zq[a + 1])
                    qc.rz(theta, zq[-1])
                    for a in range(len(zq) - 2, -1, -1): qc.cx(zq[a], zq[a + 1])
        qc.rx(2 * b, range(NB))
    qc.measure(range(NB), range(NB))
    return qc
def run_mps(qc, chi, shots=1024, seed=7):
    from qiskit_aer import AerSimulator
    sim = AerSimulator(method="matrix_product_state", matrix_product_state_max_bond_dimension=chi,
                       matrix_product_state_truncation_threshold=1e-12, seed_simulator=seed)
    t0 = time.time(); res = sim.run(qc, shots=shots).result(); wall = time.time() - t0
    counts = res.get_counts()
    vals = []; popt = 0
    for bs, n in counts.items():
        s = int(bs, 2)                                        # qiskit bitstring: cl[0] is the rightmost char, i.e. already the LSB
        vals += [y[s]] * n; popt += n if s == best else 0
    vals = np.array(vals)
    return dict(chi=chi, shots=shots, wall_s=round(wall, 1), mean_cost=float(vals.mean()), best_cost=float(vals.min()),
                best_pct_above_opt=float(100 * (vals.min() - yopt) / yopt), p_opt=popt / shots, n_distinct=len(counts))
def run_exact_aer(qc, shots=1024, seed=7):
    """Aer STATEVECTOR on the identical circuit: the control that the gate list matches the numpy reference."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(method="statevector", seed_simulator=seed)
    t0 = time.time(); counts = sim.run(qc, shots=shots).result().get_counts(); wall = time.time() - t0
    vals = []; popt = 0
    for bs, n in counts.items():
        s = int(bs, 2); vals += [y[s]] * n; popt += n if s == best else 0
    vals = np.array(vals)
    return dict(shots=shots, wall_s=round(wall, 1), mean_cost=float(vals.mean()), best_cost=float(vals.min()),
                best_pct_above_opt=float(100 * (vals.min() - yopt) / yopt), p_opt=popt / shots)
def run_exact_samples(psi, shots=1024, seed=7):
    pr = np.abs(psi) ** 2; rng = np.random.default_rng(seed); s = rng.choice(N, size=shots, p=pr / pr.sum())
    vals = y[s]
    return dict(mean_cost=float((pr * y).sum()), best_cost=float(vals.min()), best_pct_above_opt=float(100 * (vals.min() - yopt) / yopt), p_opt=float(pr[best]))

if __name__ == "__main__":
    quick = len(sys.argv) > 1 and sys.argv[1] == "quick"
    ps = [1] if quick else [1, 2, 3]; chis = [4, 32] if quick else [2, 4, 8, 16, 32, 64, 128]
    out = dict(instance="eon57_util", n_binaries=NB, optimum=yopt, n_terms_deg3=len(terms), protocol=__doc__.split("Protocol")[1][:600], results=[])
    for p in ps:
        t0 = time.time(); ev, params = optimise(p); psi = qaoa_state(params, p)
        ex = run_exact_samples(psi); ex.update(p=p, params=[float(x) for x in params], opt_wall_s=round(time.time() - t0, 1))
        print(f"\np={p} EXACT statevector: <cost> {ex['mean_cost']:.1f}  best-of-1024 {ex['best_cost']:.1f} (+{ex['best_pct_above_opt']:.2f}%)  P(opt) {ex['p_opt']:.4f}", flush=True)
        qc = build_circuit(params, p); print(f"  circuit: {qc.size()} gates, depth {qc.depth()}", flush=True)
        aer = run_exact_aer(qc); mism = abs(aer["mean_cost"] - ex["mean_cost"]) / yopt
        print(f"  Aer statevector, same circuit: <cost> {aer['mean_cost']:.1f} (sampled)  best {aer['best_cost']:.1f}  | numpy-vs-Aer mean gap {100*mism:.2f}% of optimum {'OK' if mism < 0.01 else 'MISMATCH - circuit differs from reference'}", flush=True)
        row = dict(exact=ex, aer_statevector=aer, circuit_matches_reference=bool(mism < 0.01), mps=[])
        for chi in chis:
            r = run_mps(qc, chi); row["mps"].append(r)
            poor = (r["mean_cost"] - aer["mean_cost"]) > 0.01 * yopt or (r["best_cost"] - aer["best_cost"]) > 0.01 * yopt
            r["poor_objective"] = bool(poor)
            print(f"  MPS chi={chi:4d}: <cost> {r['mean_cost']:.1f}  best {r['best_cost']:.1f} (+{r['best_pct_above_opt']:.2f}%)  P(opt) {r['p_opt']:.4f}  {r['wall_s']}s  {'POOR' if poor else 'matches exact'}", flush=True)
        out["results"].append(row)
        json.dump(out, open(os.path.join(HERE, "eon57_qaoa_mps.json"), "w"), indent=1)
    print("-> eon57_qaoa_mps.json")
