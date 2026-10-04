"""Tests for WestQuant Network."""

import pytest

from westquant_network import (
    EdgeSpec,
    ExperimentSpec,
    NodeSpec,
    PolicySet,
    QuantumLinkSpec,
    QuantumMemorySpec,
    RequestSpec,
    RoutingPolicy,
    TopologySpec,
    TopologyType,
    TrafficModel,
    TrafficSpec,
    simulate,
)
from westquant_network.adapters import BackendCapabilities
from westquant_network.backend import compare
from westquant_network.backend import simulate as simulate_backend
from westquant_network.benchmark import run_all_benchmarks
from westquant_network.policies import RoutingPolicyType
from westquant_network.validation import TranslationReport, TranslationStatus


def _make_line_experiment(n: int = 3, spacing: float = 25.0) -> ExperimentSpec:
    """Create a simple line experiment."""
    nodes = [
        NodeSpec(
            node_id=f"n{i}",
            memories=[QuantumMemorySpec(capacity=10, T2=1.0)],
            is_repeater=(0 < i < n - 1),
        )
        for i in range(n)
    ]
    edges = [
        EdgeSpec(
            source=f"n{i}",
            target=f"n{i+1}",
            quantum_link=QuantumLinkSpec(distance=spacing),
        )
        for i in range(n - 1)
    ]
    return ExperimentSpec(
        experiment_id="test",
        topology=TopologySpec(
            topology_type=TopologyType.LINE,
            nodes=nodes,
            edges=edges,
        ),
        traffic=TrafficSpec(
            model=TrafficModel.SINGLE_REQUEST,
            requests=[
                RequestSpec(
                    request_id="r0",
                    source="n0",
                    destination=f"n{n-1}",
                    num_pairs=50,
                )
            ],
        ),
        duration=10.0,
        seed=42,
    )


def test_experiment_spec_creation():
    """Test that experiment specs can be created."""
    exp = _make_line_experiment()
    assert exp.experiment_id == "test"
    assert len(exp.topology.nodes) == 3
    assert len(exp.topology.edges) == 2


def test_reference_simulator_basic():
    """Test that the reference simulator runs and produces results."""
    exp = _make_line_experiment()
    result = simulate(exp)
    assert result.backend == "reference"
    assert result.experiment_id == "test"
    assert result.seed == 42
    assert result.wall_time > 0
    assert result.simulation_time == 10.0


def test_reference_simulator_delivers_pairs():
    """Test that the reference simulator delivers pairs on ideal link."""
    exp = _make_line_experiment(2, spacing=1.0)
    exp.topology.edges[0].quantum_link.attenuation = 0.0
    result = simulate(exp)
    assert result.delivered_pairs > 0
    assert result.fidelity.mean is not None
    assert result.fidelity.mean > 0


def test_reference_simulator_loss_reduces_delivery():
    """Test that higher loss reduces delivered pairs."""
    exp_ideal = _make_line_experiment(2, spacing=1.0)
    exp_ideal.topology.edges[0].quantum_link.attenuation = 0.0
    result_ideal = simulate(exp_ideal)

    exp_lossy = _make_line_experiment(2, spacing=100.0)
    exp_lossy.topology.edges[0].quantum_link.attenuation = 0.5
    result_lossy = simulate(exp_lossy)

    assert result_ideal.delivered_pairs >= result_lossy.delivered_pairs


def test_routing_policy_shortest_hop():
    """Test shortest-hop routing."""
    exp = _make_line_experiment(3)
    exp.topology.topology_type = TopologyType.LINE
    result = simulate(exp, PolicySet(routing=RoutingPolicy(
        policy_type=RoutingPolicyType.SHORTEST_HOP
    )))
    assert result.delivered_pairs >= 0


def test_translation_report():
    """Test translation report creation."""
    report = TranslationReport(backend="reference", experiment_id="test")
    report.add("memory.T2", TranslationStatus.EXACT)
    report.add("purification", TranslationStatus.UNSUPPORTED, warning="Not implemented")
    assert report.has_warnings
    assert report.has_unsupported
    summary = report.summary()
    assert summary.get("EXACT") == 1
    assert summary.get("UNSUPPORTED") == 1


def test_backend_capabilities():
    """Test backend capability discovery."""
    caps = BackendCapabilities(backend_name="reference")
    assert caps.backend_name == "reference"
    assert caps.supports("memory.capacity") is True
    assert isinstance(caps.explain("memory.capacity"), str)


def test_golden_benchmarks():
    """Test that golden benchmarks run."""
    results = run_all_benchmarks()
    assert "B01" in results
    assert "B04" in results
    assert results["B01"]["delivered"] > 0


@pytest.mark.skipif(
    pytest.importorskip("qns", reason="SimQN not installed") is None,
    reason="SimQN not installed",
)
def test_simqn_adapter():
    """Test SimQN adapter runs and produces results."""
    pytest.importorskip("qns", reason="SimQN not installed")
    exp = _make_line_experiment(2, spacing=1.0)
    exp.topology.edges[0].quantum_link.attenuation = 0.0
    result = simulate_backend(exp, backend="simqn")
    assert result.backend == "simqn"
    assert result.experiment_id == "test"
    assert result.wall_time >= 0
    assert "memory.T2" in result.translation_report


@pytest.mark.skipif(
    pytest.importorskip("sequence", reason="SeQUeNCe not installed") is None,
    reason="SeQUeNCe not installed",
)
def test_sequence_adapter():
    """Test SeQUeNCe adapter runs and produces results."""
    pytest.importorskip("sequence", reason="SeQUeNCe not installed")
    exp = _make_line_experiment(2, spacing=1.0)
    exp.topology.edges[0].quantum_link.attenuation = 0.0
    result = simulate_backend(exp, backend="sequence")
    assert result.backend == "sequence"
    assert result.experiment_id == "test"
    assert result.wall_time >= 0
    assert "memory.T2" in result.translation_report


def test_compare_backends():
    """Test multi-backend comparison."""
    exp = _make_line_experiment(2, spacing=1.0)
    exp.topology.edges[0].quantum_link.attenuation = 0.0
    backends = ["reference"]
    try:
        import qns  # noqa: F401
        backends.append("simqn")
    except ImportError:
        pass
    try:
        import sequence  # noqa: F401
        backends.append("sequence")
    except ImportError:
        pass
    results = compare(exp, backends)
    assert "reference" in results
    assert "simqn" in results
    assert "sequence" in results
    assert results["reference"].delivered_pairs > 0


@pytest.mark.skipif(
    pytest.importorskip("qns", reason="SimQN not installed") is None,
    reason="SimQN not installed",
)
def test_simqn_capabilities():
    """Test SimQN capability discovery."""
    pytest.importorskip("qns", reason="SimQN not installed")
    from westquant_network.adapters.simqn import SimQNAdapter
    adapter = SimQNAdapter()
    caps = adapter.capabilities()
    assert caps["memory"]["capacity"] is True
    assert caps["routing"]["dijkstra"] is True
    assert "swapping" in caps


@pytest.mark.skipif(
    pytest.importorskip("sequence", reason="SeQUeNCe not installed") is None,
    reason="SeQUeNCe not installed",
)
def test_sequence_capabilities():
    """Test SeQUeNCe capability discovery."""
    pytest.importorskip("sequence", reason="SeQUeNCe not installed")
    from westquant_network.adapters.sequence import SequenceAdapter
    adapter = SequenceAdapter()
    caps = adapter.capabilities()
    assert caps["memory"]["T1"] is True
    assert caps["swapping"] is True
    assert "purification" in caps
