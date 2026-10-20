# Hybrid XY-QAOA column-generation-based heuristic for CVRP (quantum simulator)

**Submitter:** Monit Sharma (Singapore Management University) · **Paradigm:** Quantum Simulator · **Algorithm:** stochastic, 300 shots per quantum call, 10 independent runs per instance · **AI disclosure:** `assisted` (see below)

## Results

* All 55 instances solved by the hybrid workflow; 550/550 runs returned a feasible plan.
* The best of 10 runs equals the proven optimum on **45/55** instances. The mean gap of the best plan is 0.12% and the largest is 2.16%.
* 174 of 550 individual runs reached the proven optimum.

The proven optima come from our classical reference computation (route enumeration + set partitioning; source and outputs in the bundled archive). They are quoted for gap reporting only. The optimizer does not use those values or reference routes; they are read only after solving for scoring.

## Comparison with a uniform-sampling control

Every seed was also run with **each QAOA circuit replaced by uniform sampling of the same subspace, with the same number of shots**. Everything classical stayed identical: LP, exact tour lengths, staging rules.

| | QAOA (submitted) | uniform-sampling control |
|---|---|---|
| instances whose best of 10 runs is optimal | 45/55 | 42/55 |
| runs at the proven optimum | 174/550 | 89/550 |
| mean gap of a single run | 1.47% | 2.67% |
| instances with the lower mean cost | 47 | 8 |

Across the **55 paired instance means**, QAOA has lower mean cost on **47/55** instances (paired Wilcoxon signed-rank p = **1.96e-7**). This comparison summarizes effects across instances.

Run by run (same instance, same seed): QAOA gives the cheaper plan in **326** runs, uniform sampling in 165, and 59 tie (Wilcoxon signed-rank p = 7.4e-19).

The 300-shot-per-call setting was chosen in an exploratory study using the same 55 instances and partly overlapping seeds. The submitted campaign is therefore not an independent test set. Pilot outcome counts are not used as evidence here; the complete 550+550 campaign records bundled with this submission support the comparisons above.

## Method

All XSH instances are exact-load (total demand = K·Q), so every route carries exactly Q, and a plan is 4 disjoint routes covering all 20 customers.

| step | runs on | qubits | decides |
|---|---|---|---|
| customer prices λ | classical LP (HiGHS) over the current route pool | none | no route is chosen |
| pricing: propose routes | **QAOA** per route size s: Dicke(20, s) initial state, ring XY mixer, p = 3; cost = quadratic route-length surrogate − λ + exact load-equality penalty | 20 | which customer sets are sampled |
| within-route optimization | classical Held–Karp on each sampled set with load exactly Q | none | the optimal visiting order and length for that subset |
| route selection | **QAOA** over exactly-4-route states of a 16-route pool (Dicke(16, 4), XY mixer, p = 4); cost = total length + penalty per shared customer | 16 | which routes are sampled together |
| staging | non-overlapping routes found in the samples, ranked by length + restricted-pool LP look-ahead score for the uncovered customers; the best 3 are kept, then **QAOA** pricing and selection rerun on the uncovered customers only | fewer than the first call | which sampled routes are kept |
| last route | forced: the remaining customers carry exactly Q | none | no choice left |

Quantum samples propose customer subsets and route combinations. Classical LP optimization supplies prices and selects the candidate pool; exact within-route tour optimization chooses visiting orders; classical staged search ranks and assembles sampled proposals. The final remaining customer set is forced when one route remains.

Dicke initialization and XY mixing preserve customer-subset cardinality during pricing and selected-route count during selection. They do **not** preserve exact load or route disjointness by themselves: load and overlap are handled through cost penalties and classical filtering, and complete returned plans are checked for CVRP feasibility.

The residual LP look-ahead score uses only routes in the current pool, with artificial cover columns. It guides beam ranking and is not a certified lower bound on completions using every possible route. Finite sampled pricing is heuristic: finding no improving column does not certify that none exists.

 Angles are CVaR-optimised (L-BFGS-B) on the exact simulator and then sampled with a fixed number of shots. The circuits are simulated exactly in the fixed-Hamming-weight subspace. The simulator is checked gate for gate against the equivalent Qiskit circuits (`tests/test_quantum_core.py`, `tests/test_routing_quantum.py`).

This reworks the qubit-scalable decomposition of [arXiv:2604.22194](https://arxiv.org/abs/2604.22194). The quantum circuits propose customer subsets and combinations of classically sequenced routes; the mixers preserve the stated cardinality constraints.

## Scope

Model counts describe maximum pricing-circuit width. Classical LP sizes and QUBO coefficients vary per call; full historical coefficient statistics were not archived. The shot budget was selected on the same 55 instances with overlapping seeds, so this is an exploratory benchmark. The uniform comparison matches shots per call, not total shots per adaptive solve or the classical computational effort of exact angle optimization. Exact CVaR training uses simulator probabilities; the reported measurement draws do not include a shot-based hardware training protocol. The uniform ablation is not a strong cost-informed classical baseline.

Stopping: stage 1 ends at 40 rounds or two consecutive stalled rounds; stage 2 uses finite beam recursion (beam 3), two residual pricing rounds and a call guard of 40. No known-optimum cutoff is used; TTS is time to each run's final best incumbent and may be smaller than total runtime. Success threshold epsilon=0 is relative to the algorithm's own best objective over these runs.

At n = 20 these instances are classically easy: our exact solver proves all 55 optima quickly on these small instances (historical summed per-instance wall times: 76.4 s). This entry benchmarks quantum components against known optima and against a matched classical sampling control. It makes no claim of quantum advantage. Runtimes are those of the classical simulation of the circuits, so QPU Runtime is N/A.

## Reproduce

The complete review snapshot is included here as [`misc/solver_source_snapshot.zip`](misc/solver_source_snapshot.zip), so reproduction does not depend on access to the original solver repository. It contains the unchanged selected solver files from commit `cb000afafee1f25a3885b0b24427e57f5aa6b50b`, both per-seed campaigns (1,100 plans), the Qiskit equivalence tests, classical reference solvers and all 55 reference outputs. The 55 input instances and QOBLIB licenses come from upstream commit `8d0104f5af0cce25de0c973e7a731d138516e665`.

[`misc/source_snapshot_manifest.json`](misc/source_snapshot_manifest.json) records every archive member's SHA-256 and source commit; `misc/provenance.json` records the ZIP hash. These are historical measurements; later solver repairs are not substituted into the measured campaign. The original repository URL is a provenance identifier and is not required to retrieve this bundle.

Download the ZIP, manifest, `requirements-simulator.txt` and `verify_reproducibility.py` from `misc/` into one directory. With Python 3.12, first audit the archive without installing packages:

```text
python verify_reproducibility.py
python -m zipfile -e solver_source_snapshot.zip reproduction
```

The audit independently checks all 1,100 archived route plans against the bundled instances and checks all 55 reference witnesses. To run the original circuit tests, install the recorded environment inside the extracted `reproduction` directory:

```text
uv venv --python 3.12 .venv
uv pip install --python .venv -r ../requirements-simulator.txt
uv pip install --python .venv --no-deps -e . -e vrp
```

Use `.venv/Scripts/python` on Windows or `.venv/bin/python` on Linux/macOS as `<venv-python>`:

```text
<venv-python> -m pytest tests/test_quantum_core.py tests/test_routing_quantum.py -q
<venv-python> -m qvrp.submit run --runs 10 --workers 1
```

The run command skips existing archived records. For a fresh campaign, move `vrp/results/quantum_sim/runs.jsonl` aside **inside the reproduction directory only** before running. The ZIP contains no old `vrp/results/raw/cg/submit_*` caches. The command runs both QAOA and uniform variants. One worker is sufficient; the measured campaign used 14 parallel workers. Runtime depends on the reproduction machine; do not mix fresh output with submitted measurements.

The separate classical reference solver (`problems/09-routing/classical/cvrp_sp.py`) requires `gurobipy` and a suitable Gurobi license to regenerate optimality proofs; neither is needed for the simulator or the archive audit. Reference solution feasibility can be checked independently, while the bundled historical solver records report the original optimality evidence.

The pinned packaging command predates the reporting corrections here. This submission preserves measured values and traces, uses an accessible bundled source reference, clarifies the circuit-width fields, and marks unavailable dynamic coefficient statistics as N/A. `misc/provenance.json` records file hashes and the distinction.

## Validation

<!-- OFFICIAL-VALIDATION:START -->
All 55 exported solutions pass the unmodified official QOBLIB Rust CVRP checker and match the CSV objective. Upstream CSV/time-series structure checks also pass 55/55. Per-instance outputs and hashes are in `misc/official_validation.json`.
<!-- OFFICIAL-VALIDATION:END -->

Ten recorded objective traces per instance are included. A final repeated incumbent at the recorded run end is an end marker, not an invented improvement. `Optimality Bound=N/A` throughout: matching a known optimum does not mean this quantum heuristic produced an optimality proof.

**Hardware:** Intel Core i7-12700K (12 cores / 20 threads), 32 GB RAM, Windows 11; one process per run (single-threaded), 14 runs in parallel.
**Software:** Python 3.12.14, numpy 2.5.3, scipy 1.18.1 (HiGHS LP), numba, Qiskit 2.5.2 (circuit cross-check); exact fixed-Hamming-weight statevector simulator qobench.quantum.subspace.

## AI disclosure

**`assisted`** under the QOBLIB [AI policy](https://github.com/ZIB-AOPT/QOBLIB/blob/main/AI_POLICY.md). Claude Code (Claude Opus 5.5, Anthropic) assisted with initial drafts of the solver (`vrp/qvrp/`, `qobench/quantum/subspace.py`), tests, notebooks, packaging scripts and write-up. OpenAI Codex (GPT-6.1 Sol, OpenAI) assisted with verification, reporting corrections, reproducibility packaging, documentation and the fork-only submission rehearsal. The tools and model versions are identified by the submitter, who confirmed that this was assisted work and that the original drafts were reviewed and edited. Monit Sharma is responsible for final review, the correctness of the submission and its reported results. No AI system is part of the optimization algorithm.
