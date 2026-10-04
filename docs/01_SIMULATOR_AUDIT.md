# 01_SIMULATOR_AUDIT.md

**WestQuant Network — Simulator Audit**
**Phase A — SeQUeNCe and SimQN**

---

## 1A. Installation and Packaging

### SeQUeNCe 0.8.0

| Attribute | Value |
|-----------|-------|
| PyPI name | `sequence` |
| Version | 0.8.0 |
| Python | 3.7+ (tested on 3.10) |
| OS | Linux, macOS |
| Native deps | QuTiP, Dash, JupyterLab |
| License | BSD-3-Clause |
| `installation_complexity` | MEDIUM (heavy deps: QuTiP) |
| `CI_friendly` | YES |
| `redistribution_constraints` | None (BSD-3) |

```bash
pip install sequence
```

### SimQN 0.2.3

| Attribute | Value |
|-----------|-------|
| PyPI name | `qns` |
| Version | 0.2.3 |
| Python | 3.7+ (tested on 3.10) |
| OS | Linux, macOS |
| Native deps | numpy, pandas |
| License | GPLv3 |
| `installation_complexity` | LOW |
| `CI_friendly` | YES |
| `redistribution_constraints` | GPLv3 — WestQuant adapter must be GPL-compatible or separate |

```bash
pip install qns
```

---

## 1B. Simulation Kernel

### SeQUeNCe

| Attribute | Value |
|-----------|-------|
| Type | Discrete-event |
| Event queue | `EventList` (sorted list) |
| Timestamp precision | picoseconds (integer) |
| Deterministic ordering | Yes (sequence counter) |
| Cancellation | `remove_event` |
| Priorities | Yes (via event ordering) |
| Callbacks | Yes (process-based) |
| Async model | Yes (process/coroutine) |
| Clock semantics | Picosecond integer timeline |
| Pause/resume | `stop()` |
| Inspect queue | `events` property |
| Inject events | `schedule()` |
| Hooks | `add_entity` / entity callbacks |
| Event trace | Available via log |

**WestQuant can obtain:** event_id, timestamp, node, component, protocol, action via entity callbacks and log hooks.

### SimQN

| Attribute | Value |
|-----------|-------|
| Type | Discrete-event |
| Event queue | `DefaultEventPool` (heap-based) or `StablePool` / `HashBucketPool` |
| Timestamp precision | microsecond (configurable accuracy) |
| Deterministic ordering | Yes (via pool) |
| Cancellation | Yes (event removal) |
| Priorities | Yes (event ordering) |
| Callbacks | Yes (event `invoke`) |
| Async model | Yes (process-based) |
| Clock semantics | Time in seconds (float) |
| Pause/resume | No native pause |
| Inspect queue | Via pool |
| Inject events | `add_event()` |
| Hooks | Event subclassing |
| Event trace | Via log |

**WestQuant can obtain:** event_id, timestamp, node, component via event subclassing and log hooks.

---

## 2. Quantum State and Physical Model

### 2.1 State Representation

| Feature | SeQUeNCe | SimQN |
|---------|----------|-------|
| Pure state vectors | ✅ `ket_vector` | ✅ `Qubit` / `QState` |
| Density matrices | ✅ `density_matrix` | ✅ (via QState) |
| Stabilizer states | ❌ | ❌ |
| Bell-pair abstractions | ✅ `bell_diagonal` | ✅ `BellStateEntanglement` |
| Fidelity-only abstractions | ✅ (via bell_diagonal) | ✅ `WernerStateEntanglement` |
| User-defined state formalism | ✅ (register API) | ✅ (subclass) |
| Arbitrary qubit state | ✅ | ✅ |
| Multi-qubit state | ✅ | ✅ |
| Mixed state | ✅ `fock_density` | ✅ `MixedStateEntanglement` |
| Entangled multipartite | ✅ | ✅ |

**SeQUeNCe formalisms:** `ket_vector`, `density_matrix`, `fock_density`, `bell_diagonal`
**SimQN formalisms:** `BellStateEntanglement`, `WernerStateEntanglement`, `MixedStateEntanglement`

### 2.2 Noise

| Noise source | SeQUeNCe | SimQN |
|--------------|----------|-------|
| Depolarization | ✅ configurable | ✅ `DepolarStorage/Transfer/Operate/MeasureErrorModel` |
| Dephasing | ✅ configurable | ✅ `DephaseStorage/Transfer/Operate/MeasureErrorModel` |
| Amplitude damping | ✅ (via decoherence_errors) | ❌ |
| T1 | ✅ `coherence_time` | ✅ `decoherence_rate` |
| T2 | ✅ `coherence_time` | ✅ `decoherence_rate` |
| Channel losses | ✅ `attenuation` | ✅ `drop_rate` |
| Operation error | ✅ `decoherence_errors` | ✅ `DepolarOperateErrorModel` |
| Measurement error | ✅ | ✅ `DepolarMeasureErrorModel` |
| Detector dark counts | ✅ `dark_count` (detector) | ❌ |
| Detector efficiency | ✅ `efficiency` (detector) | ❌ |
| Photon loss | ✅ `attenuation` | ✅ `drop_rate` |
| Memory decoherence | ✅ time-dependent | ✅ `decoherence_rate` |
| Imperfect BSM | ✅ | ✅ (via error models) |
| Imperfect entanglement gen | ✅ | ✅ |

**Key difference:** SeQUeNCe models detector dark counts and efficiency explicitly. SimQN abstracts these into `drop_rate`.

---

## 3. Memory

### SeQUeNCe Memory

```python
Memory(name, timeline, fidelity, frequency, efficiency, coherence_time,
       wavelength, decoherence_errors=None, cutoff_ratio=1)
```

| WQMemorySpec param | SeQUeNCe | Translation |
|--------------------|----------|-------------|
| capacity | Not native (multiple Memory objects) | APPROXIMATED |
| T1 | `coherence_time` | EXACT |
| T2 | `coherence_time` | SEMANTICALLY_EQUIVALENT |
| initial_fidelity | `fidelity` / `raw_fidelity` | EXACT |
| write_efficiency | `efficiency` | SEMANTICALLY_EQUIVALENT |
| read_efficiency | `efficiency` | SEMANTICALLY_EQUIVALENT |
| write_latency | `1/frequency` | APPROXIMATED |
| read_latency | `1/frequency` | APPROXIMATED |
| operation_fidelity | `decoherence_errors` | APPROXIMATED |
| bandwidth | `frequency` | APPROXIMATED |
| wavelength | `wavelength` | EXACT |
| cutoff_time | `coherence_time * cutoff_ratio` | EXACT |
| decoherence_model | exponential (coherence_time) | BACKEND_NATIVE |

### SimQN Memory

```python
QuantumMemory(name, node, capacity, decoherence_rate, store_error_model_args, delay)
```

| WQMemorySpec param | SimQN | Translation |
|--------------------|-------|-------------|
| capacity | `capacity` | EXACT |
| T1 | `decoherence_rate` | APPROXIMATED |
| T2 | `decoherence_rate` | APPROXIMATED |
| initial_fidelity | Not native | UNSUPPORTED |
| write_efficiency | `store_error_model_args` | APPROXIMATED |
| read_efficiency | `store_error_model_args` | APPROXIMATED |
| write_latency | `delay` | APPROXIMATED |
| read_latency | `delay` | APPROXIMATED |
| operation_fidelity | error models | APPROXIMATED |
| bandwidth | Not native | UNSUPPORTED |
| wavelength | Not native | UNSUPPORTED |
| cutoff_time | Not native | UNSUPPORTED |
| decoherence_model | `decoherence_rate` (exponential) | BACKEND_NATIVE |

---

## 4. Links

### SeQUeNCe

```python
QuantumChannel(name, timeline, attenuation, distance, polarization_fidelity, light_speed, frequency)
ClassicalChannel(name, timeline, distance, delay)
```

### SimQN

```python
QuantumChannel(name, node_list, fidelity, bandwidth, delay, drop_rate, length, decoherence_rate)
ClassicChannel(name, node_list, bandwidth, delay, length, drop_rate)
```

| WQQuantumLinkSpec param | SeQUeNCe | SimQN |
|------------------------|----------|-------|
| distance | ✅ `distance` | ✅ `length` |
| attenuation | ✅ `attenuation` | ❌ (use `drop_rate`) |
| loss_probability | ✅ (computed) | ✅ `drop_rate` |
| source_rate | ✅ `frequency` | ❌ |
| source_efficiency | ✅ (memory efficiency) | ❌ |
| detector_efficiency | ✅ (detector) | ❌ |
| detector_dark_count | ✅ (detector) | ❌ |
| wavelength | ✅ (memory) | ❌ |
| classical_latency | ✅ `delay` | ✅ `delay` |
| quantum_latency | ✅ (computed from distance/speed) | ✅ `delay` |

---

## 5. Routing

### SeQUeNCe

- `StaticRoutingProtocol` — static routing table
- `NetworkManager` — manages reservations and routing
- Custom routing via protocol subclassing

### SimQN

- `DijkstraRouteAlgorithm` — standard Dijkstra
- `DijkstraRouteAlgorithmHeap` — heap-based Dijkstra (faster for large networks)
- `QuantumNetwork.build_route()` / `query_route()` / `shortest_path()`

| WQRoutingPolicy | SeQUeNCe | SimQN |
|-----------------|----------|-------|
| SHORTEST_HOP | ✅ (custom) | ✅ Dijkstra |
| SHORTEST_DISTANCE | ✅ (custom) | ✅ Dijkstra |
| DIJKSTRA_COST | ✅ (custom) | ✅ Dijkstra |
| K_SHORTEST | ❌ | ❌ (custom needed) |
| LOSS_AWARE | ❌ (custom) | ❌ (custom) |
| FIDELITY_AWARE | ❌ (custom) | ❌ (custom) |
| MEMORY_AWARE | ❌ (custom) | ❌ (custom) |
| MULTIPATH | ❌ | ❌ |

---

## 6. Entanglement Generation and Swapping

### SeQUeNCe

- `entanglement_management/generation/` — BB84, Micius, etc.
- `entanglement_management/swapping/` — swapping protocols
- `entanglement_management/purification/` — purification protocols
- `components/bsm.py` — Bell-state measurement

### SimQN

- `network/protocol/entanglement_distribution.py` — entanglement distribution
- No native swapping protocol (must be implemented as Application)
- No native purification (must be implemented as Application)

---

## 7. Topologies

| Topology | SeQUeNCe | SimQN |
|----------|----------|-------|
| LINE | ✅ (custom) | ✅ `LineTopo` |
| RING | ✅ (custom) | ✅ (custom) |
| STAR | ✅ `QLanStarTopo` | ✅ (custom) |
| TREE | ✅ (custom) | ✅ `TreeTopo` |
| GRID | ✅ (custom) | ✅ `GridTopo` |
| MESH | ✅ (custom) | ✅ (custom) |
| ER_RANDOM | ✅ (custom) | ✅ `ErdosRenyiTopo` |
| BA_SCALE_FREE | ✅ (custom) | ✅ `BarabasiAlbertTopo` |
| WAXMAN | ❌ | ✅ `WaxmanTopo` |
| CUSTOM | ✅ | ✅ `RealTopo` |

---

## 8. Observability

| Observable | SeQUeNCe | SimQN |
|------------|----------|-------|
| network_state | ✅ (NetworkManager) | ✅ (QuantumNetwork) |
| link_state | ✅ (QuantumChannel) | ✅ (QuantumChannel) |
| memory_state | ✅ (MemoryManager) | ✅ (QuantumMemory) |
| pair_age | ✅ (timeline) | ✅ (Time) |
| pair_fidelity | ✅ (Memory.fidelity) | ✅ (EPR fidelity) |
| routing_table | ✅ (StaticRoutingProtocol) | ✅ (RouteImpl) |
| request_queues | ✅ (NetworkManager) | ✅ (Request) |
| event_history | ✅ (log) | ✅ (log) |

---

## 9. Action Injection

| Action | SeQUeNCe | SimQN |
|--------|----------|-------|
| route | ✅ (StaticRoutingProtocol) | ✅ (RouteImpl) |
| memory_allocation | ✅ (MemoryManager) | ✅ (QuantumMemory) |
| swap_order | ✅ (protocol) | ❌ (custom) |
| purification_decision | ✅ (protocol) | ❌ (custom) |
| admission_decision | ✅ (NetworkManager) | ✅ (Request) |
| priority | ✅ (reservation) | ✅ (Request attr) |

---

## 10. Adapter Complexity Score

| Capability | SeQUeNCe | SimQN |
|------------|----------|-------|
| Topology | 2 | 1 |
| Memory | 2 | 1 |
| Link | 2 | 1 |
| Routing | 2 | 1 |
| Scheduling | 3 | 3 |
| Repeaters | 2 | 4 |
| Purification | 2 | 4 |
| Trace export | 2 | 2 |
| Dynamic actions | 3 | 3 |

**Scores ≥3 explained:**
- SeQUeNCe scheduling (3): RuleManager requires understanding of rule/action/condition system
- SimQN scheduling (3): No native scheduler — must implement as Application
- SimQN repeaters (4): No native swapping — must implement full protocol
- SimQN purification (4): No native purification — must implement full protocol
- Both dynamic actions (3): Requires protocol-level injection during simulation

---

## Summary

| Dimension | SeQUeNCe | SimQN |
|-----------|----------|-------|
| State formalisms | 4 (ket, density, fock, bell_diagonal) | 3 (bell, werner, mixed) |
| Noise models | Rich (detector, dark count, T1/T2) | Good (depolar/dephase error models) |
| Memory | T1/T2, fidelity, efficiency, wavelength | capacity, decoherence_rate, delay |
| Routing | Static (custom needed for advanced) | Dijkstra (heap-based available) |
| Swapping | ✅ Native | ❌ Must implement |
| Purification | ✅ Native | ❌ Must implement |
| Topologies | Custom needed | Pre-built (line, grid, BA, ER, WAXMAN) |
| Scale | Medium | Large (heap scheduler) |
| License | BSD-3 (permissive) | GPLv3 (copyleft) |

**Recommended first adapter:** SimQN (simpler API, pre-built topologies, Dijkstra routing)
**Recommended second adapter:** SeQUeNCe (richer physics, native swapping/purification)
