# Submission for XSH-n20-k4-47

This directory contains the submission for the problem **XSH-n20-k4-47**.

| Field | Value 1 |
| --- | --- |
| Problem | XSH-n20-k4-47 |
| Submitter | Monit Sharma |
| Affiliation | Singapore Management University |
| Date | 2026-10-14 |
| ====== |  |
| Reference | https://github.com/MonitSharma/QOBLIB/tree/vrp/09-routing/submissions/20261014_QAOAColumnGeneration_Sharma |
| Best Objective Value | 583 |
| Optimality Bound | N/A |
| ====== |  |
| Modeling Approach | Set partitioning over exact-load routes, addressed by a column-generation-based heuristic. Pricing: one QUBO per route size (20 binary variables, exact load-equality penalty); route selection: QUBO over pool routes (<= 16 binary variables, overlap penalty). Both sampled with XY-mixer QAOA from Dicke states |
| # Decision Variables | 20 |
| # Binary Variables | 20 |
| # Integer Variables | 0 |
| # Continuous Variables | 0 |
| # Non-Zero Coefficients | N/A |
| Coefficients Type | real |
| Coefficients Range | N/A |
| ====== |  |
| Workflow | Pre-processing: EUC_2D rounded distances; route sizes able to carry exactly Q (subset-sum table). Main: (1) heuristic column generation: restricted-master LP (HiGHS) gives customer prices; per route size s a QAOA circuit (Dicke(20,s) initial state, ring XY mixer, p=3, CVaR-optimised angles) samples customer sets; each sampled set with load exactly Q gets its optimal visiting order and exact tour length (classical Held-Karp) and joins the pool if its reduced cost is negative; dual smoothing and shot reallocation between route sizes; stop after 2 rounds without a new route. (2) staged route selection: QAOA over exactly-4-route states of a 16-route pool (Dicke(16,4), XY mixer, p=4) samples plans; non-overlapping routes in the samples are ranked by length + restricted-pool LP look-ahead score for the uncovered customers, the best 3 are fixed, and pricing and selection rerun on the uncovered customers with fewer qubits; the last route is forced. Post-processing: best complete plan among the samples. All circuits are simulated exactly (statevector in the fixed-Hamming-weight subspace) and sampled with a fixed number of shots. XY mixing preserves cardinality; load/overlap require penalties and filtering. The residual LP score is not a certified bound over all routes. |
| Algorithm Type | Stochastic |
| Paradigm | Quantum Simulator |
| # Runs | 10 |
| # Feasible Runs | 10 |
| # Successful Runs | 1 |
| Success Threshold | 0 |
| ====== |  |
| Hardware Specifications | Intel Core i7-12700K (12 cores / 20 threads), 32 GB RAM, Windows 11; one process per run (single-threaded), 14 runs in parallel |
| ====== |  |
| Total Runtime | 36.124 |
| Time to Solution | 34.987 |
| CPU Runtime | 35.163 |
| GPU Runtime | N/A |
| QPU Runtime | N/A |
| Other HW Runtime | N/A |
| ====== |  |
| Remarks | Best of 10 independent runs (seeds 0-9), 300 shots per quantum call. Proven optimum (our classical reference computation) = 583; gap of best = 0.00%; 1/10 runs reached it. Control: the same pipeline with every QAOA circuit replaced by uniform sampling of the same subspaces with the same shots reached best 583 (mean 592.2 vs QAOA mean 590.8; optimum in 1/10 runs). Largest circuit: 20 qubits; mean 225 circuits and 67,469 shots per run. Runtimes are wall-clock of the classical simulation of the circuits (QPU Runtime N/A). Model fields report the maximum pricing-circuit width, not the changing classical LP. Coefficient counts/ranges vary per call and were not archived for this historical campaign. AI disclosure: assisted (see README). |
