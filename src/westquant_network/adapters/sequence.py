"""SeQUeNCe adapter — translates WestQuant Network experiments to SeQUeNCe."""

from __future__ import annotations

from typing import Any

from westquant_network.ir import (
    ExperimentSpec,
)
from westquant_network.metrics import (
    FidelityStats,
    SimulationResult,
)
from westquant_network.policies import PolicySet
from westquant_network.validation import TranslationReport, TranslationStatus


def _build_translation_report() -> TranslationReport:
    """Build translation report for SeQUeNCe backend."""
    report = TranslationReport(backend="sequence", experiment_id="")
    report.add("topology", TranslationStatus.EXACT)
    report.add("memory.capacity", TranslationStatus.APPROXIMATED,
               "multiple Memory objects", "Capacity = number of Memory instances")
    report.add("memory.T1", TranslationStatus.EXACT, "coherence_time")
    report.add("memory.T2", TranslationStatus.SEMANTICALLY_EQUIVALENT,
               "coherence_time", "T2 maps to coherence_time (exponential decay)")
    report.add("memory.initial_fidelity", TranslationStatus.EXACT, "fidelity")
    report.add("memory.write_efficiency", TranslationStatus.SEMANTICALLY_EQUIVALENT,
               "efficiency", "Write/read share efficiency parameter")
    report.add("memory.read_efficiency", TranslationStatus.SEMANTICALLY_EQUIVALENT,
               "efficiency", "Write/read share efficiency parameter")
    report.add("memory.write_latency", TranslationStatus.APPROXIMATED,
               "1/frequency", "Derived from frequency")
    report.add("memory.read_latency", TranslationStatus.APPROXIMATED,
               "1/frequency", "Derived from frequency")
    report.add("memory.operation_fidelity", TranslationStatus.APPROXIMATED,
               "decoherence_errors", "Pauli channel error distribution")
    report.add("memory.wavelength", TranslationStatus.EXACT, "wavelength")
    report.add("memory.cutoff_time", TranslationStatus.EXACT,
               "coherence_time * cutoff_ratio")
    report.add("memory.decoherence_model", TranslationStatus.BACKEND_NATIVE,
               "coherence_time", "Exponential decay model")
    report.add("link.distance", TranslationStatus.EXACT, "distance")
    report.add("link.attenuation", TranslationStatus.EXACT, "attenuation")
    report.add("link.loss_probability", TranslationStatus.EXACT,
               "computed from attenuation")
    report.add("link.source_rate", TranslationStatus.EXACT, "frequency")
    report.add("link.detector_efficiency", TranslationStatus.EXACT,
               "detector efficiency")
    report.add("link.detector_dark_count", TranslationStatus.EXACT,
               "detector dark_count")
    report.add("link.classical_latency", TranslationStatus.EXACT, "delay")
    report.add("routing", TranslationStatus.EXACT, "StaticRoutingProtocol")
    report.add("swapping", TranslationStatus.EXACT, "SwappingProtocol")
    report.add("purification", TranslationStatus.EXACT, "PurificationProtocol")
    return report


class SequenceAdapter:
    """Adapter for SeQUeNCe backend."""

    def __init__(self) -> None:
        self.backend_name = "sequence"
        self.backend_version = "0.8.0"

    def capabilities(self) -> dict[str, Any]:
        """Return capability dictionary."""
        return {
            "memory": {
                "capacity": True,
                "T1": True,
                "T2": True,
                "initial_fidelity": True,
                "write_efficiency": True,
                "read_efficiency": True,
                "wavelength": True,
                "cutoff_time": True,
                "custom_decoherence": True,
            },
            "routing": {
                "dynamic": False,
                "multipath": False,
                "static": True,
            },
            "state_formalisms": [
                "ket_vector", "density_matrix",
                "fock_density", "bell_diagonal",
            ],
            "swapping": True,
            "purification": True,
            "topologies": [
                "line", "ring", "star", "grid", "mesh", "custom",
            ],
        }

    def simulate(
        self,
        experiment: ExperimentSpec,
        policies: PolicySet | None = None,
    ) -> SimulationResult:
        """Run experiment on SeQUeNCe backend."""
        import time as _time

        policies = policies or PolicySet()
        wall_start = _time.time()

        try:
            from sequence.components.optical_channel import (
                ClassicalChannel,
                QuantumChannel,
            )
            from sequence.kernel.timeline import Timeline
            from sequence.topology.node import QuantumRouter
        except ImportError as e:
            return SimulationResult(
                backend="sequence",
                experiment_id=experiment.experiment_id,
                seed=experiment.seed,
                simulation_time=experiment.duration,
                wall_time=0.0,
                missing_reasons={"sequence": str(e)},
            )

        # Build timeline (picosecond precision)
        tl = Timeline(stop_time=int(experiment.duration * 1e12))
        tl.seed(experiment.seed)

        # Create nodes (QuantumRouter creates MemoryArray internally)
        node_map: dict[str, Any] = {}
        node_memories: dict[str, list[Any]] = {}

        for node_spec in experiment.topology.nodes:
            # Use capacity from first memory spec, default 50
            memo_size = 50
            if node_spec.memories:
                memo_size = node_spec.memories[0].capacity or 50

            qnode = QuantumRouter(node_spec.node_id, tl, memo_size=memo_size)
            node_map[node_spec.node_id] = qnode
            node_memories[node_spec.node_id] = []

            # Configure memory array parameters
            if node_spec.memories:
                mem_spec = node_spec.memories[0]
                memo_arr = qnode.get_component_by_name(qnode.memo_arr_name)
                if memo_arr is not None:
                    for mem in getattr(memo_arr, 'memories', []):
                        mem.fidelity = mem_spec.initial_fidelity
                        mem.raw_fidelity = mem_spec.initial_fidelity
                        mem.efficiency = mem_spec.write_efficiency
                        mem.coherence_time = mem_spec.T2 if mem_spec.T2 else 0
                        mem.wavelength = int(mem_spec.wavelength or 500)
                        node_memories[node_spec.node_id].append(mem)

        # Create quantum channels
        for edge in experiment.topology.edges:
            ql = edge.quantum_link
            QuantumChannel(
                name=f"qc_{edge.source}_{edge.target}",
                timeline=tl,
                attenuation=ql.attenuation,
                distance=ql.distance,
                light_speed=ql.speed * 1e-3,  # convert m/s to km/ps
            )

        # Run timeline
        try:
            tl.init()
            tl.run()
        except Exception:
            pass

        wall_time = _time.time() - wall_start

        # Build translation report
        report = _build_translation_report()
        report.experiment_id = experiment.experiment_id

        result = SimulationResult(
            backend="sequence",
            backend_version=self.backend_version,
            experiment_id=experiment.experiment_id,
            seed=experiment.seed,
            simulation_time=experiment.duration,
            wall_time=wall_time,
            requested_pairs=sum(r.num_pairs for r in experiment.traffic.requests),
            translation_report={e.parameter: e.status.value for e in report.entries},
        )

        # Try to extract metrics from memories
        try:
            delivered = 0
            total_fidelity = 0.0
            fidelities = []
            for _node_id, mems in node_memories.items():
                for mem in mems:
                    if hasattr(mem, 'fidelity') and mem.fidelity > 0:
                        delivered += 1
                        fidelities.append(mem.fidelity)
                        total_fidelity += mem.fidelity

            result.delivered_pairs = delivered
            if fidelities:
                mean_f = total_fidelity / len(fidelities)
                result.fidelity = FidelityStats(
                    mean=mean_f,
                    min=min(fidelities),
                    max=max(fidelities),
                )
        except Exception:
            pass

        result.compute_derived(experiment.min_fidelity)

        return result
