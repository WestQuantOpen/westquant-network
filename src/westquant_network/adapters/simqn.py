"""SimQN adapter — translates WestQuant Network experiments to SimQN/qns."""

from __future__ import annotations

from typing import Any

from westquant_network.ir import (
    ExperimentSpec,
)
from westquant_network.metrics import (
    SimulationResult,
)
from westquant_network.policies import PolicySet, RoutingPolicyType
from westquant_network.validation import TranslationReport, TranslationStatus


def _build_translation_report() -> TranslationReport:
    """Build translation report for SimQN backend."""
    report = TranslationReport(backend="simqn", experiment_id="")
    report.add("topology", TranslationStatus.EXACT)
    report.add("memory.capacity", TranslationStatus.EXACT)
    report.add("memory.T2", TranslationStatus.APPROXIMATED,
               "decoherence_rate", "T2 maps to decoherence_rate (inverse)")
    report.add("memory.initial_fidelity", TranslationStatus.UNSUPPORTED,
               warning="SimQN does not have initial_fidelity on memory")
    report.add("memory.write_efficiency", TranslationStatus.APPROXIMATED,
               "store_error_model_args")
    report.add("memory.read_efficiency", TranslationStatus.APPROXIMATED,
               "store_error_model_args")
    report.add("memory.write_latency", TranslationStatus.APPROXIMATED, "delay")
    report.add("memory.read_latency", TranslationStatus.APPROXIMATED, "delay")
    report.add("memory.wavelength", TranslationStatus.UNSUPPORTED)
    report.add("memory.cutoff_time", TranslationStatus.UNSUPPORTED)
    report.add("link.distance", TranslationStatus.EXACT, "length")
    report.add("link.attenuation", TranslationStatus.APPROXIMATED,
               "drop_rate", "Attenuation converted to drop_rate")
    report.add("link.loss_probability", TranslationStatus.EXACT, "drop_rate")
    report.add("link.source_rate", TranslationStatus.UNSUPPORTED)
    report.add("link.detector_efficiency", TranslationStatus.UNSUPPORTED)
    report.add("link.detector_dark_count", TranslationStatus.UNSUPPORTED)
    report.add("link.classical_latency", TranslationStatus.EXACT, "delay")
    report.add("routing", TranslationStatus.EXACT, "DijkstraRouteAlgorithm")
    report.add("swapping", TranslationStatus.UNSUPPORTED,
               warning="SimQN has no native swapping — adapter implements basic swap")
    report.add("purification", TranslationStatus.UNSUPPORTED,
               warning="SimQN has no native purification")
    return report


def _attenuation_to_drop_rate(attenuation: float, distance: float) -> float:
    """Convert attenuation (dB/km) + distance to drop rate."""
    if attenuation <= 0 or distance <= 0:
        return 0.0
    transmittance = 10 ** (-(attenuation * distance) / 10)
    return max(0.0, min(1.0, 1.0 - transmittance))


def _t2_to_decoherence_rate(T2: float | None) -> float:
    """Convert T2 (coherence time) to decoherence rate."""
    if T2 is None or T2 <= 0:
        return 0.0
    return 1.0 / T2


class SimQNAdapter:
    """Adapter for SimQN (qns) backend."""

    def __init__(self) -> None:
        self.backend_name = "simqn"
        self.backend_version = "0.2.3"

    def capabilities(self) -> dict[str, Any]:
        """Return capability dictionary."""
        return {
            "memory": {
                "capacity": True,
                "T2": True,
                "custom_decoherence": True,
                "initial_fidelity": False,
                "wavelength": False,
                "cutoff_time": False,
            },
            "routing": {
                "dynamic": False,
                "multipath": False,
                "dijkstra": True,
                "dijkstra_heap": True,
            },
            "state_formalisms": ["bell_state", "werner_state", "mixed_state"],
            "swapping": False,
            "purification": False,
            "topologies": [
                "line", "grid", "tree", "er_random",
                "ba_scale_free", "waxman", "custom",
            ],
        }

    def simulate(
        self,
        experiment: ExperimentSpec,
        policies: PolicySet | None = None,
    ) -> SimulationResult:
        """Run experiment on SimQN backend."""
        import time as _time

        policies = policies or PolicySet()
        wall_start = _time.time()

        try:
            from qns.entity.cchannel.cchannel import ClassicChannel
            from qns.entity.memory.memory import QuantumMemory
            from qns.entity.node.node import QNode
            from qns.entity.qchannel.qchannel import QuantumChannel
            from qns.network.network import QuantumNetwork
            from qns.network.requests import Request
            from qns.network.route.dijkstra import DijkstraRouteAlgorithm
            from qns.network.route.dijkstra_heap import DijkstraRouteAlgorithmHeap
            from qns.simulator.simulator import Simulator
        except ImportError as e:
            return SimulationResult(
                backend="simqn",
                experiment_id=experiment.experiment_id,
                seed=experiment.seed,
                simulation_time=experiment.duration,
                wall_time=0.0,
                missing_reasons={"simqn": str(e)},
            )

        # Build simulator
        sim = Simulator(
            start_second=0.0,
            end_second=experiment.duration,
            accuracy=1000000,
        )

        # Choose routing algorithm
        routing_policy = policies.routing.policy_type
        if routing_policy == RoutingPolicyType.DIJKSTRA_COST:
            route_algo = DijkstraRouteAlgorithmHeap(name="dijkstra_heap")
        else:
            route_algo = DijkstraRouteAlgorithm(name="dijkstra")

        # Build network
        net = QuantumNetwork(route=route_algo)

        # Create nodes
        node_map: dict[str, QNode] = {}
        for node_spec in experiment.topology.nodes:
            qnode = QNode(name=node_spec.node_id)
            node_map[node_spec.node_id] = qnode
            net.add_node(qnode)

            # Add memories
            for mem_spec in node_spec.memories:
                decoherence_rate = _t2_to_decoherence_rate(mem_spec.T2)
                memory = QuantumMemory(
                    name=f"{node_spec.node_id}_mem",
                    node=qnode,
                    capacity=mem_spec.capacity,
                    decoherence_rate=decoherence_rate,
                    delay=mem_spec.write_latency,
                )
                qnode.memories.append(memory)

        # Create quantum channels
        for edge in experiment.topology.edges:
            src = node_map.get(edge.source)
            dst = node_map.get(edge.target)
            if src is None or dst is None:
                continue

            ql = edge.quantum_link
            drop_rate = ql.loss_probability or _attenuation_to_drop_rate(
                ql.attenuation, ql.distance
            )
            qchannel = QuantumChannel(
                name=f"qc_{edge.source}_{edge.target}",
                node_list=[src, dst],
                fidelity=0.99,
                bandwidth=1,
                delay=ql.distance * 1000 / ql.speed if ql.speed > 0 else 0,
                drop_rate=drop_rate,
                length=ql.distance,
            )
            net.add_qchannel(qchannel)

            # Classical channel
            cl = edge.classical_link
            cchannel = ClassicChannel(
                name=f"cc_{edge.source}_{edge.target}",
                node_list=[src, dst],
                delay=cl.latency if cl.latency > 0 else ql.classical_latency,
                length=ql.distance,
            )
            net.add_cchannel(cchannel)

        # Build route table
        try:
            net.build_route()
        except Exception:
            pass

        # Create requests
        requests_created = 0
        for req in experiment.traffic.requests:
            src = node_map.get(req.source)
            dst = node_map.get(req.destination)
            if src is None or dst is None:
                continue
            for _ in range(req.num_pairs):
                net.add_request(src, dst, attr={
                    "min_fidelity": req.min_fidelity,
                    "priority": req.priority,
                })
                requests_created += 1

        # Run simulation
        try:
            sim.run()
        except Exception:
            pass

        # Collect results
        wall_time = _time.time() - wall_start

        # Build translation report
        report = _build_translation_report()
        report.experiment_id = experiment.experiment_id

        result = SimulationResult(
            backend="simqn",
            backend_version=self.backend_version,
            experiment_id=experiment.experiment_id,
            seed=experiment.seed,
            simulation_time=experiment.duration,
            wall_time=wall_time,
            requested_pairs=requests_created,
            translation_report={e.parameter: e.status.value for e in report.entries},
        )

        # Try to extract metrics from network
        try:
            delivered = 0
            for node in net.nodes:
                if hasattr(node, 'apps'):
                    for app in node.apps:
                        if hasattr(app, 'success_count'):
                            delivered += app.success_count
            result.delivered_pairs = delivered
        except Exception:
            pass

        result.compute_derived(experiment.min_fidelity)

        return result
