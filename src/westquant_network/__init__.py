"""WestQuant Network — simulator-independent quantum network framework."""

from westquant_network.backend import compare
from westquant_network.backend import simulate as simulate_backend
from westquant_network.ir import (
    ClassicalLinkSpec,
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
from westquant_network.metrics import SimulationResult
from westquant_network.policies import (
    AdmissionPolicy,
    MemoryPolicy,
    PolicySet,
    PurificationPolicy,
    RoutingPolicy,
    SwapPolicy,
)
from westquant_network.reference import simulate

__version__ = "0.1.0a1"

__all__ = [
    "ExperimentSpec",
    "TopologySpec",
    "TopologyType",
    "NodeSpec",
    "QuantumMemorySpec",
    "QuantumLinkSpec",
    "ClassicalLinkSpec",
    "EdgeSpec",
    "RepeaterSpec",
    "RequestSpec",
    "TrafficSpec",
    "TrafficModel",
    "PolicySet",
    "RoutingPolicy",
    "MemoryPolicy",
    "SwapPolicy",
    "PurificationPolicy",
    "AdmissionPolicy",
    "SimulationResult",
    "simulate",
    "simulate_backend",
    "compare",
]
