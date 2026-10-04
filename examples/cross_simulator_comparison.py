"""Cross-simulator comparison example.

Run the same experiment on Reference, SimQN, and SeQUeNCe backends
and compare normalized SimulationResult schemas.
"""

from __future__ import annotations

import json

from westquant_network import (
    EdgeSpec,
    ExperimentSpec,
    NodeSpec,
    QuantumLinkSpec,
    QuantumMemorySpec,
    RequestSpec,
    TopologySpec,
    TopologyType,
    TrafficModel,
    TrafficSpec,
    compare,
)


def main() -> None:
    """Run cross-simulator comparison."""
    # Build a simple 2-node experiment
    experiment = ExperimentSpec(
        experiment_id="cross_sim_comparison",
        topology=TopologySpec(
            topology_type=TopologyType.LINE,
            nodes=[
                NodeSpec(
                    node_id="alice",
                    memories=[QuantumMemorySpec(capacity=10, T2=1.0)],
                ),
                NodeSpec(
                    node_id="bob",
                    memories=[QuantumMemorySpec(capacity=10, T2=1.0)],
                ),
            ],
            edges=[
                EdgeSpec(
                    source="alice",
                    target="bob",
                    quantum_link=QuantumLinkSpec(distance=10.0, attenuation=0.2),
                ),
            ],
        ),
        traffic=TrafficSpec(
            model=TrafficModel.SINGLE_REQUEST,
            requests=[
                RequestSpec(
                    request_id="r0",
                    source="alice",
                    destination="bob",
                    num_pairs=100,
                    min_fidelity=0.9,
                ),
            ],
        ),
        duration=10.0,
        seed=42,
    )

    # Run on all available backends
    backends = ["reference", "simqn", "sequence"]
    results = compare(experiment, backends)

    # Print comparison
    print("=" * 60)
    print("Cross-Simulator Comparison")
    print("=" * 60)
    print(f"Experiment: {experiment.experiment_id}")
    print(f"Backends: {backends}")
    print()

    for backend, result in results.items():
        print(f"--- {backend} ---")
        print(f"  Delivered: {result.delivered_pairs}")
        print(f"  Qualified: {result.qualified_pairs}")
        print(f"  Goodput: {result.goodput}")
        print(f"  Fidelity mean: {result.fidelity.mean}")
        print(f"  Wall time: {result.wall_time:.4f}s")
        if result.missing_reasons:
            print(f"  Missing: {result.missing_reasons}")
        print(f"  Translation entries: {len(result.translation_report)}")
        print()

    # Export full results
    output = {
        backend: result.model_dump()
        for backend, result in results.items()
    }
    print("Full JSON output:")
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
