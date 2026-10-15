# Quantum column generation with XY-mixer QAOA for CVRP (quantum simulator)

**Submitter:** Monit Sharma (Singapore Management University) · **Paradigm:** Quantum Simulator · **Algorithm:** stochastic, 300 shots per quantum call, 10 independent runs per instance · **AI disclosure:** `assisted` (see below)

## Results

* All 55 instances solved by the quantum workflow; 550/550 runs returned a feasible plan.
* The best of 10 runs equals the proven optimum on **45/55** instances. The mean gap of the best plan is 0.12% and the largest is 2.16%.
* 174 of 550 individual runs reached the proven optimum.

The proven optima come from our classical submission (route enumeration + set partitioning). They are quoted for gap reporting only. The optimizer does not use those values or reference routes; they are read only after solving for scoring.

## Comparison with a uniform-sampling control

Every seed was also run with **each QAOA circuit replaced by uniform sampling of the same subspace, with the same number of shots**. Everything classical stayed identical: LP, exact tour lengths, staging rules.

| | QAOA (submitted) | uniform-sampling control |
|---|---|---|
| instances whose best of 10 runs is optimal | 45/55 | 42/55 |
| runs at the proven optimum | 174/550 | 89/550 |
| mean gap of a single run | 1.47% | 2.67% |
| instances with the lower mean cost | 47 | 8 |

Run by run (same instance, same seed): QAOA gives the cheaper plan in **326** runs, uniform sampling in 165, and 59 tie (Wilcoxon signed-rank p = 7.4e-19).

The budget of 300 shots was fixed before this campaign, from a separate multi-seed study (55 instances × 3 seeds × budgets 100/300/1000). There, QAOA beat the control on paired runs at 100 shots (125 vs 26, Wilcoxon p = 4·10⁻¹⁸) and at 300 shots (93 vs 56, p = 2·10⁻⁵). At 1,000 shots the gain was not significant (p = 0.09). The 300-shot setting was selected from that exploratory study; the same instances and some seeds overlap the submitted campaign.

## Method

All XSH instances are exact-load (total demand = K·Q), so every route carries exactly Q, and a plan is 4 disjoint routes covering all 20 customers.

| step | runs on | qubits | decides |
|---|---|---|---|
| customer prices λ | classical LP (HiGHS) over the current route pool | none | no route is chosen |
| pricing: propose routes | **QAOA** per route size s: Dicke(20, s) initial state, ring XY mixer, p = 3; cost = quadratic route-length surrogate − λ + exact load-equality penalty | 20 | which customer sets are sampled |
| route length | classical Held–Karp on each sampled set with load exactly Q | none | the length of a sampled route |
| route selection | **QAOA** over exactly-4-route states of a 16-route pool (Dicke(16, 4), XY mixer, p = 4); cost = total length + penalty per shared customer | 16 | which routes are sampled together |
| staging | non-overlapping routes found in the samples, ranked by length + LP bound of the uncovered customers; the best 3 are kept, then **QAOA** pricing and selection rerun on the uncovered customers only | fewer than the first call | which sampled routes are kept |
| last route | forced: the remaining customers carry exactly Q | none | no choice left |

Every route in a submitted plan was either sampled by a QAOA circuit or forced by the routes sampled before it. Angles are CVaR-optimised (L-BFGS-B) on the exact simulator and then sampled with a fixed number of shots. The circuits are simulated exactly in the fixed-Hamming-weight subspace. The simulator is checked gate for gate against the equivalent Qiskit circuits (`tests/test_quantum_core.py`, `tests/test_routing_quantum.py`).

This reworks the qubit-scalable decomposition of [arXiv:2604.22194](https://arxiv.org/abs/2604.22194). The quantum circuits now generate and select whole routes, and constraint-preserving mixers replace slack and tilted penalties.

## Scope

Model counts describe maximum pricing-circuit width. Classical LP sizes and QUBO coefficients vary per call; full historical coefficient statistics were not archived. The shot budget was selected on the same 55 instances with overlapping seeds, so this is an exploratory benchmark. The uniform comparison matches shots per call, not the classical computational effort of exact angle optimization.

Stopping: stage 1 ends at 40 rounds or two consecutive stalled rounds; stage 2 uses finite beam recursion (beam 3), two residual pricing rounds and a call guard of 40. No known-optimum cutoff is used; TTS is time to each run's final best incumbent and may be smaller than total runtime. Success threshold epsilon=0 is relative to the algorithm's own best objective over these runs.

At n = 20 these instances are classically easy: our exact solver proves all 55 optima quickly on these small instances (historical summed per-instance wall times: 76.4 s). This entry benchmarks quantum components against known optima and against a matched classical sampling control. It makes no claim of quantum advantage. Runtimes are those of the classical simulation of the circuits, so QPU Runtime is N/A.

## Reproduce

Public source and archived campaign: [cb000afafee1f25a3885b0b24427e57f5aa6b50b](https://github.com/MonitSharma/quantum_optimization_benchmarking/tree/cb000afafee1f25a3885b0b24427e57f5aa6b50b).
The results are historical measurements from this source snapshot; later hardware-protocol repairs are not substituted into the measured campaign.

```bash
git clone https://github.com/MonitSharma/quantum_optimization_benchmarking
cd quantum_optimization_benchmarking
git checkout cb000afafee1f25a3885b0b24427e57f5aa6b50b
git clone https://github.com/ZIB-AOPT/QOBLIB.git external/QOBLIB
git -C external/QOBLIB checkout 8d0104f5af0cce25de0c973e7a731d138516e665
uv venv --python 3.12 .venv
# Save misc/requirements-simulator.txt from this submission to the checkout first.
uv pip install --python .venv -r requirements-simulator.txt
uv pip install --python .venv --no-deps -e . -e vrp
```

On Windows use `.venv/Scripts/python`; on Linux/macOS use `.venv/bin/python`:

```text
<venv-python> -m pytest tests/test_quantum_core.py tests/test_routing_quantum.py -q
<venv-python> -m qvrp.submit run --runs 10 --workers 1
```

For a fresh computation, use a clean clone: the pinned command skips already archived runs. Move `vrp/results/quantum_sim/runs.jsonl` aside **in the reproduction clone only**, and remove any old `vrp/results/raw/cg/submit_*` caches before running. One worker is sufficient; the measured campaign used 14 parallel workers. Runtime depends on the reproduction machine. Do not mix reproduction output with the submitted measurements.

The pinned packaging command predates the reporting corrections here. This submission preserves measured values and traces, pins Reference URLs, clarifies the circuit-width fields, and marks unavailable dynamic coefficient statistics as N/A. `misc/provenance.json` records file hashes and the distinction.

## Validation

<!-- OFFICIAL-VALIDATION:START -->
All 55 exported solutions pass the unmodified official QOBLIB Rust CVRP checker and match the CSV objective. Upstream CSV/time-series structure checks also pass 55/55. Per-instance outputs and hashes are in `misc/official_validation.json`.
<!-- OFFICIAL-VALIDATION:END -->

Ten recorded objective traces per instance are included. A final repeated incumbent at the recorded run end is an end marker, not an invented improvement. `Optimality Bound=N/A` throughout: matching a known optimum does not mean this quantum heuristic produced an optimality proof.

**Hardware:** Intel Core i7-12700K (12 cores / 20 threads), 32 GB RAM, Windows 11; one process per run (single-threaded), 14 runs in parallel.
**Software:** Python 3.12.14, numpy 2.5.3, scipy 1.18.1 (HiGHS LP), numba, Qiskit 2.5.2 (circuit cross-check); exact fixed-Hamming-weight statevector simulator qobench.quantum.subspace.

## AI disclosure

**`assisted`** under the QOBLIB [AI policy](https://github.com/ZIB-AOPT/QOBLIB/blob/main/AI_POLICY.md). The solver code (`vrp/qvrp/`, `qobench/quantum/subspace.py`), the tests, the notebooks, the packaging scripts and this README were drafted with Claude Code (model: Claude Opus 5.5, Anthropic). They were then reviewed, run and edited by the submitter, Monit Sharma, who is responsible for this submission and opened the pull request. The method builds on the submitter's own work (arXiv:2604.22194). No AI system is part of the optimization method.
