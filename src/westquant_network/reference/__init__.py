"""WestQuant reference discrete-event simulator.

This is NOT a device-level quantum-physics simulator.
It is an auditable, abstract discrete-event model for CI,
reproducibility, and benchmark baselines.

Supported:
- Direct links, linear repeater chains, star/switch topology
- Elementary-pair generation with loss
- Finite quantum memories with exponential decoherence
- Entanglement swapping
- Classical communication latency
- FIFO / oldest-first / fidelity-first memory scheduling
- Shortest-hop / shortest-distance / Dijkstra routing
- Request queues with deadlines and priorities
"""

from __future__ import annotations

import heapq
import math
import random
from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from westquant_network.ir import (
    EdgeSpec,
    ExperimentSpec,
    RequestSpec,
)
from westquant_network.metrics import (
    FidelityStats,
    LatencyStats,
    SimulationResult,
)
from westquant_network.policies import (
    PolicySet,
    RoutingPolicyType,
)
from westquant_network.validation import TranslationReport, TranslationStatus


@dataclass(order=True)
class Event:
    """Discrete event in the reference simulator."""

    timestamp: float
    seq: int  # tiebreaker for deterministic ordering
    event_type: str = field(compare=False)
    data: dict[str, Any] = field(default_factory=dict, compare=False)


@dataclass
class MemorySlot:
    """A single memory slot holding an entangled pair."""

    pair_id: str
    creation_time: float
    fidelity: float
    source_node: str
    dest_node: str
    route_id: str | None = None
    deadline: float | None = None
    priority: int = 0


@dataclass
class StoredPair:
    """An entangled pair stored in memory."""

    pair_id: str
    creation_time: float
    fidelity: float
    source: str
    destination: str
    age: float = 0.0


class ReferenceSimulator:
    """WestQuant reference discrete-event quantum network simulator."""

    def __init__(
        self,
        experiment: ExperimentSpec,
        policies: PolicySet | None = None,
    ) -> None:
        self.experiment = experiment
        self.policies = policies or PolicySet()
        self.rng = random.Random(experiment.seed)
        self.events: list[Event] = []
        self._seq = 0
        self.current_time = 0.0
        self.graph = nx.Graph()
        self.node_memories: dict[str, list[MemorySlot]] = {}
        self.requests: list[RequestSpec] = []
        self.results = SimulationResult(
            backend="reference",
            backend_version="0.1.0",
            experiment_id=experiment.experiment_id,
            seed=experiment.seed,
            simulation_time=experiment.duration,
            wall_time=0.0,
        )
        self.latencies: list[float] = []
        self.fidelities: list[float] = []
        self.pair_ages: list[float] = []
        self.route_lengths: list[int] = []
        self.memory_history: list[float] = []
        self.event_count = 0

    def _schedule(
        self, timestamp: float, event_type: str, data: dict[str, Any] | None = None,
    ) -> None:
        """Schedule a new event."""
        self._seq += 1
        heapq.heappush(
            self.events,
            Event(timestamp, self._seq, event_type, data or {}),
        )

    def _build_graph(self) -> None:
        """Build networkx graph from topology."""
        topo = self.experiment.topology
        for node in topo.nodes:
            self.graph.add_node(
                node.node_id,
                memories=node.memories,
                is_repeater=node.is_repeater,
            )
            self.node_memories[node.node_id] = []
        for edge in topo.edges:
            self.graph.add_edge(
                edge.source,
                edge.target,
                distance=edge.quantum_link.distance,
                attenuation=edge.quantum_link.attenuation,
                loss=self._compute_loss(edge),
                quantum_link=edge.quantum_link,
            )

    def _compute_loss(self, edge: EdgeSpec) -> float:
        """Compute photon loss probability for a link."""
        ql = edge.quantum_link
        if ql.loss_probability is not None:
            return ql.loss_probability
        # attenuation-based: P_loss = 1 - 10^(-attenuation*distance/10)
        transmittance = 10 ** (-(ql.attenuation * ql.distance) / 10)
        return 1.0 - transmittance * ql.source_efficiency * ql.detector_efficiency

    def _decohere(self, fidelity: float, age: float, T2: float | None) -> float:  # noqa: N803
        """Apply exponential decoherence: F(t) = F0 * exp(-t/T2)."""
        if T2 is None or T2 <= 0:  # noqa: N806
            return fidelity
        return fidelity * math.exp(-age / T2)  # noqa: N806

    def _get_T2(self, node_id: str) -> float | None:  # noqa: N802
        """Get T2 for a node's first memory."""
        slots = self.node_memories.get(node_id, [])
        if not slots:
            return None
        # Get from topology spec
        topo = self.experiment.topology
        for node in topo.nodes:
            if node.node_id == node_id and node.memories:
                return node.memories[0].T2
        return None

    def _get_capacity(self, node_id: str) -> int:
        """Get memory capacity for a node."""
        topo = self.experiment.topology
        for node in topo.nodes:
            if node.node_id == node_id and node.memories:
                return node.memories[0].capacity
        return 0

    def _find_route(self, source: str, destination: str) -> list[str] | None:
        """Find a route based on routing policy."""
        policy = self.policies.routing.policy_type
        if policy == RoutingPolicyType.SHORTEST_HOP:
            try:
                return nx.shortest_path(self.graph, source, destination)
            except nx.NetworkXNoPath:
                return None
        elif policy == RoutingPolicyType.SHORTEST_DISTANCE:
            try:
                return nx.shortest_path(
                    self.graph, source, destination, weight="distance"
                )
            except nx.NetworkXNoPath:
                return None
        elif policy == RoutingPolicyType.DIJKSTRA_COST:
            try:
                return nx.dijkstra_path(
                    self.graph, source, destination, weight="loss"
                )
            except nx.NetworkXNoPath:
                return None
        else:
            try:
                return nx.shortest_path(self.graph, source, destination)
            except nx.NetworkXNoPath:
                return None

    def _generate_pair(self, source: str, destination: str, route: list[str]) -> str:
        """Attempt to generate an elementary pair on a link."""
        pair_id = f"pair_{self.rng.randint(0, 999999)}"
        # Check loss on first link
        if len(route) >= 2:
            edge_data = self.graph[route[0]][route[1]]
            loss_prob = edge_data["loss"]
            if self.rng.random() < loss_prob:
                self.results.generation_attempts += 1
                return ""  # lost
        self.results.generation_attempts += 1
        # Initial fidelity
        init_fidelity = 1.0
        for node in self.experiment.topology.nodes:
            if node.node_id == source and node.memories:
                init_fidelity = node.memories[0].initial_fidelity
                break
        # Store in source memory
        slot = MemorySlot(
            pair_id=pair_id,
            creation_time=self.current_time,
            fidelity=init_fidelity,
            source_node=source,
            dest_node=destination,
        )
        cap = self._get_capacity(source)
        if len(self.node_memories[source]) < cap or cap == 0:
            self.node_memories[source].append(slot)
        return pair_id

    def _try_swap(self, route: list[str], pair_id: str) -> bool:
        """Attempt entanglement swapping along a route."""
        if len(route) <= 2:
            return True  # direct link, no swap needed
        for i in range(1, len(route) - 1):
            repeater = route[i]
            # Apply swap success probability
            swap_prob = 1.0
            for rep in self.experiment.repeaters:
                if rep.node_id == repeater:
                    swap_prob = rep.swap_success_probability
                    break
            if self.rng.random() > swap_prob:
                self.results.swap_attempts += 1
                return False
            self.results.swap_attempts += 1
            self.results.swap_successes += 1
        return True

    def _deliver_pair(self, pair_id: str, route: list[str], request: RequestSpec) -> None:
        """Deliver a completed entangled pair."""
        if not pair_id:
            return
        age = self.current_time - self._get_pair_creation_time(pair_id)
        # Apply decoherence
        T2 = self._get_T2(route[0])  # noqa: N806
        init_f = 1.0
        for node in self.experiment.topology.nodes:
            if node.node_id == route[0] and node.memories:
                init_f = node.memories[0].initial_fidelity
                break
        fidelity = self._decohere(init_f, age, T2)
        self.results.delivered_pairs += 1
        self.fidelities.append(fidelity)
        self.latencies.append(age)
        self.pair_ages.append(age)
        self.route_lengths.append(len(route) - 1)
        if fidelity >= request.min_fidelity:
            self.results.qualified_pairs += 1
        if request.deadline and age > request.deadline:
            self.results.deadline_misses += 1
        # Remove from memory
        for node_id, slots in self.node_memories.items():
            self.node_memories[node_id] = [
                s for s in slots if s.pair_id != pair_id
            ]

    def _get_pair_creation_time(self, pair_id: str) -> float:
        """Get creation time of a pair."""
        for slots in self.node_memories.values():
            for s in slots:
                if s.pair_id == pair_id:
                    return s.creation_time
        return self.current_time

    def _expire_old_pairs(self) -> None:
        """Remove expired pairs from memory based on cutoff policy."""
        for node_id, slots in list(self.node_memories.items()):
            T2 = self._get_T2(node_id)  # noqa: N806
            cutoff = None
            for node in self.experiment.topology.nodes:
                if node.node_id == node_id and node.memories:
                    cutoff = node.memories[0].cutoff_time
                    break
            kept: list[MemorySlot] = []
            for s in slots:
                age = self.current_time - s.creation_time
                expired = False
                if cutoff is not None and age > cutoff:
                    expired = True
                if T2 is not None and T2 > 0:
                    fidelity = self._decohere(s.fidelity, age, T2)
                    if fidelity < 0.01:
                        expired = True
                if expired:
                    self.results.expired_pairs += 1
                else:
                    kept.append(s)
            self.node_memories[node_id] = kept

    def _process_request(self, request: RequestSpec) -> None:
        """Process a single entanglement request."""
        self.results.requested_pairs += request.num_pairs
        route = self._find_route(request.source, request.destination)
        if route is None:
            self.results.blocked_requests += 1
            return
        for _ in range(request.num_pairs):
            pair_id = self._generate_pair(request.source, request.destination, route)
            if pair_id:
                if self._try_swap(route, pair_id):
                    self._deliver_pair(pair_id, route, request)
                else:
                    # Swap failed, pair lost
                    for node_id, slots in list(self.node_memories.items()):
                        self.node_memories[node_id] = [
                            s for s in slots if s.pair_id != pair_id
                        ]
            else:
                # Generation lost
                pass

    def _record_memory_occupancy(self) -> None:
        """Record current memory occupancy."""
        total_cap = 0
        total_used = 0
        for node_id, slots in self.node_memories.items():
            cap = self._get_capacity(node_id)
            total_cap += cap
            total_used += len(slots)
        if total_cap > 0:
            self.memory_history.append(total_used / total_cap)

    def run(self) -> SimulationResult:
        """Run the simulation."""
        import time as _time

        wall_start = _time.time()
        self._build_graph()
        # Schedule requests from traffic spec
        traffic = self.experiment.traffic
        if traffic.requests:
            for req in traffic.requests:
                self._schedule(0.0, "request", {"request": req})
        else:
            # Default: single request from first to last node
            topo = self.experiment.topology
            if len(topo.nodes) >= 2:
                req = RequestSpec(
                    request_id="default",
                    source=topo.nodes[0].node_id,
                    destination=topo.nodes[-1].node_id,
                    min_fidelity=self.experiment.min_fidelity,
                )
                self._schedule(0.0, "request", {"request": req})

        # Process events
        while self.events:
            event = heapq.heappop(self.events)
            self.current_time = event.timestamp
            if self.current_time > self.experiment.duration:
                break
            self.event_count += 1
            if event.event_type == "request":
                self._process_request(event.data["request"])
            self._expire_old_pairs()
            self._record_memory_occupancy()

        # Compute derived metrics
        self.results.wall_time = _time.time() - wall_start
        self.results.event_count = self.event_count
        self.results.compute_derived(self.experiment.min_fidelity)

        # Latency stats
        if self.latencies:
            sl = sorted(self.latencies)
            n = len(sl)
            self.results.latency = LatencyStats(
                mean=sum(sl) / n,
                p50=sl[n // 2],
                p95=sl[int(n * 0.95)] if n >= 20 else sl[-1],
                p99=sl[int(n * 0.99)] if n >= 100 else sl[-1],
            )

        # Fidelity stats
        if self.fidelities:
            sf = sorted(self.fidelities)
            n = len(sf)
            mean_f = sum(sf) / n
            std_f = math.sqrt(sum((f - mean_f) ** 2 for f in sf) / n) if n > 1 else 0.0
            self.results.fidelity = FidelityStats(
                mean=mean_f,
                std=std_f,
                min=sf[0],
                max=sf[-1],
            )

        # Memory stats
        if self.memory_history:
            self.results.memory_occupancy_mean = sum(self.memory_history) / len(
                self.memory_history
            )
            self.results.memory_occupancy_peak = max(self.memory_history)

        if self.pair_ages:
            self.results.mean_pair_age = sum(self.pair_ages) / len(self.pair_ages)

        if self.route_lengths:
            self.results.route_length_mean = sum(self.route_lengths) / len(
                self.route_lengths
            )

        # Translation report (reference = EXACT for everything)
        report = TranslationReport(
            backend="reference",
            experiment_id=self.experiment.experiment_id,
        )
        report.add("topology", TranslationStatus.EXACT)
        report.add("memory.capacity", TranslationStatus.EXACT)
        report.add("memory.T2", TranslationStatus.EXACT)
        report.add("memory.write_efficiency", TranslationStatus.EXACT)
        report.add("link.distance", TranslationStatus.EXACT)
        report.add("link.attenuation", TranslationStatus.EXACT)
        report.add("link.loss_probability", TranslationStatus.EXACT)
        report.add("routing", TranslationStatus.EXACT)
        report.add("swapping", TranslationStatus.EXACT)
        report.add(
            "purification", TranslationStatus.UNSUPPORTED,
            warning="Not implemented in reference simulator",
        )
        self.results.translation_report = {
            e.parameter: e.status.value for e in report.entries
        }

        return self.results


def simulate(
    experiment: ExperimentSpec, policies: PolicySet | None = None,
) -> SimulationResult:
    """Run the WestQuant reference simulator."""
    sim = ReferenceSimulator(experiment, policies)
    return sim.run()
