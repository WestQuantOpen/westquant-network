"""WestQuant Network benchmark suite — golden experiments."""

from __future__ import annotations

from westquant_network.ir import (
    EdgeSpec,
    ExperimentSpec,
    NodeSpec,
    QuantumLinkSpec,
    QuantumMemorySpec,
    RepeaterSpec,
    RequestSpec,
    TopologySpec,
    TopologyType,
    TrafficModel,
    TrafficSpec,
)
from westquant_network.policies import PolicySet  # noqa: F401
from westquant_network.reference import simulate


def _line_topology(
    n: int, spacing_km: float = 25.0, memory_capacity: int = 10, T2: float = 1.0,  # noqa: N803
) -> TopologySpec:
    """Create a line topology with n nodes."""
    nodes = [
        NodeSpec(
            node_id=f"n{i}",
            memories=[QuantumMemorySpec(capacity=memory_capacity, T2=T2)],
            is_repeater=(0 < i < n - 1),
        )
        for i in range(n)
    ]
    edges = [
        EdgeSpec(
            source=f"n{i}",
            target=f"n{i + 1}",
            quantum_link=QuantumLinkSpec(distance=spacing_km),
        )
        for i in range(n - 1)
    ]
    return TopologySpec(
        topology_type=TopologyType.LINE,
        nodes=nodes,
        edges=edges,
    )


def b01_direct_ideal_link() -> ExperimentSpec:
    """B01: Direct ideal link — 2 nodes, no loss, no decoherence."""
    topo = TopologySpec(
        topology_type=TopologyType.LINE,
        nodes=[
            NodeSpec(node_id="n0", memories=[QuantumMemorySpec(capacity=10, T2=None)]),
            NodeSpec(node_id="n1", memories=[QuantumMemorySpec(capacity=10, T2=None)]),
        ],
        edges=[
            EdgeSpec(
                source="n0",
                target="n1",
                quantum_link=QuantumLinkSpec(distance=1.0, attenuation=0.0),
            )
        ],
    )
    return ExperimentSpec(
        experiment_id="B01_direct_ideal_link",
        topology=topo,
        traffic=TrafficSpec(
            model=TrafficModel.SINGLE_REQUEST,
            requests=[
                RequestSpec(request_id="r0", source="n0", destination="n1", num_pairs=100)
            ],
        ),
        duration=10.0,
        seed=42,
    )


def b02_lossy_direct_link() -> ExperimentSpec:
    """B02: Lossy direct link — 2 nodes, 50% loss."""

    topo = TopologySpec(
        topology_type=TopologyType.LINE,
        nodes=[
            NodeSpec(node_id="n0", memories=[QuantumMemorySpec(capacity=10, T2=None)]),
            NodeSpec(node_id="n1", memories=[QuantumMemorySpec(capacity=10, T2=None)]),
        ],
        edges=[
            EdgeSpec(
                source="n0",
                target="n1",
                quantum_link=QuantumLinkSpec(distance=50.0, attenuation=0.2),
            )
        ],
    )
    return ExperimentSpec(
        experiment_id="B02_lossy_direct_link",
        topology=topo,
        traffic=TrafficSpec(
            model=TrafficModel.SINGLE_REQUEST,
            requests=[
                RequestSpec(request_id="r0", source="n0", destination="n1", num_pairs=100)
            ],
        ),
        duration=10.0,
        seed=42,
    )


def b03_memory_decay() -> ExperimentSpec:
    """B03: Memory decay — T2 = 0.5s."""

    topo = TopologySpec(
        topology_type=TopologyType.LINE,
        nodes=[
            NodeSpec(node_id="n0", memories=[QuantumMemorySpec(capacity=10, T2=0.5)]),
            NodeSpec(node_id="n1", memories=[QuantumMemorySpec(capacity=10, T2=0.5)]),
        ],
        edges=[
            EdgeSpec(
                source="n0",
                target="n1",
                quantum_link=QuantumLinkSpec(distance=1.0, attenuation=0.0),
            )
        ],
    )
    return ExperimentSpec(
        experiment_id="B03_memory_decay",
        topology=topo,
        traffic=TrafficSpec(
            model=TrafficModel.SINGLE_REQUEST,
            requests=[
                RequestSpec(request_id="r0", source="n0", destination="n1", num_pairs=100)
            ],
        ),
        duration=10.0,
        seed=42,
    )


def b04_single_repeater() -> ExperimentSpec:
    """B04: Single repeater — A-R-B, 3 nodes."""

    topo = _line_topology(3, spacing_km=25.0, memory_capacity=10, T2=1.0)
    return ExperimentSpec(
        experiment_id="B04_single_repeater",
        topology=topo,
        repeaters=[
            RepeaterSpec(node_id="n1", swap_success_probability=0.9),
        ],
        traffic=TrafficSpec(
            model=TrafficModel.SINGLE_REQUEST,
            requests=[
                RequestSpec(request_id="r0", source="n0", destination="n2", num_pairs=100)
            ],
        ),
        duration=10.0,
        seed=42,
    )


def b05_repeater_chain(n_repeaters: int = 4) -> ExperimentSpec:
    """B05: Linear repeater chain — n repeaters between A and B."""
    n = n_repeaters + 2
    topo = _line_topology(n, spacing_km=25.0, memory_capacity=10, T2=1.0)
    repeaters = [
        RepeaterSpec(node_id=f"n{i}", swap_success_probability=0.95)
        for i in range(1, n - 1)
    ]
    return ExperimentSpec(
        experiment_id=f"B05_repeater_chain_{n_repeaters}",
        topology=topo,
        repeaters=repeaters,
        traffic=TrafficSpec(
            model=TrafficModel.SINGLE_REQUEST,
            requests=[
                RequestSpec(
                    request_id="r0",
                    source="n0",
                    destination=f"n{n - 1}",
                    num_pairs=100,
                )
            ],
        ),
        duration=10.0,
        seed=42,
    )


def b07_finite_memory(capacity: int = 4) -> ExperimentSpec:
    """B07: Finite memory — capacity constraint."""
    topo = _line_topology(3, spacing_km=25.0, memory_capacity=capacity, T2=1.0)
    return ExperimentSpec(
        experiment_id=f"B07_finite_memory_{capacity}",
        topology=topo,
        repeaters=[RepeaterSpec(node_id="n1", swap_success_probability=0.9)],
        traffic=TrafficSpec(
            model=TrafficModel.SINGLE_REQUEST,
            requests=[
                RequestSpec(request_id="r0", source="n0", destination="n2", num_pairs=100)
            ],
        ),
        duration=10.0,
        seed=42,
    )


GOLDEN_BENCHMARKS = {
    "B01": b01_direct_ideal_link,
    "B02": b02_lossy_direct_link,
    "B03": b03_memory_decay,
    "B04": b04_single_repeater,
    "B05": b05_repeater_chain,
    "B07": b07_finite_memory,
}


def run_all_benchmarks() -> dict[str, dict[str, float]]:
    """Run all golden benchmarks on the reference simulator."""
    results = {}
    for name, factory in GOLDEN_BENCHMARKS.items():
        exp = factory()
        result = simulate(exp)
        results[name] = {
            "delivered": result.delivered_pairs,
            "qualified": result.qualified_pairs,
            "goodput": result.goodput or 0.0,
            "fidelity_mean": result.fidelity.mean or 0.0,
            "wall_time": result.wall_time,
        }
    return results
