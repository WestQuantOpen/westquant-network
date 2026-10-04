# WestQuant Network — Four-Simulator Compatibility, Validation, Benchmark and Adapter Program

**Version:** 0.1.0 (Phase A — Simulator Audit)
**Status:** Living document. Updated as phases complete.
**Owner:** WestQuant Open

---

## Executive Summary

WestQuant Network is a simulator-independent framework for quantum-network modelling, simulation, benchmarking, representation search, and AI-driven optimization.

The initial four simulator backends are:

| Backend | Strength | Layer focus |
|---------|----------|-------------|
| **SeQUeNCe** | Resource management, protocols, rule-based local control | Hardware → Application |
| **NetSquid** | Time-dependent decoherence, physical state formalisms | Physics |
| **SimQN** | Network-layer scale, routing, topology | Network |
| **Qoala** | Application execution, scheduling, multitasking | Software/Hardware |

**The goal is NOT to declare one simulator "best".**

The goal is to determine:

> How can WestQuant become a strong, scientifically correct and practically useful add-on layer for all four simulators while preserving the distinctive capabilities and validity domains of each backend?

The final architecture should allow a researcher to describe an experiment once at the WestQuant level and execute it on one or more compatible backends whenever scientifically meaningful.

**We must NEVER assume that two simulations are scientifically equivalent simply because the input parameters have the same names.**

---

## Research Principles

### P0.1 Do not force false equivalence

If two simulators implement different abstractions of decoherence, fidelity, loss, entanglement generation, memory, swapping, purification, timing, or control-plane communication, do not silently translate one into the other.

Every translation must explicitly state whether it is:

- `EXACT`
- `SEMANTICALLY_EQUIVALENT`
- `APPROXIMATED`
- `BACKEND_NATIVE`
- `IGNORED`
- `UNSUPPORTED`
- `UNKNOWN`

### P0.2 Distinguish physics from network abstractions

For every simulator identify what is represented as:

- physical quantum state
- stochastic physical process
- phenomenological fidelity/loss model
- network-level abstraction
- software/runtime abstraction

Never compare models across these levels without documenting the approximation.

### P0.3 Reproducibility first

Every experiment must record: simulator, simulator version, Python version, OS, dependencies, configuration, input schema, random seed, number of repetitions, wall-clock time, CPU time, peak RAM, event count where available, git commit, WestQuant adapter version.

All generated data must be machine-readable.

---

## Part 1. Simulator Audit

Before coding adapters, inspect the latest documentation, source code, examples, papers and releases for all four simulators.

### 1A. Installation and packaging

Evaluate: PyPI availability, private package repositories, authentication requirements, supported Python versions, supported operating systems, native/C/Cython dependencies, compiler requirements, ease of installation, Docker feasibility, CI/CD feasibility, licence, restrictions on redistribution, restrictions affecting an open-source WestQuant adapter, whether simulator dependencies can safely be optional dependencies.

Record:
- `installation_complexity = LOW | MEDIUM | HIGH`
- `CI_friendly = YES | PARTIAL | NO`
- `redistribution_constraints = ...`

### 1B. Simulation kernel

Determine: discrete-event vs timestep, event queue architecture, event timestamp precision, deterministic ordering of simultaneous events, cancellation support, priorities, callbacks, asynchronous protocol model, process/coroutine model, simulation clock semantics, ability to pause/resume, ability to inspect event queues, ability to inject custom events, ability to hook before/after events, ability to export event traces.

Test whether WestQuant can obtain: `event_id`, `timestamp`, `node`, `component`, `protocol`, `action`, `state_before`, `state_after` without modifying simulator internals.

---

## Part 2. Quantum State and Physical Model Audit

### 2.1 State representation

Test whether the backend supports: pure state vectors, density matrices, stabilizer states, Bell-pair abstractions, fidelity-only abstractions, user-defined state formalism, arbitrary qubit state, multi-qubit state, mixed state, entangled multipartite state.

Record scalability implications.

### 2.2 Noise

Test independently: depolarization, dephasing, amplitude damping, T1, T2, channel losses, operation error, measurement error, detector dark counts, detector efficiency, photon loss, memory decoherence, imperfect BSM, imperfect entanglement generation.

For each noise source determine: native? configurable? time-dependent? state-dependent? analytic? stochastic? composable?

---

## Part 3. Quantum Memory Test Program

### WQMemorySpec

| Parameter | Description |
|-----------|-------------|
| `capacity` | number of modes/qubits |
| `T1` | population lifetime |
| `T2` | coherence time |
| `initial_fidelity` | F |
| `write_efficiency` | ηw |
| `read_efficiency` | ηr |
| `write_latency` | ns–ms |
| `read_latency` | ns–ms |
| `operation_fidelity` | gate fidelity |
| `bandwidth` | Hz |
| `wavelength` | nm |
| `conversion_efficiency` | ηc |
| `multiplexing_modes` | temporal/spectral/spatial |
| `cutoff_time` | discard rule |
| `decoherence_model` | exponential/custom |
| `custom_parameters` | backend-specific |

### Memory tests

- **M1: Single memory decay** — Store for 0, 0.1T2, 0.25T2, 0.5T2, 1T2, 2T2, 5T2. Measure fidelity, survival probability, state error, output state, backend-specific internal state.
- **M2: Capacity** — Test 1, 2, 4, 8, 16, 32, 64, 128. Determine hard capacity enforcement, overflow behavior, allocation behaviour, resource manager behaviour, performance scaling.
- **M3: Write/read efficiency** — Sweep ηw, ηr ∈ {0.5, 0.7, 0.9, 0.99, 1.0}. Determine how each simulator represents failure.
- **M4: Heterogeneous memories** — Nodes with different memory classes. Determine native support vs adapter-level logic.
- **M5: Memory scheduling** — FIFO, LIFO, OLDEST_FIRST, YOUNGEST_FIRST, FIDELITY_FIRST, DEADLINE_FIRST, PRIORITY_FIRST, RANDOM. Measure qualified goodput, latency, fidelity, expired pairs, memory utilization, starvation, fairness.

---

## Part 4. Photonic Link Test Program

### WQQuantumLinkSpec

| Parameter | Description |
|-----------|-------------|
| `distance` | km |
| `speed` | propagation speed |
| `attenuation` | dB/km |
| `loss_probability` | per photon |
| `source_rate` | Hz |
| `source_efficiency` | ηsource |
| `detector_efficiency` | ηdet |
| `detector_dark_count` | per second |
| `wavelength` | nm |
| `channel_noise` | noise model |
| `classical_latency` | s |
| `quantum_latency` | s |

### Link tests

- **L1: Distance sweep** — 1, 5, 10, 25, 50, 100, 200 km. Measure successful entanglement rate, latency, fidelity, generation attempts.
- **L2: Loss sweep** — Sweep attenuation/loss independently of distance.
- **L3: Asymmetric links** — A→B ≠ B→A.
- **L4: Classical control latency** — Vary classical RTT while keeping quantum link constant.

---

## Part 5. Entanglement Generation

- **E1: Two-node generation** — A↔B. Measure raw_generation_rate, qualified_generation_rate, latency_distribution, fidelity_distribution, attempts_per_success.
- **E2: Generation under finite memory** — memory_capacity = 1, 2, 4, 8, 16.
- **E3: Generation under competing flows** — Multiple applications compete for elementary-link capacity.

---

## Part 6. Repeaters and Swapping

### WQRepeaterSpec + WQSwapPolicy

- **R1: Single repeater** — A—R—B. Test elementary-link generation, simultaneous vs asynchronous pair arrival, storage, BSM, swap success, classical notification, resulting fidelity.
- **R2: Repeater chain** — A-R1-R2-...-Rn-B. n = 1, 2, 3, 4, 7, 15. Measure scaling of latency, goodput, fidelity, memory occupation, event count, runtime.
- **R3: Swap policies** — SWAP_ASAP, BALANCED_TREE, LEFT_TO_RIGHT, RIGHT_TO_LEFT, AGE_AWARE, FIDELITY_AWARE.
- **R4: Swap failure** — Sweep swap success probability: 0.50, 0.70, 0.90, 0.95, 0.99, 1.00.

---

## Part 7. Purification

### WQPurificationPolicy

- NEVER, ALWAYS, FIDELITY_THRESHOLD, AGE_THRESHOLD, ADAPTIVE
- Test whether purification is natively implemented, user extensible, protocol-specific, or missing.
- Measure: fidelity_gain, pair_consumption, latency_cost, goodput_cost, net_utility.
- **Do not fake purification in a backend that cannot represent the required quantum state.**

---

## Part 8. Topologies

LINE, RING, STAR, TREE, GRID, MESH, ER_RANDOM, BA_SCALE_FREE, WAXMAN, REAL_WORLD_GRAPH, CUSTOM_GRAPH.

N = 2, 3, 5, 10, 25, 50, 100, 250, 500 as computationally feasible.

Document topology-size limits.

---

## Part 9. Routing

### WQRoutingPolicy

SHORTEST_HOP, SHORTEST_DISTANCE, DIJKSTRA_COST, K_SHORTEST, LOSS_AWARE, FIDELITY_AWARE, MEMORY_AWARE, CONGESTION_AWARE, DEADLINE_AWARE, MULTIPATH, CUSTOM.

- **RT1: Static routing** — Compare hop-count, distance, expected transmission probability.
- **RT2: Dynamic routing** — Change link fidelity, available memory, congestion, failed nodes/links during simulation.
- **RT3: Multipath** — Choose among multiple paths, distribute traffic, reserve multiple routes, fail over.
- **RT4: Joint routing and memory constraints** — Shortest path NOT optimal because intermediate repeater has low memory capacity, short T2, or congestion.

---

## Part 10. Traffic and Workload

Traffic models: SINGLE_REQUEST, PERIODIC, POISSON, BURST, MMPP, TRACE_DRIVEN.

Application mixtures: single flow, multiple independent flows, all-to-all, hotspot, incast, outcast, priority traffic, deadline traffic, mixed SLA traffic.

---

## Part 11. Resource Management

Test control granularity: FULL, PARTIAL, OBSERVE_ONLY, UNSUPPORTED for memory allocation, link allocation, generation scheduling, swap scheduling, purification scheduling, route reservation, request admission, priority, preemption.

---

## Part 12. Qoala-Specific Execution Tests

- Q1: One quantum-network application.
- Q2: Two applications competing for the same node.
- Q3: Multiple applications competing for memory and quantum processing.
- Q4: Vary classical CPU latency.
- Q5: Vary quantum processor latency.
- Q6: Vary network entanglement availability.

---

## Part 13. Cross-Simulator Golden Experiments

G01–G15: direct ideal link, lossy direct link, memory decay, single repeater, repeater chain, finite memory, competing requests, shortest-path routing, multipath topology, heterogeneous links, heterogeneous memories, congestion, deadline traffic, link failure, node failure.

For every experiment produce: Reference specification, Backend translations, TranslationReport, Raw results, Normalized results, Statistical comparison, Interpretation.

---

## Part 14. Cross-Simulator Invariance

- **Level A: Numerical agreement** — Are metric values statistically compatible?
- **Level B: Ranking agreement** — Do simulators agree about policy A > policy B? (Kendall τ, Spearman ρ, pairwise win/loss matrices)
- **Level C: Conclusion agreement** — Do they support the same scientific statement?

---

## Part 15. Sensitivity Analysis

For shared parameters sweep: T2, memory capacity, link loss, generation rate, swap success, request arrival rate, fidelity threshold, distance, classical latency.

Estimate ∂Y/∂x numerically. Compare sign and magnitude between simulators.

---

## Part 16. Performance Benchmark

N_nodes = 2, 5, 10, 25, 50, 100, 250, 500, 1000 as feasible.

Record: wall time, CPU time, peak RAM, events/sec, simulated time / real time, startup overhead, serialization overhead.

Identify scaling laws: T(N) ∝ N^α, M(N) ∝ N^β.

---

## Part 17. Determinism and Reproducibility

Same seed × 20, then 20 independent seeds. Test global RNG control, component RNGs, event-order effects, multiprocessing RNG, thread safety.

---

## Part 18. Observability

Classify each observable as: PUBLIC_API, HOOK, MONKEY_PATCH, SOURCE_MODIFICATION, NOT_AVAILABLE.

---

## Part 19. Action Injection

Determine whether an external WestQuant controller can dynamically modify: route, memory allocation, swap order, purification decision, admission decision, priority, reservation, cutoff time, generation scheduling, repeater policy.

---

## Part 20. Adapter Complexity Score

0 = trivial mapping, 1 = direct API, 2 = small wrapper, 3 = custom backend component, 4 = invasive integration, 5 = scientifically unsafe/impossible.

---

## Part 21. WestQuant Common Denominator

- **Level 1: WQ-Core-Network** — Capabilities reliably representable across all four simulators.
- **Level 2: WQ-Extended-Network** — Capabilities available on several, but not all, backends.
- **Level 3: Backend-native extensions** — `westquant.backend.netsquid...`, etc.

---

## Part 22. Capability Discovery API

```python
backend.capabilities()
backend.supports(feature)
backend.explain(feature)
```

---

## Part 23. Translation Report

Every execution must produce a translation report documenting EXACT, APPROXIMATED, IGNORED, UNSUPPORTED, BACKEND_NATIVE for every parameter.

---

## Part 24. Semantic Hashing

Canonical WestQuant experiment serialization with: `experiment_hash`, `semantic_model_hash`, `backend_translation_hash`.

---

## Part 25. WestQuant Normalized Result

`WQNetworkResult` with: backend, backend_version, experiment_id, seed, topology, simulation_time, wall_time, requested_pairs, generated_pairs, delivered_pairs, qualified_pairs, raw_rate, goodput, latency_mean/p50/p95/p99, fidelity_mean/std/quantiles, generation_attempts, swap_attempts, swap_successes, purification_attempts, memory_occupancy_mean/peak, mean_pair_age, expired_pairs, route_length_mean, reroutes, blocked_requests, fairness, deadline_misses, event_count, peak_memory_mb, cpu_seconds.

Metrics unavailable in a simulator must be `NULL + reason`, not silently zero.

---

## Part 26. Metric Definitions

Every metric must have a formal definition. E.g.:

- Qualified goodput: G_F = N_delivered(F ≥ F_min) / T_obs
- Deadline-qualified goodput: G_{F,D} = N(F ≥ F_min, L ≤ D) / T_obs

---

## Part 27. WestQuant Network Trace

Common trace format: timestamp, backend, node, component, event_type, request_id, pair_id, memory_id, link_id, route_id, fidelity, age, state, action, metadata.

---

## Part 28. Dataset Generation for AI

Export: state_t, action_t, reward_t, state_t+1, done, constraints, backend, experiment, seed.

AI tasks: AI-A routing, AI-B memory scheduling, AI-C joint representation scheduling.

---

## Part 29. Oracle Generation

For small networks (N = 3–6), enumerate feasible routes × memory assignments × swap schedules × purification choices × scheduling policies. Generate optimal labels a* = argmax_a U(s,a).

---

## Part 30. Backend Stress Tests

Test: T2=0, T2→∞, capacity=0, loss=1, loss=0, generation rate=0, generation rate extremely high, swap success=0, swap success=1, zero classical delay, very large classical delay, disconnected graph, single-node graph.

---

## Part 31. Software Quality Tests

API stability, documentation quality, examples, test coverage, type annotations, exception handling, extension patterns, release cadence, backwards compatibility, issue responsiveness, code modularity.

---

## Part 32. Required Final Reports

01_SIMULATOR_AUDIT.md, 02_FEATURE_MATRIX.csv, 03_MODEL_EQUIVALENCE_MATRIX.csv, 04_MEMORY_BENCHMARK.md, 05_REPEATER_BENCHMARK.md, 06_ROUTING_BENCHMARK.md, 07_PERFORMANCE_BENCHMARK.md, 08_REPRODUCIBILITY_REPORT.md, 09_CROSS_SIMULATOR_INVARIANCE.md, 10_ADAPTER_COMPLEXITY.md, 11_WESTQUANT_NETWORK_IR_SPEC.md, 12_WESTQUANT_CAPABILITY_API.md, 13_TRANSLATION_REPORT_SPEC.md, 14_NORMALIZED_RESULT_SPEC.md, 15_DATASET_SCHEMA.md, 16_IMPLEMENTATION_ROADMAP.md.

---

## Part 33. Required Figures

1. Simulator abstraction-layer map
2. Capability heatmap
3. WestQuant common API vs backend-specific capabilities
4. Cross-simulator metric agreement
5. Cross-simulator policy ranking agreement
6. Runtime vs number of nodes
7. RAM vs number of nodes
8. Memory T2 sensitivity
9. Routing-policy performance
10. Repeater-chain scaling
11. Translation-loss heatmap
12. Proposed WestQuant adapter architecture

---

## Part 34. Adapter Architecture

```
westquant-network
│
├── ir
│   ├── network
│   ├── node
│   ├── link
│   ├── memory
│   ├── repeater
│   ├── request
│   └── protocol
│
├── policies
│   ├── routing
│   ├── memory
│   ├── swapping
│   ├── purification
│   └── admission
│
├── metrics
├── trace
├── datasets
├── benchmark
├── validation
│
└── adapters
    ├── sequence
    ├── netsquid
    ├── simqn
    └── qoala
```

---

## Part 35. Scientific Pass/Fail Gates

A WestQuant abstraction may enter the stable common API only if:
- Gate A: Maps meaningfully to all four backends
- Gate B: Semantics can be formally defined
- Gate C: Unsupported parameters can be detected
- Gate D: Results can be normalized without scientifically misleading transformations
- Gate E: At least one golden experiment validates the mapping
- Gate F: Seed/reproduction behaviour is understood

---

## Part 36. Engineering Pass/Fail Gates

A backend adapter is ready for alpha release when: ≥95% unit-test pass, all golden tests run, capability discovery works, TranslationReport works, version detection works, invalid inputs fail safely, normalized results validate, seed handling documented, CI installation works where licensing permits.

---

## Part 37. Key Research Question

> To what extent are scientific conclusions about quantum-network performance invariant to simulator choice?

---

## Part 38. Strategic Question

For every backend, answer: What can WestQuant add that the simulator does not already provide?

---

## Part 39. Product Positioning

```python
from westquant.network import Experiment

exp = Experiment.from_yaml("experiment.yaml")

results = exp.compare(
    backends=["sequence", "netsquid", "simqn", "qoala"]
)
```

---

## Part 40. Execution Order

| Phase | Work |
|-------|------|
| A | Documentation/source-code audit |
| B | Minimal canonical IR |
| C | Installation and hello-world tests |
| D | Two-node physical tests |
| E | Memory validation |
| F | Three-node repeater validation |
| G | Routing/topology tests |
| H | Traffic/resource-management tests |
| I | Cross-simulator golden benchmarks |
| J | Performance/scaling |
| K | Capability/translation API |
| L | Dataset and AI hooks |
| M | Final WestQuant architecture |

**Do not build large amounts of adapter code until Phases A–F identify which semantic mappings are scientifically legitimate.**

---

## Final Required Output

A matrix of WestQuant function × simulator with CORE/EXTENDED/BACKEND_SPECIFIC/REJECT classification.

The primary success criterion is:

> A user should gain something substantial by installing WestQuant on top of ANY ONE of the four simulators, while a user with several simulators should gain an even larger benefit from common experiments, comparison, optimization, validation and provenance.

The secondary success criterion is scientific:

> WestQuant must make simulator assumptions more visible rather than hiding them.

The third success criterion is strategic:

> WestQuant should provide the layer that currently sits between quantum-network simulators: a common representation, common experiment specification, common measurement system, cross-simulator validation framework and optimization/AI interface.
