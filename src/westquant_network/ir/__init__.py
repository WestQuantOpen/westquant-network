"""WQIR Network representation — framework-neutral quantum network IR."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TopologyType(str, Enum):
    """Supported topology types."""

    LINE = "line"
    RING = "ring"
    STAR = "star"
    TREE = "tree"
    GRID = "grid"
    MESH = "mesh"
    ER_RANDOM = "er_random"
    BA_SCALE_FREE = "ba_scale_free"
    WAXMAN = "waxman"
    REAL_WORLD = "real_world"
    CUSTOM = "custom"


class MemoryTechnology(str, Enum):
    """Quantum memory technology families."""

    RARE_EARTH = "rare_earth"
    ATOMIC_ENSEMBLE = "atomic_ensemble"
    TRAPPED_ION = "trapped_ion"
    NEUTRAL_ATOM = "neutral_atom"
    NV_CENTER = "nv_center"
    QUANTUM_DOT = "quantum_dot"
    OPTOMECHANICAL = "optomechanical"
    GENERIC = "generic"


class DecoherenceModel(str, Enum):
    """Memory decoherence model."""

    EXPONENTIAL = "exponential"
    CUSTOM = "custom"
    NONE = "none"


class CutoffPolicy(str, Enum):
    """Policy for discarding stale entangled pairs."""

    AGE = "age"
    FIDELITY = "fidelity"
    BOTH = "both"
    NONE = "none"


class QuantumMemorySpec(BaseModel):
    """Specification for a quantum memory.

    Technology-agnostic: describes capacity, coherence, efficiency,
    latency, bandwidth, multiplexing, and decoherence model.
    """

    capacity: int = Field(ge=0, description="Number of storage modes/qubits")
    T1: float | None = Field(default=None, ge=0, description="Population lifetime (s)")
    T2: float | None = Field(default=None, ge=0, description="Coherence time (s)")
    initial_fidelity: float = Field(
        default=1.0, ge=0, le=1, description="Initial state fidelity"
    )
    write_efficiency: float = Field(
        default=1.0, ge=0, le=1, description="Write success probability"
    )
    read_efficiency: float = Field(
        default=1.0, ge=0, le=1, description="Read success probability"
    )
    write_latency: float = Field(default=0.0, ge=0, description="Write latency (s)")
    read_latency: float = Field(default=0.0, ge=0, description="Read latency (s)")
    operation_fidelity: float = Field(
        default=1.0, ge=0, le=1, description="Gate operation fidelity"
    )
    bandwidth: float | None = Field(default=None, ge=0, description="Bandwidth (Hz)")
    wavelength: float | None = Field(default=None, ge=0, description="Wavelength (nm)")
    conversion_efficiency: float = Field(
        default=1.0, ge=0, le=1, description="Quantum frequency conversion efficiency"
    )
    multiplexing_modes: int = Field(default=1, ge=1, description="Multiplexing modes")
    cutoff_time: float | None = Field(
        default=None, ge=0, description="Cutoff time for pair discarding (s)"
    )
    decoherence_model: DecoherenceModel = Field(
        default=DecoherenceModel.EXPONENTIAL,
        description="Decoherence model",
    )
    cutoff_policy: CutoffPolicy = Field(
        default=CutoffPolicy.AGE, description="Cutoff policy"
    )
    technology: MemoryTechnology = Field(
        default=MemoryTechnology.GENERIC, description="Memory technology family"
    )
    custom_parameters: dict[str, Any] = Field(
        default_factory=dict, description="Backend-specific parameters"
    )


class QuantumLinkSpec(BaseModel):
    """Specification for a quantum (photonic) link."""

    distance: float = Field(ge=0, description="Distance (km)")
    speed: float = Field(
        default=2e8, ge=0, description="Propagation speed in fiber (m/s)"
    )
    attenuation: float = Field(
        default=0.2, ge=0, description="Attenuation (dB/km)"
    )
    loss_probability: float | None = Field(
        default=None, ge=0, le=1, description="Override loss probability"
    )
    source_rate: float = Field(
        default=1e6, ge=0, description="Source generation rate (Hz)"
    )
    source_efficiency: float = Field(
        default=1.0, ge=0, le=1, description="Source efficiency"
    )
    detector_efficiency: float = Field(
        default=1.0, ge=0, le=1, description="Detector efficiency"
    )
    detector_dark_count: float = Field(
        default=0.0, ge=0, description="Detector dark count rate (Hz)"
    )
    wavelength: float = Field(default=1550, ge=0, description="Wavelength (nm)")
    channel_noise: float = Field(
        default=0.0, ge=0, le=1, description="Channel noise parameter"
    )
    classical_latency: float = Field(
        default=0.0, ge=0, description="Classical communication latency (s)"
    )
    quantum_latency: float | None = Field(
        default=None, ge=0, description="Quantum channel latency override (s)"
    )


class ClassicalLinkSpec(BaseModel):
    """Specification for a classical communication link."""

    latency: float = Field(default=0.0, ge=0, description="Latency (s)")
    bandwidth: float | None = Field(
        default=None, ge=0, description="Bandwidth (bits/s)"
    )


class NodeSpec(BaseModel):
    """A quantum network node."""

    node_id: str = Field(description="Unique node identifier")
    label: str | None = Field(default=None, description="Human-readable label")
    memories: list[QuantumMemorySpec] = Field(
        default_factory=list, description="Quantum memories at this node"
    )
    is_repeater: bool = Field(default=False, description="Whether node is a repeater")
    is_source: bool = Field(default=False, description="Whether node is a source")
    is_detector: bool = Field(default=False, description="Whether node is a detector")
    processor_latency: float = Field(
        default=0.0, ge=0, description="Classical processing latency (s)"
    )
    custom_parameters: dict[str, Any] = Field(
        default_factory=dict, description="Backend-specific parameters"
    )


class EdgeSpec(BaseModel):
    """An edge (link) between two nodes."""

    source: str = Field(description="Source node ID")
    target: str = Field(description="Target node ID")
    quantum_link: QuantumLinkSpec = Field(description="Quantum link spec")
    classical_link: ClassicalLinkSpec = Field(
        default_factory=ClassicalLinkSpec, description="Classical link spec"
    )


class TopologySpec(BaseModel):
    """Network topology specification."""

    topology_type: TopologyType = Field(description="Topology type")
    nodes: list[NodeSpec] = Field(description="Nodes in the network")
    edges: list[EdgeSpec] = Field(description="Edges (links) in the network")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Topology-specific parameters"
    )


class RepeaterSpec(BaseModel):
    """Repeater specification."""

    node_id: str = Field(description="Repeater node ID")
    swap_success_probability: float = Field(
        default=1.0, ge=0, le=1, description="BSM swap success probability"
    )
    swap_latency: float = Field(default=0.0, ge=0, description="Swap operation latency (s)")
    memories: list[QuantumMemorySpec] = Field(
        default_factory=list, description="Repeater memories"
    )


class RequestSpec(BaseModel):
    """An entanglement generation request."""

    request_id: str = Field(description="Unique request ID")
    source: str = Field(description="Source node ID")
    destination: str = Field(description="Destination node ID")
    min_fidelity: float = Field(
        default=0.9, ge=0, le=1, description="Minimum required fidelity"
    )
    deadline: float | None = Field(
        default=None, ge=0, description="Deadline (s), None = no deadline"
    )
    priority: int = Field(default=0, ge=0, description="Priority (higher = more)")
    num_pairs: int = Field(default=1, ge=1, description="Number of pairs requested")


class TrafficModel(str, Enum):
    """Traffic generation model."""

    SINGLE_REQUEST = "single_request"
    PERIODIC = "periodic"
    POISSON = "poisson"
    BURST = "burst"
    TRACE_DRIVEN = "trace_driven"


class TrafficSpec(BaseModel):
    """Traffic/workload specification."""

    model: TrafficModel = Field(description="Traffic model")
    rate: float = Field(default=1.0, ge=0, description="Request rate (Hz)")
    requests: list[RequestSpec] = Field(
        default_factory=list, description="Explicit requests"
    )
    duration: float = Field(default=10.0, ge=0, description="Simulation duration (s)")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Model-specific parameters"
    )


class ExperimentSpec(BaseModel):
    """Complete experiment specification — the WestQuant Network IR.

    This is the canonical, simulator-independent description of a
    quantum-network experiment. It is translated by each adapter
    into backend-native configuration.
    """

    experiment_id: str = Field(description="Unique experiment identifier")
    topology: TopologySpec = Field(description="Network topology")
    repeaters: list[RepeaterSpec] = Field(
        default_factory=list, description="Repeater specifications"
    )
    traffic: TrafficSpec = Field(default_factory=TrafficSpec, description="Traffic")
    seed: int = Field(default=42, description="Random seed")
    duration: float = Field(default=10.0, ge=0, description="Simulation duration (s)")
    objective: str = Field(
        default="qualified_goodput", description="Optimization objective"
    )
    min_fidelity: float = Field(
        default=0.9, ge=0, le=1, description="Global minimum fidelity threshold"
    )
    backend: str = Field(default="reference", description="Backend to use")
    backend_params: dict[str, Any] = Field(
        default_factory=dict, description="Backend-specific parameters"
    )
    custom: dict[str, Any] = Field(
        default_factory=dict, description="Custom experiment parameters"
    )
